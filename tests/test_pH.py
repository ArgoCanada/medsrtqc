
import unittest
import numpy as np

from medsrtqc.resources import resource_path
from medsrtqc.vms import read_vms_profiles
from medsrtqc.qc.ph import pHTest
from medsrtqc.qc.operation import QCOperationContext
from medsrtqc.qc.util import ResetQCOperation
from medsrtqc.qc.flag import Flag

# quiet context for testing
class TestContext(QCOperationContext):
    def log(self, *args, **kwargs):
        pass


class TestpHTest(unittest.TestCase):

    def test_basic(self):
        vms = read_vms_profiles(resource_path('bgc_vms.dat'))
        prof = vms[0]
        prof.prepare()

        # reset the QC flags for CHLA
        ResetQCOperation().run(prof)
        self.assertTrue(np.all(prof['PHPH'].qc == Flag.NO_QC))
        self.assertTrue(np.all(prof['PHTO'].qc == Flag.NO_QC))

        test = pHTest()
        test.run(prof, context=TestContext())
        self.assertTrue(np.all(prof['PHPH'].qc == Flag.NO_QC))

if __name__ == '__main__':
    unittest.main()