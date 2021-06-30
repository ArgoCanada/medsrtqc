
import unittest
import os
from netCDF4 import Dataset
from medsrtqc.resources import resource_path
from medsrtqc.nc import read_nc_profile
from medsrtqc.core import Trace


class TestNetCDFProfile(unittest.TestCase):

    def test_variable_finding(self):
        profile = read_nc_profile(resource_path('BR6904117_085.nc'))
        self.assertIsInstance(profile._datasets[0], Dataset)
        self.assertIn('PRES', profile.keys())
        self.assertIsInstance(profile['PRES'], Trace)

    def test_dataset_file(self):
        nc_abspath = read_nc_profile(resource_path('BR6904117_085.nc'))
        self.assertIsInstance(nc_abspath._datasets[0], Dataset)

        test_file_abs = resource_path('BR6904117_085.nc')
        test_file_rel = os.path.relpath(test_file_abs, os.getcwd())
        nc_relpath = read_nc_profile(test_file_rel)
        self.assertIsInstance(nc_relpath._datasets[0], Dataset)

    def test_dataset_bytes(self):
        with open(resource_path('BR6904117_085.nc'), 'rb') as f:
            self.assertIsInstance(read_nc_profile(f.read())._datasets[0], Dataset)

    def test_dataset_url(self):
        path = 'dac/coriolis/6904117/profiles/BR6904117_085.nc'
        url = 'https://data-argo.ifremer.fr/' + path
        self.assertIsInstance(read_nc_profile(url)._datasets[0], Dataset)

    def test_dataset_dataset(self):
        ds = Dataset(resource_path('BR6904117_085.nc'))
        self.assertIs(read_nc_profile(ds)._datasets[0], ds)

    def test_dataset_unknown(self):
        with self.assertRaises(ValueError):
            read_nc_profile('this is not anything')


if __name__ == '__main__':
    unittest.main()
