
import unittest
import numpy as np

from medsrtqc.core import Profile
from medsrtqc.betasw import betasw
from medsrtqc.resources import resource_path
from medsrtqc.nc import read_nc_profile
from medsrtqc.qc.bbp import bbpTest
from medsrtqc.qc.operation import QCOperationContext
from medsrtqc.qc.util import ResetQCOperation
from medsrtqc.qc.flag import Flag
from medsrtqc.qc.history import QCx

# quiet context for testing
class TestContext(QCOperationContext):
    def log(self, *args, **kwargs):
        pass

class TestBbpTest(unittest.TestCase):

    def test_basic(self):
        vms = read_nc_profile(
            resource_path('bgc_vms.dat'),
        )
        prof = vms[0]
        prof.prepare()

        # reset the QC flags for CHLA
        ResetQCOperation().run(prof)
        self.assertTrue(np.all(prof['BBP$'].qc == Flag.NO_QC))

        test = bbpTest()
        test.run(prof, context=TestContext())
        self.assertTrue(np.all(prof['BBP$'].qc == Flag.GOOD))

    def test_betasw(self):

        ncp = read_nc_profile(
            resource_path('R6904117_085.nc')
        )

        beta_seawater = betasw(ncp['PRES'].value, ncp['TEMP'].value, ncp['PSAL'].value, 0, 0, 700, 70)

        self.assertTrue(np.all(beta_seawater[~np.isnan(beta_seawater)] > 0))


if __name__ == '__main__':
    unittest.main()
