
import unittest
import os
from netCDF4 import Dataset
from medsrtqc.resources import resource_path
from medsrtqc.nc import read_nc_profile


class TestNetCDFProfile(unittest.TestCase):

    def test_dataset_file(self):
        nc_abspath = read_nc_profile(resource_path('BR2902746_001.nc'))
        self.assertIsInstance(nc_abspath._dataset, Dataset)

        test_file_abs = resource_path('BR2902746_001.nc')
        test_file_rel = os.path.relpath(test_file_abs, os.getcwd())
        nc_relpath = read_nc_profile(test_file_rel)
        self.assertIsInstance(nc_relpath._dataset, Dataset)

    def test_dataset_bytes(self):
        with open(resource_path('BR2902746_001.nc'), 'rb') as f:
            self.assertIsInstance(read_nc_profile(f.read())._dataset, Dataset)

    def test_dataset_url(self):
        path = 'dac/csio/2902746/profiles/BR2902746_001.nc'
        url = 'https://data-argo.ifremer.fr/' + path
        self.assertIsInstance(read_nc_profile(url)._dataset, Dataset)

    def test_dataset_dataset(self):
        ds = Dataset(resource_path('BR2902746_001.nc'))
        self.assertIs(read_nc_profile(ds)._dataset, ds)

    def test_dataset_unknown(self):
        with self.assertRaises(ValueError):
            read_nc_profile('this is not anything')


if __name__ == '__main__':
    unittest.main()
