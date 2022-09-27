
import unittest

from medsrtqc.core import Profile
from medsrtqc.resources import resource_path
from medsrtqc.vms import read_vms_profiles
from medsrtqc.qc.check import preTestCheck
from medsrtqc.qc.operation import QCOperationContext

# quiet context for testing
class TestContext(QCOperationContext):
    def log(self, *args, **kwargs):
        pass

class TestPreCheckTest(unittest.TestCase):

    def test_basic(self):
        vms = read_vms_profiles(resource_path('bgc_vms.dat'))
        p = vms[0]

        check = preTestCheck()
        tests = check.run(p, context=TestContext())
        self.assertTrue(len(tests) == 2)

        self.assertTrue('FLUA' in p.keys())

if __name__ == '__main__':
    unittest.main()