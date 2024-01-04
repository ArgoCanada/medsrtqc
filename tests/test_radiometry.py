
import unittest
import numpy as np

from medsrtqc.resources import resource_path
from medsrtqc.qc.radio import radiometryTest
from medsrtqc.qc.operation import QCOperationContext
from medsrtqc.qc.util import ResetQCOperation
from medsrtqc.qc.flag import Flag
from medsrtqc.vms.read import read_vms_profiles

# quiet context for testing
class TestContext(QCOperationContext):
    def log(self, *args, **kwargs):
        pass

class TestRadioTest(unittest.TestCase):

    def test_basic(self):
        vms = read_vms_profiles(resource_path('bgc_vms.dat'))
        test = radiometryTest()
        prof = vms[0]
        prof.prepare(tests=[test])

        # reset the QC flags for BBP
        ResetQCOperation().run(prof)
        self.assertTrue(np.all(prof['PAR$'].qc == Flag.NO_QC))

        test.run(prof, context=TestContext())
        self.assertTrue(np.all(prof['PAR$'].qc == Flag.GOOD))