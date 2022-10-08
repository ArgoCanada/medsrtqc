
from warnings import warn
from typing import Iterable
from copy import deepcopy

import numpy as np
from numpy.ma import MaskedArray
from numpy.ma.core import zeros

from medsrtqc.qc.history import QCx
from medsrtqc.core import Trace, Profile


class VMSProfile(Profile):
    """
    An implementation of the :class:`core.Profile` type
    backed by data read from the MEDS internal VMS data
    structure. These objects are usually created by
    :func:`read_vms_profiles`.
    """

    def __init__(self, data) -> None:
        super().__init__()
        # copy data to avoid side effects to or from the caller
        self._data = deepcopy(data)

        # do some pre-processing to make fetching data easier
        self._by_param = None
        self._update_by_param_from_data()

    def prepare(self, tests=[None]):
        # this function so that read_vms_profiles() does not add information
        # but also means it will need to be called before performing QC
        data = self._data
        # save the wmo and cycle
        self.wmo = int(data['PR_STN']['FXD']['CR_NUMBER'].replace('Q',''))
        for d in data['PR_STN']['SURFACE']:
            if d['PCODE'] == 'PFN$':
                self.cycle_number = int(d['PARM'])
                break
        
        if 'FLU1' in self.keys() and 'FLUA' not in self.keys():
            self.add_new_pr_profile('FLU1', 'FLUA')

        # don't add QCP/QCF if we are not going to perform any tests
        if len(tests) > 0:
            self.add_qcp_qcf()
            self.qc_tests = QCx.qc_tests(self.get_surf_code('QCP$'), self.get_surf_code('QCF$'))

    def _update_by_param_from_data(self):
        pr_stn_prof = deepcopy(self._data['PR_STN']['PROF'])

        # the PR_PROFILE structs can be broken into
        # segments so we need to be able to map those back to
        # the profile indices here. Also create the list elements
        # that will contain these objects so that everything is in
        # one list of length number_of_profiles
        pr_stn_prof_indices = []
        for i, prof in enumerate(pr_stn_prof):
            prof['_pr_profile_fxd'] = []
            prof['_pr_profile_prof'] = []
            for j in range(prof['NO_SEG']):
                pr_stn_prof_indices.append(i)

        pr_profiles = deepcopy(self._data['PR_PROFILE'])
        for pr_stn_i, pr_profile in zip(pr_stn_prof_indices, pr_profiles):
            pr_stn_prof[pr_stn_i]['_pr_profile_fxd'].append(pr_profile['FXD'])
            for pr_profile_prof in pr_profile['PROF']:
                pr_stn_prof[pr_stn_i]['_pr_profile_prof'].append(pr_profile_prof)

        param_names = [item['PROF_TYPE'] for item in pr_stn_prof]
        by_param = {}
        for param_name, param_data in zip(param_names, pr_stn_prof):
            by_param[param_name] = param_data

        self._by_param = by_param

    def keys(self) -> Iterable[str]:
        keys = tuple(self._by_param.keys())
        return ('PRES', ) + keys if 'TEMP' in keys else keys

    def __getitem__(self, k) -> Trace:
        # Special case 'PRES' since these qc values are copied with
        # for each parameter. Use the 'TEMP' trace for this.
        if k == 'PRES':
            meas = self._by_param['TEMP']['_pr_profile_prof']
        else:
            meas = self._by_param[k]['_pr_profile_prof']

        pres = MaskedArray(zeros(len(meas)))
        value = MaskedArray(zeros(len(meas)))
        qc = MaskedArray(zeros(len(meas)))

        if k == 'PRES':
            for i, m in enumerate(meas):
                pres[i] = m['DEPTH_PRESS']
                value[i] = m['DEPTH_PRESS']
                qc[i] = m['DP_FLAG']
        else:
            for i, m in enumerate(meas):
                pres[i] = m['DEPTH_PRESS']
                value[i] = m['PARM']
                qc[i] = m['Q_PARM']

        return Trace(value, qc=qc, pres=pres)

    def __setitem__(self, k, v):
        # check dimensions against current
        current_value = self[k]
        if len(v) != len(current_value):
            msg = f"Expected trace for '{k}' with size {len(current_value)} but got {len(v)}"
            raise ValueError(msg)

        # for now we can only update the 'qc' attribute
        # make sure this is the case or else some updates are going
        # to get lost
        if not np.all(v.value == current_value.value):
            warn("Trace.value was updated in a VMSProfile, please ensure this was intended!")
        if not np.all(v.adjusted.mask):
            warn("Trace.adjusted was updated, to update adjusted variable, ensure it is manually assigned")
        if not np.all(v.adjusted_qc.mask):
            warn("Trace.adjusted_qc was updated, to update adjusted variable, ensure it is manually assigned")
        if not np.all(v.pres == current_value.pres):
            raise ValueError("Updating Trace.pres in a VMSProfile is not permitted")
        if not np.all(v.mtime.mask):
            raise ValueError("Can't update Trace.mtime in a VMSProfile")

        # Strategy for update is to copy all the data while updating it
        # to avoid a partial update if something goes wrong in the process.
        # I don't think speed will ever be an issue here but if so it is possible
        # to reduce the amount of copying.
        data_copy = deepcopy(self._data)

        # PRES is special because it isn't stored explicitly
        # strategy is to check exact values and update the flag
        # for that
        if k == 'PRES':
            for pr_profile in data_copy['PR_PROFILE']:
                for m in pr_profile['PROF']:
                    pres_match = v.value == m['DEPTH_PRESS']
                    if not np.any(pres_match): # pragma: no cover
                        continue
                    m['DP_FLAG'] = bytes(v.qc[pres_match][0])
        else:
            # the data might be split into segments so we have to keep track of
            # the index within the trace separately
            trace_i = 0
            for pr_profile in data_copy['PR_PROFILE']:
                if pr_profile['FXD']['PROF_TYPE'] == k:
                    for m in pr_profile['PROF']:
                        m['PARM'] = v.value[trace_i]
                        m['Q_PARM'] = bytes(v.qc[trace_i])
                        trace_i += 1

            # bookkeeping in case the check above didn't catch this
            if trace_i != len(v):  # pragma: no cover
                msg = f"Wrong number of values in trace ({trace_i}/{len(v)}) whilst updating '{k}'"
                raise ValueError(msg)

        # everything worked, so update the underlying data
        self._data = data_copy
        # ...and recalculate the _by_param attribute
        self._update_by_param_from_data()

    def add_new_pr_profile(self, k, nk):
        """
        Add a new variable to Profile. Data is stored in Profile._data['PR_PROFILE']
        """

        data_copy = deepcopy(self._data)

        adjusted_trace = None
        i = 0
        for pr_profile in self._data['PR_PROFILE']:
            i += 1
            # iterate MKEY if it comes after FLUA insertion
            if adjusted_trace is not None:
                new_mkey = str(int(pr_profile['FXD']['MKEY'])+1).rjust(8, '0')
                pr_profile['FXD']['MKEY'] = new_mkey
                data_copy['PR_PROFILE'][i] = pr_profile
            # add the new variable
            if pr_profile['FXD']['PROF_TYPE'] == k:
                adjusted_trace = deepcopy(pr_profile)
                adjusted_trace['FXD']['PROF_TYPE'] = nk
                new_mkey = str(int(pr_profile['FXD']['MKEY'])+1).rjust(8, '0')
                adjusted_trace['FXD']['MKEY'] = new_mkey
                data_copy['PR_PROFILE'].insert(i, adjusted_trace)
        
        if not adjusted_trace: #pragma: no cover
            raise ValueError(f"No such trace for f{k}")

        adjusted_stn = None
        i = 0
        for prof in self._data['PR_STN']['PROF']:
            i += 1
            if prof['PROF_TYPE'] == k:
                adjusted_stn = deepcopy(prof)
                adjusted_stn['PROF_TYPE'] = nk
                data_copy['PR_STN']['PROF'].insert(i, adjusted_stn)

        if not adjusted_stn: # pragma: no cover
            raise ValueError(f"No such PR_STN_PROF for f{k}")

        data_copy['PR_STN']['FXD']['NO_PROF'] = len(data_copy['PR_STN']['PROF'])

        # everything worked, so update the underlying data
        self._data = data_copy
        # ...and recalculate the _by_param attribute
        self._update_by_param_from_data()
    
    def add_qcp_qcf(self):
        data_copy = deepcopy(self._data)

        current_vars = [d['PCODE'] for d in data_copy['PR_STN']['SURF_CODES']]
        for v in ['QCP$', 'QCF$']:
            if v not in current_vars:
                data_copy['PR_STN']['SURF_CODES'].append(QCx.blank(v))
        
        data_copy['PR_STN']['FXD']['SPARMS'] = len(data_copy['PR_STN']['SURF_CODES'])
        
        # everything worked, so update the underlying data
        self._data = data_copy
        # ...and recalculate the _by_param attribute
        self._update_by_param_from_data()
    
    def get_surf_code(self, v):

        for d in self._data['PR_STN']['SURF_CODES']:
            if d['PCODE'] == v:
                return d['CPARM']

    def update_qcx(self):

        if not hasattr(self, 'qc_tests'):
            raise LookupError('Profile has no attribute qc_tests, call VMSProfile().prepare() to add it')
        
        data_copy = deepcopy(self._data)
        for d in data_copy['PR_STN']['SURF_CODES']:
            if d['PCODE'] == 'QCP$':
                d['CPARM'] = QCx.array_to_hex(self.qc_tests[0,:])
            elif d['PCODE'] == 'QCF$':
                d['CPARM'] = QCx.array_to_hex(self.qc_tests[1,:])
        
        # update the underlying data
        self._data = data_copy
        # ...and recalculate the _by_param attribute
        self._update_by_param_from_data()
