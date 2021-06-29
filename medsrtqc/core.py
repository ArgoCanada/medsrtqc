
from typing import Iterable, Dict, Any, Tuple
from numpy.ma import MaskedArray
from numpy.ma.core import make_mask


class Trace:
    """
    Trace objects are a simple representation of a value measured along
    a pressure axis. Both `pres` and `value` should be one-dimensional
    numpy MaskedArray objects.
    """

    def __init__(self, pres: MaskedArray, value: MaskedArray,
                 value_qc=None, adjusted=None, adjusted_error=None,
                 adjusted_qc=None) -> None:
        self.pres = pres
        self.value = value
        self.value_qc = value_qc
        self.adjusted = adjusted
        self.adjusted_error = adjusted_error
        self.adjusted_qc = adjusted_qc


class Profile:
    """
    An abstract base class for a Profile. A Profile is 
    dict-like with each element as a Trace, allowing
    profile objects to accomodate all parameters collected
    during an ascent regardless of sampling frequency.
    """

    def keys(self) -> Iterable[str]:  # pragma: no cover
        raise NotImplementedError()

    def __getitem__(self, k) -> Trace:  # pragma: no cover
        raise NotImplementedError()

    def meta(self) -> Dict[str, Trace]:  # pragma: no cover
        raise NotImplementedError()

    def __in__(self, k) -> bool:
        return k in self.keys()

    def items(self) -> Iterable[Tuple[str, Trace]]:
        for k in self.keys():
            yield k, self[k]


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
