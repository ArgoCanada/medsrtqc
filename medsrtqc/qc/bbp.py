
import numpy as np

from .operation import QCOperation, QCOperationError
from .flag import Flag

class bbpSpikeTest(QCOperation):

    def run_impl(self):
        # global range test will be within this method as well
        bbp = self.profile['BBP']
        self.update_trace('BBP', bbp)

    def running_median(self, n):
        self.log(f'Calculating running median over window size {n}')
        x = self.profile['BBP']
        ix = np.arange(n) + np.arange(len(x)-n+1)[:,None]
        b = [row[row > 0] for row in x[ix]]
        k = int(n/2)
        med = [np.median(c) for c in b]
        med = np.array(k*[np.nan] + med + k*[np.nan])
        return med

