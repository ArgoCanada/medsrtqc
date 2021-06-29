
from typing import Dict, Iterable
from numpy.ma import ma
from ..core import Profile, ProfileList


class VMSProfile(Profile):
    """
    An implementation of the Profile type backed by data read from
    the MEDS internal VMS data structure.
    """

    def __init__(self, data) -> None:
        self._data = data

    def levels(self) -> Dict[str, ma]:
        return super().levels()

    def prof(self) -> Dict[str, ma]:
        return super().prof()


class VMSProfileList(ProfileList):
    """
    An implementation of the ProfileList type backed by data read from
    the MEDS internal VMS data structure.
    """

    def __init__(self, data=None) -> None:
        if data is None:
            data = []
        self._data = data

    def __len__(self):
        return len(self._data)

    def __getitem__(self, k) -> Profile:
        return VMSProfile(self._data[k])

    def __iter__(self) -> Iterable[Profile]:
        for item in self._data:
            yield VMSProfile(item)

    def meta(self):
        return {}
