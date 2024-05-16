
import copy
import numpy as np

from medsrtqc.qc.operation import QCOperation
from medsrtqc.qc.flag import Flag
from medsrtqc.qc.history import QCx

class nitrateTest(QCOperation):

    def run_impl(self):
        nitrate = self.profile['NIT$']
        all_passed = True