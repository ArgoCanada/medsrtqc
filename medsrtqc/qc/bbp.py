
import numpy as np

from .operation import QCOperation, QCOperationError
from .flag import Flag

class bbpSpikeTest(QCOperation):

    def run_impl(self):
        # global range test will be within this method as well
        bbp = self.profile['BBP']
        self.update_trace('BBP', bbp)

        bbp = self.profile['BBP']

        # NOTE this is copied from CHLA, verify in manual that this is proper flagging
        self.log('Setting previously unset flags for BBP to PROBABLY_BAD')
        Flag.update_safely(bbp.qc, to=Flag.PROBABLY_BAD)

        self.log('Setting previously unset flags for BBP_ADJUSTED to GOOD')
        Flag.update_safely(bbp.adjusted_qc, to=Flag.GOOD)

    def running_median(self, n):
        self.log(f'Calculating running median over window size {n}')
        x = self.profile['BBP']
        ix = np.arange(n) + np.arange(len(x)-n+1)[:,None]
        b = [row[row > 0] for row in x[ix]]
        k = int(n/2)
        med = [np.median(c) for c in b]
        med = np.array(k*[np.nan] + med + k*[np.nan])
        return med

