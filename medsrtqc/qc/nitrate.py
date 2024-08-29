
import copy
import numpy as np

from medsrtqc.qc.operation import QCOperation
from medsrtqc.qc.flag import Flag
from medsrtqc.qc.history import QCx

class nitrateTest(QCOperation):

    def run_impl(self):
        nitrate = self.profile['NTR2']
        all_passed = True

        self.log('Setting previously unset flags for NITRATE to PROBABLY_BAD')
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

        # stuck value test
        self.log('Performing stuck value test on NITRATE')
        stuck_value = all(nitrate.value == nitrate.value[0])
        if stuck_value: # pragma: no cover
            self.log('stuck values found, setting all profile flags to 4')
            Flag.update_safely(nitrate.qc, Flag.BAD)
        QCx.update_safely(self.profile.qc_tests, 13, not stuck_value)

        # nitrate specific tests
        temp = self.profile['TEMP']
        temp_syn_qc = [temp.qc[np.abs(temp.pres - p) == np.min(np.abs(temp.pres - p))] for p in nitrate.pres]
        Flag.update_safely(nitrate.qc, Flag.BAD, temp_syn_qc == 4)

        # sensor saturation value
        # sensor_saturated = self.profile['NO3S'] == 2**16-1
        # Flag.update_safely(nitrate.qc, Flag.PROBABLY_BAD, sensor_saturated)
        # all_passed = all_passed and not any(sensor_saturated)

        # absorbance at 240nm

        # RMSE of fit residuals
        high_residual = self.profile['NO3R'].value >= 0.003
        Flag.update_safely(nitrate.qc, Flag.BAD, high_residual)
        all_passed = all_passed and not any(high_residual)

        # update QCP/QCF
        QCx.update_safely(self.profile.qc_tests, 59, all_passed)

        # update the CHLA trace
        self.update_trace('NTR2', nitrate)

        return nitrate

    def running_median(self, n):
        self.log(f'Calculating running median over window size {n}')
        x = self.profile['NTR2'].value
        ix = np.arange(n) + np.arange(len(x)-n+1)[:,None]
        b = [row[row > 0] for row in x[ix]]
        k = int(n/2)
        med = [np.median(c) for c in b]
        med = np.array(k*[np.nan] + med + k*[np.nan])
        return med