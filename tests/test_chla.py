
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
            'FLU1': ncp['CHLA']
        })

        # reset the QC flags for CHLA
        ResetQCOperation().run(ncp_writable)
        self.assertTrue(np.all(ncp_writable['FLU1'].qc == Flag.NO_QC))

        test = ChlaTest()
        test.run(ncp_writable, context=TestContext())
        self.assertTrue(np.all(ncp_writable['FLU1'].qc == Flag.PROBABLY_BAD))


if __name__ == '__main__':
    unittest.main()
