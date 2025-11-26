
import copy
import numpy as np

from medsrtqc.qc.operation import QCOperation
from medsrtqc.qc.flag import Flag
from medsrtqc.coefficient import gains

class doxyTest(QCOperation):

    def run_impl(self):
        doxy = self.profile['DOXY']