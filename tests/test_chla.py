
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
        ncp = read_nc_profile(
            resource_path('BR6904117_085.nc'),
            resource_path('R6904117_085.nc')
        )

        ncp_writable = Profile({
            'PRES': ncp['PRES'],
            'TEMP': ncp['TEMP'],
            'PSAL': ncp['PSAL'],
            'FLU3': ncp['FLUORESCENCE_CHLA'],
            'FLU1': ncp['CHLA'],
            'FLUA': ncp['CHLA'],
        })
        # this isn't true, but equally demonstrates ability to look up coefficients
        # we don't have coeffs for 6904117
        ncp_writable.wmo = 6903026
        ncp_writable.cycle_number = 85

        # reset the QC flags for CHLA
        ResetQCOperation().run(ncp_writable)
        self.assertTrue(np.all(ncp_writable['FLU1'].qc == Flag.NO_QC))

        test = ChlaTest()
        test.run(ncp_writable, context=TestContext())
        self.assertTrue(np.all(ncp_writable['FLU1'].qc != Flag.NO_QC))

    def test_bad_counts(self):

        vms = read_vms_profiles(resource_path('bgc_vms.dat'))

        # use counts from backscatter, which will be way off of chla counts
        ncp_writable = Profile({
            'PRES': vms[0]['PRES'],
            'TEMP': vms[0]['TEMP'],
            'PSAL': vms[0]['PSAL'],
            'FLU3': vms[0]['B700'],
            'FLU1': vms[0]['FLU1'],
            'FLUA': vms[0]['FLU1'],
        })

        # this isn't true, but equally demonstrates ability to look up coefficients
        # we don't have coeffs for 6904117
        ncp_writable.wmo = 6903026
        ncp_writable.cycle_number = 85
        ncp_writable.qc_tests = QCx.qc_tests(self.get_surf_code('QCP$'), self.get_surf_code('QCF$'))

        # reset the QC flags for CHLA
        ResetQCOperation().run(ncp_writable)
        self.assertTrue(np.all(ncp_writable['FLU1'].qc == Flag.NO_QC))

        test = ChlaTest()
        test.run(ncp_writable, context=TestContext())
        self.assertTrue(np.all(ncp_writable['FLU1'].qc == Flag.PROBABLY_BAD))

if __name__ == '__main__':
    unittest.main()
