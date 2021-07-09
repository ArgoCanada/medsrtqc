
"""
The ``named_tests`` module contains the named tests in the
Argo QC handbook. The main difference between a these tests
and a regular :class:`~medsrtqc.core.QCOperation` is that
they (1) have an ID, binary ID,and NVS URI and (2) the
:func:`~medsrtqc.core.QCOperation.run` method returns
``True`` or ``False`` to indicate a "passed" or "failed"
check. Most tests also modify the input
:class:`~medsrtqc.core.Profile` (e.g., to set flags).
"""

import numpy as np
from ..core import QCOperation
from .flag import Flag

# a lot of this is copied+modified from
# https://github.com/euroargodev/argortqcpy/blob/main/argortqcpy/checks.py
# in the future this package should import that one and use it where
# possible!


class QCTest(QCOperation):
    """
    Whereas a :class:`~medsrtqc.core.QCOperation` is generic and
    can do anything, a ``QCTest`` is a specific operation defined
    within the Argo data management framework. ``QCTest``s have
    names, binary IDs, and specific descriptions.
    """
    argo_id = None
    argo_binary_id = None
    argo_name = None
    nvs_uri = None

    def run_impl(self) -> bool:  # pragma: no cover
        """Run the test and return ``True`` if it passed or ``False`` otherwise"""
        return super().run_impl()


class PressureIncreasingTest(QCTest):
    """
    The pressure increasing test checks for monotonically increasing
    pressure. The test modifies the QC flags for PRES, TEMP, and PSAL
    and fails if any of these flags were set to ``Flag.BAD``.

    >>> from medsrtqc.qc.named_tests import PressureIncreasingTest
    >>> from medsrtqc.qc.flag import Flag
    >>> from medsrtqc.core import Trace, Profile
    >>> import numpy as np
    >>> qc5 = np.repeat([Flag.NO_QC], 5)
    >>> pres =  Trace([0, 50, 0, 50, 100], qc=qc5)
    >>> pres.pres = pres.value
    >>> prof = Profile({
    ...     'PRES': pres,
    ...     'TEMP': Trace([10, 5, 7, 7, 7], qc=qc5, pres=pres.value),
    ...     'PSAL': Trace([8, 9, 10, 11, 12], qc=qc5, pres=pres.value)
    ... })
    >>> PressureIncreasingTest().run(prof)
    >>> prof['PRES']
    """

    argo_id = 8
    argo_binary_id = 256
    argo_name = "Pressure increasing test"
    nvs_uri = "http://vocab.nerc.ac.uk/collection/R11/current/8/"

    def run_impl(self):
        pres = self.profile['PRES']
        temp = self.profile['TEMP']
        psal = self.profile['PSAL']

        # ensure pressure values are identical for the three params
        temp_pres_eq = temp.pres == pres.value
        psal_pres_eq = psal.pres == pres.value
        if not np.all(temp_pres_eq) or not np.all(psal_pres_eq):
            self.error("Pressure values not identical for 'PRES', 'TEMP', and/or 'PSAL'")

        # do the first pass checking that every value is increasing
        diff = np.diff(pres.value, prepend=-np.inf)  # first measurement always passes
        non_monotonic_elements = diff < 0.0
        Flag.update_safely(pres.qc, Flag.BAD, where=non_monotonic_elements)
        Flag.update_safely(temp.qc, Flag.BAD, where=non_monotonic_elements)
        Flag.update_safely(psal.qc, Flag.BAD, where=non_monotonic_elements)

        # do the second pass finding consecutive constant values
        constant = diff == 0.0
        Flag.update_safely(pres.qc, Flag.BAD, where=constant)
        Flag.update_safely(temp.qc, Flag.BAD, where=constant)
        Flag.update_safely(psal.qc, Flag.BAD, where=constant)

        # do the third pass finding any sections where it has been non-montonic and
        # is still below the last good value this is a running maximum,
        # constant parts mean bad values
        running_maximum = np.maximum.accumulate(pres.value, axis=-1)
        running_maximum_constant = np.diff(running_maximum, prepend=-np.inf) == 0.0
        Flag.update_safely(pres.qc, Flag.BAD, where=running_maximum_constant)
        Flag.update_safely(temp.qc, Flag.BAD, where=running_maximum_constant)
        Flag.update_safely(psal.qc, Flag.BAD, where=running_maximum_constant)

        # apply updates
        self.update_trace('PRES', pres)
        self.update_trace('TEMP', temp)
        self.update_trace('PSAL', psal)

        # fail for any flags set as BAD
        return not np.any(non_monotonic_elements | constant | running_maximum_constant)
