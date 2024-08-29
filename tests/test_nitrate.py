
import unittest
import numpy as np

from medsrtqc.resources import resource_path
from medsrtqc.nc import read_nc_profile
from medsrtqc.qc.nitrate import nitrateTest
from medsrtqc.qc.operation import QCOperationContext
from medsrtqc.qc.util import ResetQCOperation
from medsrtqc.qc.flag import Flag
from medsrtqc.vms.read import read_vms_profiles

# quiet context for testing
class TestContext(QCOperationContext):
    def log(self, *args, **kwargs):
        pass

class TestNitrateTest(unittest.TestCase):

    def test_basic(self):
        vms = read_vms_profiles(resource_path('arvor_bgc_win_qc_output_mass.dat'), ver='win')
        test = nitrateTest()
        prof = vms[3]
        prof.prepare(tests=[test])

        test.run(prof, context=TestContext())
        self.assertTrue(np.all(prof['NTR2'].qc == Flag.PROBABLY_BAD))

        # fails because no temperature in BD - use TEMP_DOXY?
        # nc = read_nc_profile(resource_path('BD6903197_026.nc'))
        # print(nc.keys())
        # nc.prepare(tests=[test])
        # test.run(nc)

if __name__ == '__main__':
    unittest.main()