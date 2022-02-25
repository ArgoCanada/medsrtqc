
import numpy as np

from .operation import QCOperation, QCOperationError
from .flag import Flag

class bbpSpikeTest(QCOperation):

    def run_impl(self):
        # global range test will be within this method as well
        bbp = self.profile['BBP']
        self.update_trace('BBP', bbp)
