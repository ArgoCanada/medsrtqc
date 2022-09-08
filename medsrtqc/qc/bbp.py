
import numpy as np

from .operation import QCOperation, QCOperationError
from .flag import Flag

class bbpTest(QCOperation):

    def run_impl(self):
        # get sensor constants
        # wavelength = get wavelength, similar to dark counts or scale
        wavelength = 700 # dummy placeholder, also will probably always be 700nm

        # convert sensor value to backscatter
        bbp = self.profile['BBP$']
        
        if wavelength == 532:
            lower_lim = -0.000005
        elif wavelength == 700:
            lower_lim = -0.000025
        else:
            self.log(f'No valid wavelength provided (wavelength = {wavelength:d}), setting lower limit of range check to -0.000025')
            lower_lim = -0.000025

        self.log('Setting previously unset flags for BBP to GOOD')
        Flag.update_safely(bbp.qc, to=Flag.GOOD)

        self.log('Setting previously unset flags for BBP_ADJUSTED to GOOD')
        Flag.update_safely(bbp.adjusted_qc, to=Flag.GOOD)

        # global range test
        self.log('Applying global range test to BBP')
        values_outside_range = (bbp.value < lower_lim) | (bbp.value > 0.1)
        Flag.update_safely(bbp.qc, Flag.BAD, values_outside_range)
        Flag.update_safely(bbp.adjusted_qc, Flag.BAD, values_outside_range)

        # BBP spike test
        self.log('Performing negative spike test')
        median_bbp = self.running_median(5)
        res = bbp.value - median_bbp
        spike_values = res < 2*np.percentile(res, 10)
        Flag.update_safely(bbp.qc, Flag.BAD, spike_values)
        Flag.update_safely(bbp.adjusted_qc, Flag.BAD, spike_values)

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

