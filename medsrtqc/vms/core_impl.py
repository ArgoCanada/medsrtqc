
from typing import Iterable
from copy import deepcopy
from numpy.ma import MaskedArray
from numpy.ma.core import zeros
from ..core import Trace, Profile, ProfileList


class VMSProfile(Profile):
    """
    An implementation of the :class:`core.Profile` type
    backed by data read from the MEDS internal VMS data
    structure. These objects are always created from a
    :class:`VMSProfileList`.
    """

    def __init__(self, data) -> None:
        # copy data to avoid side effects to or from the caller
        self._data = deepcopy(data)

        # do some pre-processing to make implementing these methods easier
        self._by_param = self._param_data_from_input(self._data)

    def _param_data_from_input(self, data):
        pr_stn_prof = deepcopy(data['PR_STN']['PROF'])

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

        pr_profiles = deepcopy(data['PR_PROFILE'])
        for pr_stn_i, pr_profile in zip(pr_stn_prof_indices, pr_profiles):
            pr_stn_prof[pr_stn_i]['_pr_profile_fxd'].append(pr_profile['FXD'])
            for pr_profile_prof in pr_profile['PROF']:
                pr_stn_prof[pr_stn_i]['_pr_profile_prof'].append(pr_profile_prof)

        param_names = [item['PROF_TYPE'] for item in pr_stn_prof]
        by_param = {}
        for param_name, param_data in zip(param_names, pr_stn_prof):
            by_param[param_name] = param_data

        return by_param

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


class VMSProfileList(ProfileList):
    """
    An implementation of the ProfileList type backed by data read from
    the MEDS internal VMS data structure. This is the object
    created by :func:`read_vms_profiles` and is a container for
    :class:`VMSProfile` objects.
    """

    def __init__(self, data) -> None:
        self._data = deepcopy(data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, k) -> Profile:
        return VMSProfile(self._data[k])

    def __iter__(self) -> Iterable[Profile]:
        for item in self._data:
            yield VMSProfile(item)
