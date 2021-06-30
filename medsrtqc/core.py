
from typing import Iterable, Dict, Any, Tuple
from numpy.ma import MaskedArray


class Trace:
    """
    Trace objects are a simple representation of a value series.
    All attributes of a :class:`Trace` are ``numpy``
    ``MaskedArray`` objects like those that might be read from an Argo
    NetCDF file. The ``value`` attributes is guaranteed
    to not be ``None``; other attributes are optional and should be
    checked in code that uses these objects. QC operations can be
    written as functions of :class:`Trace` objects and the result of
    QC operations is often a modified :class:`Trace`.

    :param value: The parameter value reading
    :param value_qc: The parameter QC value
    :param adjusted: The adjusted parameter value
    :param adjusted_error: The error estimate for the adjusted value
    :param adjusted_qc: The adjusted parameter QC value
    :param id: An identifier that can be used between :class:`Trace`
        objects to match levels. It is helpful if these values are
        monotonic (e.g., datetime) but callers should check this
        assumption (e.g., when using pressure).
    """

    def __init__(self, value: MaskedArray,
                 value_qc=None, adjusted=None, adjusted_error=None,
                 adjusted_qc=None, id=None) -> None:
        self.value = value
        self.value_qc = value_qc
        self.adjusted = adjusted
        self.adjusted_error = adjusted_error
        self.adjusted_qc = adjusted_qc
        self.id = id


class Profile:
    """
    An abstract base class for the concept of a "Profile".
    Unlike a "Profile" in an Argo NetCDF file, these objects should contain
    all parameters measured during an ascent (or some other event
    that can be QCed). The interface is dict-like with elements as
    :class:`Trace` objects that can be extracted by name or iterated
    over using :meth:`keys` or :meth:`items`.
    """

    def keys(self) -> Iterable[str]:  # pragma: no cover
        raise NotImplementedError()

    def __getitem__(self, k) -> Trace:  # pragma: no cover
        raise NotImplementedError()
    
    def __iter__(self) -> Iterable[str]:
        return iter(self.keys())

    def __in__(self, k) -> bool:
        return k in self.keys()

    def items(self) -> Iterable[Tuple[str, Trace]]:
        for k in self.keys():
            yield k, self[k]


class ProfileList:  # pragma: no cover
    """
    An abstract base class for a collection of Profile objects
    measured in the same location but not necessarily at the same
    pressure levels. These objects are list-like with each member
    as a :class:`Profile` implementation.
    """

    def __len__(self):
        raise NotImplementedError()

    def __getitem__(self, k) -> Profile:
        raise NotImplementedError()

    def __iter__(self) -> Iterable[Profile]:
        raise NotImplementedError()
