
import unittest
import os

from medsrtqc.resources import resource_path


class TestResources(unittest.TestCase):

    def test_exists(self):
        res = [
            'BINARY_VMS.DAT', 'BINARY_VMS.json',
            'BR6904117_085.nc', 'R6904117_085.nc',
            'OUTPUT_RT.DAT', 'OUTPUT_RT.json'
        ]

        for r in res:
            self.assertTrue(os.path.isfile(resource_path(r)))

        with self.assertRaises(FileNotFoundError):
            resource_path('definitely not a resource')


if __name__ == '__main__':
    unittest.main()
