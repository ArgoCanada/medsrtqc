
import copy
import numpy as np

from medsrtqc.qc.operation import QCOperation
from medsrtqc.qc.flag import Flag
from medsrtqc.qc.history import QCx

class nitrateTest(QCOperation):

    def run_impl(self):
        nitrate = self.profile['NIT$']
        all_passed = True

        self.log('Setting previously unset flags for BBP to PROBABLY_BAD')
        Flag.update_safely(nitrate.qc, to=Flag.PROBABLY_BAD)

        # global range test
        self.log('Applying global range test to NITRATE')
        values_outside_range = (nitrate.value < -15.0) | (nitrate.value > 65.0)
        Flag.update_safely(nitrate.qc, Flag.BAD, values_outside_range)
        QCx.update_safely(self.profile.qc_tests, 6, not any(values_outside_range))
        all_passed = all_passed and not any(values_outside_range)
