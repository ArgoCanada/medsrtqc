
import unittest
import os
import tempfile
import numpy as np
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

    def test_empty(self):
        profile = read_nc_profile()
        self.assertEqual(profile.keys(), ())

    def test_strip_trail(self):
        profile = read_nc_profile(resource_path('BR6904117_085.nc'))
        # all values are finite
        self.assertEqual(len(profile['CHLA']), 1273)
        # trim trailing values
        self.assertEqual(len(profile['DOXY']), 516)

    def test_uv_intensity_nitrate(self):
        # UV_INTENSITY_NITRATE is special because its value has two
        # dimensions; however, its QC attribute only has one dimension
        # for both, the len() is the same, so this is used to validate
        profile = read_nc_profile(resource_path('BR6904117_085.nc'))
        nitrate = profile['UV_INTENSITY_NITRATE']
        self.assertIsInstance(nitrate, Trace)
        self.assertEqual(nitrate._shape, (117, 90))
        self.assertEqual(len(nitrate), 117)

    def test_set_value(self):
        try:
            # make writable copy
            fd, tmp = tempfile.mkstemp()
            nc = resource_path('BR6904117_085.nc')
            with open(tmp, 'wb') as dst, open(nc, 'rb') as src:
                dst.write(src.read())
            prof = read_nc_profile(tmp, mode='r+')

            # change something
            chla = prof['CHLA']
            chla.value[:] = 1
            prof['CHLA'] = chla

            # see if it sticks
            self.assertTrue(np.all(prof['CHLA'].value == 1))

            # write to disk
            prof.close()

            # see if it stuck for good
            prof = read_nc_profile(tmp)
            self.assertTrue(np.all(prof['CHLA'].value == 1))
        finally:
            os.close(fd)

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
        path = 'dac/coriolis/6904117/profiles/BD6904117_085.nc'
        url = 'https://data-argo.ifremer.fr/' + path
        self.assertIsInstance(read_nc_profile(url)._datasets[0], Dataset)

    def test_dataset_dataset(self):
        ds = Dataset(resource_path('BR6904117_085.nc'))
        self.assertIs(read_nc_profile(ds)._datasets[0], ds)

    def test_dataset_unknown(self):
        with self.assertRaises(ValueError):
            read_nc_profile('this is not anything')

    def test_dataset_bad_type(self):
        with self.assertRaises(TypeError):
            read_nc_profile(None)


if __name__ == '__main__':
    unittest.main()
