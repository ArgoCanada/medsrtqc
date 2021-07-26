
"""
Writing portable QC operations shouldn't depend on the underlying
data storage mechanism, which might be a database, NetCDF file,
or binary export. The classes in the ``core`` module are designed to
provide a view of Argo data that can be passed to or returned from
QC operations. Here Argo data are modeled as :class:`Trace` objects
that are contained by :class:`Profile` objects.
"""

from typing import Iterable, Tuple
from copy import deepcopy
from numpy.ma import MaskedArray
from numpy import zeros, float32, dtype


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
    :param qc: The parameter QC value.
    :param adjusted: The adjusted parameter value.
    :param adjusted_error: The error estimate for the adjusted value.
    :param adjusted_qc: The adjusted parameter QC value
    :param pres: The pressure measurement (in dbar) corresponding to
        the ``value``.
    :param mtime: The measurement time
    """

    def __init__(self, value: MaskedArray,
                 qc=None, adjusted=None, adjusted_error=None,
                 adjusted_qc=None, pres=None, mtime=None) -> None:
        value = MaskedArray(value)
        self._shape = value.shape
        self._n = len(value)

        self.value = self._sanitize(value, float32, 'value')
        self.qc = self._sanitize(qc, dtype('S1'), 'qc')
        self.adjusted = self._sanitize(adjusted, float32, 'adjusted')
        self.adjusted_error = self._sanitize(adjusted_error, float32, 'adjusted_error')
        self.adjusted_qc = self._sanitize(adjusted_qc, dtype('S1'), 'adjusted_qc')
        self.pres = self._sanitize(pres, float32, 'pres')
        self.mtime = self._sanitize(mtime, float32, 'mtime')

    def _sanitize(self, v, dtype_if_none, attr):
        if v is None:
            v = zeros(self._shape, dtype=dtype_if_none)
            return MaskedArray(v, mask=True)
        else:
            v = MaskedArray(v).astype(dtype_if_none)
            if len(v) != self._n:
                gen_msg = f'len() of Trace attributes must match len(value) ({self._n}).'
                spec_msg = f"Attribute '{attr}' has shape {repr(v.shape)}"
                raise ValueError(gen_msg + '\n' + spec_msg)
            return v

    def __len__(self):
        return self._n

    def __repr__(self) -> str:
        summaries = []
        for attr in ['value', 'qc', 'adjusted', 'adjusted_error', 'pres', 'mtime']:
            v = getattr(self, attr)

            if self._n == 0:
                summaries.append(f'{attr}=[]')
            elif self._n <= 6:
                summary = ', '.join(repr(item) for item in v)
                summaries.append(f'{attr}=[{summary}]')
            else:
                head_summary = ', '.join(repr(item) for item in v[:3])
                tail_summary = ', '.join(repr(item) for item in v[-3:])
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
    a ``dict`` of :class:`Trace` objects.
    """

    def __init__(self, data=None, meta=None):
        self.__data = dict(data) if data is not None else None
        self.__meta = dict(meta) if meta is not None else None

    def keys(self) -> Iterable[str]:
        if self.__data is None:
            raise NotImplementedError()
        return tuple(self.__data.keys())

    def __getitem__(self, k) -> Trace:
        if self.__data is None:
            raise NotImplementedError()
        return deepcopy(self.__data[k])

    def __setitem__(self, k, v):
        if self.__data is None:
            raise NotImplementedError()
        self.__data[k] = v

    def __iter__(self) -> Iterable[str]:
        return iter(self.keys())

    def __contains__(self, k) -> bool:
        return k in self.keys()

    def items(self) -> Iterable[Tuple[str, Trace]]:
        for k in self.keys():
            yield k, self[k]

    def meta_keys(self):
        if self.__meta is None:
            raise NotImplementedError()
        return tuple(self.__meta.keys())

    def meta(self, k):
        if self.__meta is None:
            raise NotImplementedError()
        return self.__meta[k]

    def set_meta(self, k, v):
        if self.__meta is None:
            raise NotImplementedError()
        self.__meta[k] = v
