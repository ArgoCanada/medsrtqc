
import numpy as np

from medsrtqc.core import Trace
from medsrtqc.qc.operation import QCOperation
from medsrtqc.qc.flag import Flag
from medsrtqc.coefficient import gains

class doxyTest(QCOperation):

    def run_impl(self):
        doxy = self.profile['DOXY']
        adjusted = self.profile['DOXA']

        gain = gains[self.wmo]

        print(adjusted)
        print("verify that adjusted flags aren't stuck on 3")

        self.log('Setting previously unset flags for DOXY_ADJUSTED to PROBABLY_GOOD')
        Flag.update_safely(adjusted.qc, to=Flag.PROBABLY_GOOD)

        print(adjusted)
        print('verify that QC=4 where DOXY_QC=4 is taken')

        self.log('Setting DOXY_ADJUSTED flags to BAD where DOXY_QC is BAD')
        Flag.update_safely(adjusted.qc, to=Flag.BAD, where=doxy.qc == Flag.BAD)

        print(adjusted)

        adjusted = Trace(
            pres=adjusted.pres, 
            value=self.apply_gain(gain['gain'], gain['date']),
            qc=adjusted.qc,
            mtime=adjusted.mtime
        )

        self.update_trace('DOXA', adjusted)
    
    def apply_gain(self, g, t):
        # hello!
        print(0)