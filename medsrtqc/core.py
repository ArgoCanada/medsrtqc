
"""
Writing portable QC operations shouldn't depend on the underlying
data storage mechanism, which might be a database, NetCDF file,
or binary export. The classes in the ``core`` module are designed to
provide a view of Argo data that can be passed to or returned from
QC operations. Here Argo data are modeled as a three-level heiarchy
where :class:`Trace` objects are contained by :class:`Profile` objects
which are in turn contained by :class:`ProfileList` objects.
"""

from typing import Iterable, Tuple
from numpy.ma import MaskedArray
from numpy import nditer, nan, zeros, float32, dtype


class Trace:
    """
    Trace objects are a simple representation of a value series.
    All attributes of a :class:`Trace` are ``numpy``
    ``MaskedArray`` objects like those that might be read from an Argo
    NetCDF file. The ``value`` attribute is guaranteed
    to not be ``None``; other attributes are optional and should be
    checked in code that uses these objects. QC operations can be
    written as functions of :class:`Trace` objects and the result of
    QC operations is often a modified :class:`Trace`.

    :param value: The parameter value. This should be the same units
        as would be written to the Argo NetCDF file.
    :param value_qc: The parameter QC value.
    :param adjusted: The adjusted parameter value.
    :param adjusted_error: The error estimate for the adjusted value.
    :param adjusted_qc: The adjusted parameter QC value
    :param pres: The pressure measurement (in dbar) corresponding to
        the ``value``.
    :param mtime: The measurement time
    """

    def __init__(self, value: MaskedArray,
                 value_qc=None, adjusted=None, adjusted_error=None,
                 adjusted_qc=None, pres=None, mtime=None) -> None:
        self.value = MaskedArray(value)
        if len(self.value.shape) != 1:
                raise ValueError('All Trace attributes must be 1d arrays')
        self._n = self.value.shape[0]

        self.value_qc = self._sanitize(value_qc, dtype('S1'))
        self.adjusted = self._sanitize(adjusted, float32)
        self.adjusted_error = self._sanitize(adjusted_error, float32)
        self.adjusted_qc = self._sanitize(adjusted_qc, dtype('S1'))
        self.pres = self._sanitize(pres, float32)
        self.mtime = self._sanitize(mtime, float32)
    
    def _sanitize(self, v, dtype_if_none):
        if v is None:
            v = zeros((self._n, ), dtype=dtype_if_none)
            return MaskedArray(v, mask=True)
        else:
            v = MaskedArray(v)
            if len(v.shape) != 1:
                raise ValueError('All Trace attributes must be 1d arrays')
            return v

    def __len__(self):
        return self._n
    
    def __repr__(self) -> str:
        summaries = []
        for attr in ['value', 'value_qc', 'adjusted', 'adjusted_error', 'pres', 'mtime']:
            v = getattr(self, attr)
            if v.dtype.kind != 'S':
                v = v.copy()
                v[v.mask] = nan

            if self._n == 0:
                summaries.append(f'{attr}=[]')
            elif self._n <= 6:
                summary = repr(list(nditer(v)))
                summaries.append(f'{attr}={summary}')
            else:
                head_summary = ', '.join(str(item) for item in nditer(v[:3]))
                tail_summary = ', '.join(str(item) for item in nditer(v[-3:]))
                n_miss = self._n - 6
                summary = f"{attr}=[{head_summary}, [{n_miss} values], {tail_summary}]"
                summaries.append(summary)
        
        all_summaries = ',\n    '.join(summaries)
        return f"Trace(\n    {all_summaries}\n)"


class Profile:
    """
    A base class for the concept of a "Profile".
    Unlike a "Profile" in an Argo NetCDF file, these objects should contain
    all parameters measured during an ascent (or some other event
    that can be QCed). The interface is dict-like with elements as
    :class:`Trace` objects that can be extracted by name or iterated
    over using :meth:`keys` or :meth:`items`. The base class can wrap
    an immutable ``dict`` of :class:`Trace` objects.
    """

    def __init__(self, data=None):
        self.__data = data

    def keys(self) -> Iterable[str]:
        if self.__data is None:
            raise NotImplementedError()
        return self.__data.keys()

    def __getitem__(self, k) -> Trace:
        if self.__data is None:
            raise NotImplementedError()
        return self.__data[k]
    
    def __iter__(self) -> Iterable[str]:
        return iter(self.keys())

    def __in__(self, k) -> bool:
        return k in self.keys()

    def items(self) -> Iterable[Tuple[str, Trace]]:
        for k in self.keys():
            yield k, self[k]


class ProfileList:
    """
    An base class for a collection of Profile objects
    measured in the same location but not necessarily at the same
    pressure levels. These objects are list-like with each member
    as a :class:`Profile` implementation. The base class can wrap
    an immutable ``list()`` of :class:`Profile` objects.
    """

    def __init__(self, data=None):
        self.__data = data

    def __len__(self):
        if self.__data is None:
            raise NotImplementedError()
        return len(self.__data)

    def __getitem__(self, k) -> Profile:
        if self.__data is None:
            raise NotImplementedError()
        return self.__data[k]

    def __iter__(self) -> Iterable[Profile]:
        for i in range(len(self)):
            yield self[i]
