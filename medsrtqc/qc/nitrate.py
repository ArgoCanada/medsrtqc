
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

        # spike test
        self.log('Applying spike test to NITRATE')
        median_nit = self.running_median(5)
        res = nitrate.value - median_nit
        high_res = res > 5
        Flag.update_safely(nitrate.qc, Flag.BAD, high_res)
        QCx.update_safely(self.profile.qc_tests, 9, not any(high_res))
        all_passed = all_passed and not any(high_res)

    def running_median(self, n):
        self.log(f'Calculating running median over window size {n}')
        x = self.profile['NIT$'].value
        ix = np.arange(n) + np.arange(len(x)-n+1)[:,None]
        b = [row[row > 0] for row in x[ix]]
        k = int(n/2)
        med = [np.median(c) for c in b]
        med = np.array(k*[np.nan] + med + k*[np.nan])
        return med