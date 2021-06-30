
import unittest
import os

from medsrtqc.resources import resource_path

class TestResources(unittest.TestCase):

    def test_exists(self):
        res = ['BINARY_VMS.DAT', 'BINARY_VMS.json']
        for r in res:
            self.assertTrue(os.path.isfile(resource_path(r)))

if __name__ == '__main__':
    unittest.main()