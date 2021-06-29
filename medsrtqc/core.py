
from typing import Iterable, Dict, Any, Tuple
from numpy.ma import MaskedArray


class Profile:  # pragma: no cover
    """
    An abstract base class for a Profile. An Argo
    profile NetCDF file is composed of one or more Profiles,
    described along the N_PROF dimension.
    For floats with sensors that sample at differing rates
    there will be more than one Profile for each cycle. These
    objects are dict-like where variables are accessed via [].
    Metadata variables are available via .meta() and are a
    dictionary of masked arrays of length 1 to facilitate encoding
    these values along the N_PROF NetCDF dimension.
    """

    def keys(self) -> Iterable[str]:
        raise NotImplementedError()

    def __getitem__(self, k) -> MaskedArray:
        raise NotImplementedError()

    def meta(self) -> Dict[str, MaskedArray]:
        raise NotImplementedError()

    def __in__(self, k) -> bool:
        return k in self.keys()

    def items(self) -> Iterable[Tuple[str, MaskedArray]]:
        for k in self.keys():
            yield self[k]


class ProfileList:  # pragma: no cover
    """
    An abstract base class for a collection of Profile objects
    measured in the same location but not necessarily at the same
    pressure levels. These objects are list-like.
    """

    def __len__(self):
        raise NotImplementedError()

    def __getitem__(self, k) -> Profile:
        raise NotImplementedError()

    def __iter__(self) -> Iterable[Profile]:
        raise NotImplementedError()

    def meta(self) -> Dict[str, Any]:
        raise NotImplementedError()
