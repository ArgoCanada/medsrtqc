
import unittest
import numpy as np

from medsrtqc.core import Profile
from medsrtqc.resources import resource_path
from medsrtqc.nc import read_nc_profile
from medsrtqc.vms import read_vms_profiles
from medsrtqc.qc.chla import ChlaTest
from medsrtqc.qc.operation import QCOperationContext
from medsrtqc.qc.util import ResetQCOperation
from medsrtqc.qc.flag import Flag
from medsrtqc.qc.history import QCx

# quiet context for testing
class TestContext(QCOperationContext):
    def log(self, *args, **kwargs):
        pass


class TestChlaTest(unittest.TestCase):

    def test_basic(self):
        
        vms = read_vms_profiles(resource_path('bgc_vms.dat'))
        prof = vms[0]
        prof.prepare()

        # reset the QC flags for CHLA
        ResetQCOperation().run(prof)
        self.assertTrue(np.all(prof['FLU1'].qc == Flag.NO_QC))

        test = ChlaTest()
        test.run(prof, context=TestContext())
        self.assertTrue(np.all(prof['FLU1'].qc != Flag.NO_QC))

    def test_bad_counts(self):

        vms = read_vms_profiles(resource_path('bgc_vms.dat'))
        prof = vms[0]
        prof['FLU3'] = prof['B700']
        prof.prepare()
        
        # reset the QC flags for CHLA
        ResetQCOperation().run(prof)
        self.assertTrue(np.all(prof['FLU1'].qc == Flag.NO_QC))

        test = ChlaTest()
        test.run(prof, context=TestContext())
        self.assertTrue(np.all(prof['FLU1'].qc == Flag.PROBABLY_BAD))

if __name__ == '__main__':
    unittest.main()
