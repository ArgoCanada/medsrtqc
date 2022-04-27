
import numpy as np

from .operation import QCOperation, QCOperationError
from .flag import Flag

class bbpSpikeTest(QCOperation):

    def run_impl(self):
        beta = self.profile['BETA_BACKSCATTERING']
        bbp = self.profile['BBP']

        # get wavelength
        # wavelength = get wavelength, similar to dark counts or scale
        wavelength = 700 # dummy placeholder, also will probably always be 700nm

        if wavelength == 532:
            lower_lim = -0.000005
        elif wavelength == 700:
            lower_lim = -0.000025
        else:
            self.log(f'No valid wavelength provided (wavelength = {wavelength:d}), setting lower limit of range check to -0.000025')
            lower_lim = -0.000025

        # NOTE this is copied from CHLA, verify in manual that this is proper flagging
        self.log('Setting previously unset flags for BBP to PROBABLY_BAD')
        Flag.update_safely(bbp.qc, to=Flag.PROBABLY_BAD)

        self.log('Setting previously unset flags for BBP_ADJUSTED to GOOD')
        Flag.update_safely(bbp.adjusted_qc, to=Flag.GOOD)

        # global range test
        self.log('Applying global range test to BBP')
        values_outside_range = (bbp.value < lower_lim) | (bbp.value > 0.1)
        Flag.update_safely(bbp.qc, Flag.BAD, values_outside_range)
        Flag.update_safely(bbp.adjusted_qc, Flag.BAD, values_outside_range)

    def running_median(self, n):
        self.log(f'Calculating running median over window size {n}')
        x = self.profile['BBP']
        ix = np.arange(n) + np.arange(len(x)-n+1)[:,None]
        b = [row[row > 0] for row in x[ix]]
        k = int(n/2)
        med = [np.median(c) for c in b]
        med = np.array(k*[np.nan] + med + k*[np.nan])
        return med

