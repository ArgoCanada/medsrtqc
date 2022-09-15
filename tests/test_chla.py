
import unittest
import numpy as np

from medsrtqc.core import Profile
from medsrtqc.resources import resource_path
from medsrtqc.nc import read_nc_profile
from medsrtqc.qc.chla import ChlaTest
from medsrtqc.qc.operation import QCOperationContext
from medsrtqc.qc.util import ResetQCOperation
from medsrtqc.qc.flag import Flag


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
            'FLU1': ncp['CHLA'],
            'FLU3': ncp['FLUORESCENCE_CHLA']
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

        # change counts to be way off so that new dark count is more than 20% different
        ncp_writable['FLU3'].value = ncp_writable['FLU3'].value + 200
        test.run(ncp_writable, context=TestContext())
        self.assertTrue(np.all(ncp_writable['FLU1'].qc == Flag.PROBABLY_BAD))


if __name__ == '__main__':
    unittest.main()
