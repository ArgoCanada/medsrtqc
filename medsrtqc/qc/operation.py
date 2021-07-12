
"""
:class:`QCOperation` objects build on the :class:`Profile` and :class:`Trace`,
updating the :class:`Profile` and/or performing operations with side
effects like creating a plot or logging information to stderr. The
:class:`QCOperationContext` class provides methods for common actions
to minimize the number of custom :class:`QCOperation` classes needed
to implement a production QC workflow.
"""

import sys

class QCOperationError(Exception):
    """
    An ``Exception`` subclass with attributes ``profile``, ``trace``,
    and ``trace_key``. These errors give an opportunity for inspection
    on debugging and potentially more informative printing because
    they contain some context.
    """

    def __init__(self, *args, profile=None, **kwargs):
        """
        :param profile: The :class:`Profile` associated with this error
        :param args: Passed to ``super()``
        :param kwargs: Passed to ``super()``
        """
        super().__init__(*args, **kwargs)
        self.profile = profile


class QCOperationContext:
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

    def error(self, profile, message):
        """
        Shortcut for ``raise QCOperationError()``
        """
        raise QCOperationError(message, profile=profile)

    def pyplot(self, profile):
        """
        Get a version of matplotlib.pyplot used for use in a ``with``
        statement. The default method returns a context manager that
        wraps a dummy version of the module that does nothing.
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


class QCOperationProfileContext:
    """
    Internal class used by :func:`QCOperation.run` to set the
    profile, previous profile, and context during execution of
    :func:`QCOperation.run_impl`.
    """

    def __init__(self, op, profile=None, previous_profile=None, context=None) -> None:
        self._op = op
        self._profile = profile
        self._previous_profile = previous_profile
        if context is None:
            self._context = QCOperationContext()
        else:
            self._context = context

    def __enter__(self):
        self._old_profile = self._op.profile
        self._old_previous_profile = self._op.previous_profile
        self._old_context = self._context

        self._op.profile = self._profile
        self._op.previous_profile = self._previous_profile
        self._op.context = self._context

    def __exit__(self, *execinfo):
        self._op.profile = self._old_profile
        self._op.previous_profile = self._old_previous_profile
        self._op.context = self._old_context


class QCOperation:
    """
    A QC operation is instantiated with the parameters
    that govern the functioning of the test (if any) and are :func:`run`
    with the :class:`medsrtqc.core.Profile` as an argument. QC operations
    should implement the :func:`run_impl` method and use the built-in
    methods to do any data updates or communication with the user.
    """

    def __init__(self):
        self.context = None
        self.profile = None
        self.previous_profile = None

    def update_trace(self, k, trace):
        """Convenience wrapper for :func:`QCOperationContext.update_trace`"""
        self.context.update_trace(self.profile, k, trace)

    def log(self, message):
        """Convenience wrapper for :func:`QCOperationContext.log`"""
        self.context.log(self.profile, message)

    def error(self, message):
        """Convenience wrapper for :func:`QCOperationContext.error`"""
        self.context.error(self.profile, message)

    def pyplot(self):
        """Convenience wrapper for :func:`QCOperationContext.pyplot`"""
        return self.context.pyplot(self.profile)

    def run(self, profile, previous_profile=None, context=None):
        """
        Run the test. This is the method used by callers to actually
        run the test. The default method temporarily sets ``self.profile`` and
        ``self.previous_profile`` and calls :func:`run_impl`.
        """
        with QCOperationProfileContext(self, profile, previous_profile, context):
            return self.run_impl()

    def run_impl(self):
        """Test implementation. This method must be implemented by test subclasses."""
        raise NotImplementedError()
