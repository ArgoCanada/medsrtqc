
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

# quiet context for testing
class TestContext(QCOperationContext):
    def log(self, *args, **kwargs):
        pass

class TestBbpTest(unittest.TestCase):

    def test_basic(self):
        ncp = read_nc_profile(
            resource_path('BR6904117_085.nc'),
            resource_path('R6904117_085.nc')
        )

        ncp_writable = Profile({
            'PRES': ncp['PRES'],
            'TEMP': ncp['TEMP'],
            'PSAL': ncp['PSAL'],
            'B700': ncp['BETA_BACKSCATTERING700'],
            'BBP$': ncp['BBP700'],
        })
        # this isn't true, but equally demonstrates ability to look up coefficients
        # we don't have coeffs for 6904117
        ncp_writable.wmo = 6903026
        ncp_writable.cycle_number = 85

        # reset the QC flags for CHLA
        ResetQCOperation().run(ncp_writable)
        self.assertTrue(np.all(ncp_writable['BBP$'].qc == Flag.NO_QC))

        test = bbpTest()
        test.run(ncp_writable, context=TestContext())
        self.assertTrue(np.all(ncp_writable['BBP$'].qc == Flag.GOOD))

    def test_betasw(self):

        ncp = read_nc_profile(
            resource_path('R6904117_085.nc')
        )

        # betasw(P, T, S, lon, lat, wavelength, theta)
        beta_seawater = betasw(ncp['PRES'].value, ncp['TEMP'].value, ncp['PSAL'].value, 0, 0, 700, 70)

        self.assertTrue(np.all(beta_seawater[~np.isnan(beta_seawater)] > 0))


if __name__ == '__main__':
    unittest.main()
