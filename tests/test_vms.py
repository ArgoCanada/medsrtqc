
import unittest
from medsrtqc import vms


class TestOceanProcessingProfile(unittest.TestCase):

    def test_profile(self):
        prof = vms.OceanProcessingProfile()
        self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main()
