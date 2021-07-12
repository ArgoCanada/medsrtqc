
from typing import Iterable
from copy import deepcopy

import numpy as np
from numpy.ma import MaskedArray
from numpy.ma.core import zeros

from ..core import Trace, Profile


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
            raise ValueError("Can't update Trace.value in a VMSProfile")
        if not np.all(v.pres == current_value.pres):
            raise ValueError("Can't update Trace.pres in a VMSProfile")
        if not np.all(v.adjusted.mask):
            raise ValueError("Can't update Trace.adjusted in a VMSProfile")
        if not np.all(v.adjusted_qc.mask):
            raise ValueError("Can't update Trace.adjusted_qc in a VMSProfile")
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
                    if not np.any(pres_match):
                        continue
                    m['DP_FLAG'] = bytes(v.qc[pres_match][0])

        else:
            # the data might be split into segments so we have to keep track of
            # the index within the trace separately
            trace_i = 0
            for pr_profile in data_copy['PR_PROFILE']:
                if pr_profile['FXD']['PROF_TYPE'] == k:
                    for m in pr_profile['PROF']:
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
