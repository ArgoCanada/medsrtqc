
import numpy as np

from medsrtqc.qc.operation import QCOperation
from medsrtqc.qc.flag import Flag
from medsrtqc.qc.history import QCx

class bbpTest(QCOperation):

    def run_impl(self):
        bbp = self.profile['BBP$']
        all_passed = True
        
        if 'B700' in self.profile.keys():
            lower_lim = -0.000025
        elif 'B532' in self.profile.keys():
            lower_lim = -0.000005
        else:
            self.log(f'No valid wavelength information found, setting lower limit of range check to -0.000025')
            lower_lim = -0.000025

        self.log('Setting previously unset flags for BBP to GOOD')
        Flag.update_safely(bbp.qc, to=Flag.GOOD)

        # global range test
        self.log('Applying global range test to BBP')
        values_outside_range = (bbp.value < lower_lim) | (bbp.value > 0.1)
        Flag.update_safely(bbp.qc, Flag.PROBABLY_BAD, values_outside_range)
        QCx.update_safely(self.profile.qc_tests, 6, not any(values_outside_range))
        all_passed = all_passed and any(values_outside_range)

        # BBP spike test
        self.log('Performing negative spike test')
        median_bbp = self.running_median(5)
        res = bbp.value - median_bbp
        spike_values = res < 2*np.percentile(res, 10)
        Flag.update_safely(bbp.qc, Flag.BAD, spike_values)
        all_passed = all_passed and any(spike_values)
        QCx.update_safely(self.profile.qc_tests, 9, not any(spike_values))

        # update QCP/QCF
        QCx.update_safely(self.profile.qc_tests, 62, all_passed)

        # update trace
        self.update_trace('BBP$', bbp)

    def running_median(self, n):
        self.log(f'Calculating running median over window size {n}')
        x = self.profile['BBP$'].value
        ix = np.arange(n) + np.arange(len(x)-n+1)[:,None]
        b = [row[row > 0] for row in x[ix]]
        k = int(n/2)
        med = [np.median(c) for c in b]
        med = np.array(k*[np.nan] + med + k*[np.nan])
        return med

