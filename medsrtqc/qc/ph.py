
import numpy as np

from medsrtqc.qc.operation import QCOperation
from medsrtqc.qc.flag import Flag
from medsrtqc.qc.history import QCx

class pHTest(QCOperation):

    def run_impl(self):
        pH_free = self.profile['PHPH']
        pH_total = self.profile['PHTO']

        # set flags to zero, there are no QC tests for pH yet
        Flag.update_safely(pH_free.qc, Flag.NO_QC)
        self.update_trace('PHPH', pH_free)

        # set flags of pH in situ to 3 by default
        Flag.update_safely(pH_free.qc, Flag.PROBABLY_BAD)

        # global range test
        self.log('Applying global range test to PH_IN_SITU_TOTAL')
        values_outside_range = (pH_total.value < 7.0) | (pH_total.value > 8.3)
        Flag.update_safely(pH_total.qc, Flag.BAD, values_outside_range)
        QCx.update_safely(self.profile.qc_tests, 6, not any(values_outside_range))

        # spike test
        self.log('Performing spike test on pH')
        median_chla = self.running_median(5)
        res = np.abs(pH_total.value - median_chla)
        spike_values = res > 0.04
        Flag.update_safely(pH_total.qc, Flag.BAD, spike_values)
        QCx.update_safely(self.profile.qc_tests, 9, not any(spike_values))

        # stuck value test
        self.log('Performing stuck value test on total pH')
        stuck_value = all(pH_total.value == pH_total.value[0])
        if stuck_value: # pragma: no cover
            self.log('stuck values found, setting all profile flags to 4')
            Flag.update_safely(pH_total.qc, Flag.BAD)
        QCx.update_safely(self.profile.qc_tests, 13, not stuck_value)

        # pH specific tests
        pres = self.profile['PRES']
        temp = self.profile['TEMP']
        temp_syn_qc = [temp.qc[np.abs(temp.pres - p) == np.min(np.abs(temp.pres - p))] for p in pH_total.pres]
        Flag.update_safely(pH_total.qc, Flag.BAD, temp_syn_qc == 4)
        pres_syn_qc = [pres.qc[np.abs(pres.value - p) == np.min(np.abs(pres.value - p))] for p in pH_total.pres]
        Flag.update_safely(pH_total.qc, Flag.BAD, pres_syn_qc == 4)
        # technically another test is pH_total.qc = 3 if psal.qc = 4 but
        # pH_total.qc is already 3 by default - will matter for adjusted mode?

        # currently no number in bgc manual for these tests? manual from Tanya has 56 or 59?
        # QCx.update_safely(self.profile.qc_tests, 56, not stuck_value)
        
        self.update_trace('PHTO', pH_total)

    def running_median(self, n):
        self.log(f'Calculating running median over window size {n}')
        x = self.profile['PHTO'].value
        ix = np.arange(n) + np.arange(len(x)-n+1)[:,None]
        b = [row[row > 0] for row in x[ix]]
        k = int(n/2)
        med = [np.median(c) for c in b]
        med = np.array(k*[np.nan] + med + k*[np.nan])
        return med
