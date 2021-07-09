
import numpy as np
from ..core import QCOperation
from .flag import Flag


class QCTest(QCOperation):
    """
    Whereas :class:`~medsrtqc.core.QCOperation`s are generic and
    can do anything, a ``QCTest`` is a specific operation defined
    within the Argo data management framework. ``QCTest``s have
    names, binary IDs, and specific descriptions.
    """
    argo_id = None
    argo_binary_id = None
    argo_name = None
    nvs_uri = None


class PressureIncreasingTest(QCTest):
    argo_id = 8
    argo_binary_id = 256
    argo_name = "Pressure increasing test"
    nvs_uri = "http://vocab.nerc.ac.uk/collection/R11/current/8/"

    def run(self):
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
