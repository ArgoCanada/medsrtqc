
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
from copy import deepcopy
import sys
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
        value = MaskedArray(value)
        self._shape = value.shape
        self._n = len(value)

        self.value = self._sanitize(value, float32, 'value')
        self.value_qc = self._sanitize(value_qc, dtype('S1'), 'value_qc')
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
        for attr in ['value', 'value_qc', 'adjusted', 'adjusted_error', 'pres', 'mtime']:
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

    def __init__(self, data=None):
        self.__data = dict(data) if data is not None else None

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


class ProfileList:
    """
    An base class for a collection of Profile objects.
    These objects are list-like with each member
    as a :class:`Profile` implementation. The base class wraps
    a ``list()`` of :class:`Profile` objects.
    """

    def __init__(self, data=None):
        self.__data = list(data) if data is not None else data

    def __len__(self):
        if self.__data is None:
            raise NotImplementedError()
        return len(self.__data)

    def __getitem__(self, k) -> Profile:
        if self.__data is None:
            raise NotImplementedError()
        return deepcopy(self.__data[k])

    def __setitem__(self, k, v):
        if self.__data is None:
            raise NotImplementedError()
        self.__data[k] = v

    def __iter__(self) -> Iterable[Profile]:
        for i in range(len(self)):
            yield self[i]


class QCOperationError(Exception):
    """
    An ``Exception`` subclass with attributes ``profile``, ``trace``,
    and ``trace_key``. These errors give an opportunity for inspection
    on debugging and potentially more informative printing because
    they contain some context.
    """

    def __init__(self, *args, profile=None, trace_key=None, trace=None, **kwargs):
        """
        :param profile: The :class:`Profile` associated with this error
        :param trace_key: The key associated with this error
        :param trace: The :class:`Trace` associated with this error
        :param args: Passed to ``super()``
        :param kwargs: Passed to ``super()``
        """
        super().__init__(*args, **kwargs)
        self.profile = profile
        self.trace = trace
        self.trace_key = trace_key


class QCOperationApplier:
    """
    QC operations may be run in many different contexts. The obvious context
    is to apply the result of the operation to the underlying
    :class:`Profile` (the default), but this class is used to give
    flexibility should users wish to do something else (e.g., print what
    actions would be taken without actually applying them) or require
    specialized actions to perform data updates that are impossible or
    inconvenient to implement in the :class:`Profile` subclass.
    """

    def update_trace(self, profile, k, trace):
        """
        Updates a given :class:`Trace` for a :class:`Profile`.
        The default method runs ``profile[k] = trace``.
        """
        profile[k] = trace

    def log(self, profile, message):
        """
        Print a log message for a given :class:`Profile`.
        The default method prints the message to ``sys.stderr``.
        """
        print(f"[{repr(profile)}] {message}", file=sys.stderr)

    def pyplot(self, profile):
        """
        Get a version of matplotlib.pyplot used for use in a ``with:``
        statement. The default method returns a context manager that
        wraps a dummy version of the module that does nothing.

        >>> from medsrtqc.core import Profile, Trace, QCOperationApplier
        >>> applier = QCOperationApplier()
        >>> profile = Profile({'param': Trace([1, 2])})
        >>> with applier.pyplot(profile) as plt:
        ...     plt.plot(profile['param'].value)
        """

        class DummyPyPlot:

            def plot(self, *args, **kwargs):
                return self

            def scatter(self, *args, **kwargs):
                return self

            def errorbar(self, *args, **kwargs):
                return self

            def subplots(self, *args, **kwargs):
                return self, (self, )

            def subplot(self, *args, **kwargs):
                return self

            def __enter__(self):
                return self

            def __exit__(self, value, *execinfo):
                return value is AttributeError

        return DummyPyPlot()


class QCOperation:
    """
    A QC operation here is instantiated with a target
    :class:`Profile` and the previous :class:`Profile` as these
    are needed to implement many of the tests. QC operations
    should implement the ``run()`` method and use the built-in
    methods to do any data updates.
    """

    def __init__(self, profile, previous_profile=None, applier=None):
        """
        :param profile: The target :class:`Profile`.
        :param profile: The previous :class:`Profile` from this float
        :param applier: The :class:`QCOperationApplier` instance used
            to perform update operations on ``profile``.
        """
        if applier is None:
            self.applier = QCOperationApplier()
        else:
            self.applier = applier

        self.profile = profile
        self.previous_profile = previous_profile

    def update_trace(self, k, trace):
        """Convenience wrapper for :func:`QCOperationApplier.update_trace`"""
        self.applier.update_trace(self.profile, k, trace)

    def log(self, message):
        """Convenience wrapper for :func:`QCOperationApplier.log`"""
        self.applier.log(self.profile, message)

    def pyplot(self):
        """Convenience wrapper for :func:`QCOperationApplier.pyplot`"""
        return self.applier.pyplot(self.profile)

    def run(self):
        """Run the test. This method must be implemented by test subclasses."""
        raise NotImplementedError()
