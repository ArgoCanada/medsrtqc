
import unittest
from io import BytesIO
import os
import tempfile

import numpy as np

from medsrtqc.resources import resource_path
import medsrtqc.vms.enc as enc
import medsrtqc.vms.read as read
from medsrtqc.core import Trace
from medsrtqc.vms.core_impl import VMSProfile


class TestEncoding(unittest.TestCase):

    def test_padding(self):
        f = enc.Padding(3)
        self.assertEqual(f.sizeof(), 3)
        file = BytesIO()
        f.encode(file, None)
        self.assertEqual(file.getvalue(), b'\x00\x00\x00')
        self.assertEqual(f.decode(BytesIO(b'\x00\x00\x00')), None)

    def test_character(self):
        f = enc.Character(5)
        self.assertEqual(f.sizeof(), 5)
        file = BytesIO()
        f.encode(file, 'abcd')
        self.assertEqual(file.getvalue(), b'abcd ')
        self.assertEqual(f.decode(BytesIO(b'abcd ')), 'abcd')
        with self.assertRaises(ValueError):
            f.encode(file, '123456')

    def test_struct(self):
        f = enc.StructEncoding(
            ('name1', enc.Character(3)),
            enc.Padding(1),
            ('name2', enc.Character(4))
        )
        self.assertEqual(f.sizeof(), 8)
        file = BytesIO()
        f.encode(file, {'name1': 'abc', 'name2': 'abcd'})
        self.assertEqual(file.getvalue(), b'abc\x00abcd')
        self.assertEqual(
            f.decode(BytesIO(b'abc\x00abcd')),
            {'name1': 'abc', 'name2': 'abcd'}
        )

    def test_array(self):
        f = enc.ArrayOf(enc.Character(5), max_length=10)
        self.assertEqual(f.sizeof([None]), 5)
        file = BytesIO()
        f.encode(file, ['abcd'])
        self.assertEqual(file.getvalue(), b'abcd ')
        # test determinate length and indeterminate length
        self.assertEqual(f.decode(BytesIO(b'abcd '), [None]), ['abcd'])
        self.assertEqual(f.decode(BytesIO(b'abcd ')), ['abcd'])

        with self.assertRaises(ValueError):
            f.encode(file, ['abcd'] * 11)

    def test_python_struct(self):
        f = enc.PythonStructEncoding('>h')
        self.assertEqual(f.sizeof(), 2)
        file = BytesIO()
        f.encode(file, 16)
        self.assertEqual(file.getvalue(), b'\x00\x10')
        self.assertEqual(f.decode(BytesIO(b'\x00\x10')), 16)

    def test_integer2(self):
        f = enc.Integer2()
        self.assertEqual(f.sizeof(), 2)
        file = BytesIO()
        f.encode(file, 16)
        self.assertEqual(file.getvalue(), b'\x10\x00')
        self.assertEqual(f.decode(BytesIO(b'\x10\x00')), 16)

    def test_integer4(self):
        f = enc.Integer4()
        self.assertEqual(f.sizeof(), 4)
        file = BytesIO()
        f.encode(file, 16)
        self.assertEqual(file.getvalue(), b'\x10\x00\x00\x00')
        self.assertEqual(f.decode(BytesIO(b'\x10\x00\x00\x00')), 16)

    def test_real4(self):
        f = enc.Real4()
        self.assertEqual(f.sizeof(), 4)
        file = BytesIO()
        f.encode(file, 99.9999008178711)
        self.assertEqual(file.getvalue(), b'\xc7C\xf3\xff')
        self.assertEqual(f.decode(BytesIO(b'\xc7C\xf3\xff')), 99.9999008178711)


class TestVMSRead(unittest.TestCase):

    def test_vms_profile(self):
        test_file = resource_path('BINARY_VMS.DAT')

        profiles = read.read_vms_profiles(test_file)
        self.assertEqual(len(profiles), 2)
        self.assertIsInstance(profiles, list)

        for p in profiles:
            self.assertIsInstance(p, VMSProfile)

        self.assertIsInstance(profiles[0], VMSProfile)
        self.assertIsInstance(profiles[1], VMSProfile)

        profile_count = 0
        for profile in profiles:
            self.assertIsInstance(profile, VMSProfile)
            for name, trace in profile.items():
                self.assertIsInstance(name, str)
                self.assertIsInstance(trace, Trace)
            profile_count += 1

        self.assertEqual(profile_count, len(profiles))

        # make sure the 'PRES' export works (because it isn't stored
        # separately but is copied with each parameter)
        self.assertTrue('PRES' in profiles[0])
        self.assertTrue(np.all(profiles[0]['TEMP'].pres == profiles[0]['PRES'].value))

    def test_vms_profile_update(self):
        test_file = resource_path('BINARY_VMS.DAT')
        profiles = read.read_vms_profiles(test_file)
        prof = profiles[0]

        # valid update of not PRES QC
        temp = prof['TEMP']
        temp.qc[:] = b'4'
        prof['TEMP'] = temp
        self.assertTrue(np.all(prof['TEMP'].qc == b'4'))

        # valid update of PRES QC
        pres = prof['PRES']
        pres.qc[:] = b'4'
        prof['PRES'] = pres
        self.assertTrue(np.all(prof['PRES'].qc == b'4'))

        # attempt to update non-qc attrs
        with self.assertRaises(ValueError):
            temp = prof['TEMP']
            temp.value[:] = 0
            prof['TEMP'] = temp
        with self.assertRaises(ValueError):
            temp = prof['TEMP']
            temp.adjusted[:] = 0
            prof['TEMP'] = temp
        with self.assertRaises(ValueError):
            temp = prof['TEMP']
            temp.adjusted_qc[:] = b'4'
            prof['TEMP'] = temp
        with self.assertRaises(ValueError):
            temp = prof['TEMP']
            temp.pres[:] = 0
            prof['TEMP'] = temp
        with self.assertRaises(ValueError):
            temp = prof['TEMP']
            temp.mtime[:] = 0
            prof['TEMP'] = temp

    def test_vms_profile_update_adjusted(self):
        # load a bgc VMS file (source files from coriolis)
        profs = read.read_vms_profiles(resource_path('bgc_vms.dat'))
        prof = profs[0]

        chla_trace = prof["FLU1"]

        chla_trace.qc[0] = b'5'
        prof["FLU1"] = chla_trace

        chla_trace.adjusted = chla_trace.value

        prof["FLU1"] = chla_trace
        chla_trace_updated = prof["FLU1"]
        self.assertTrue(np.all(chla_trace_updated.adjusted == chla_trace.value))

    def test_read_write(self):
        with self.assertRaises(TypeError):
            read.read_vms_profiles(None)

        with self.assertRaises(TypeError):
            read.write_vms_profiles(None, None)

        test_file = resource_path('BINARY_VMS.DAT')
        profiles = read.read_vms_profiles(test_file)

        with self.assertRaises(TypeError):
            read.write_vms_profiles(profiles, None)

        with open(test_file, 'rb') as f:
            for i, prof in enumerate(read.read_vms_profiles(f)):
                self.assertEqual(prof._data, profiles[i]._data)

        size_calc = read._file_encoding.sizeof([item._data for item in profiles])
        with open(test_file, 'rb') as f:
            content = f.read()
            self.assertEqual(size_calc, len(content))
            written_content = BytesIO()
            read.write_vms_profiles(profiles, written_content)
            self.assertEqual(written_content.getvalue(), content)

            fd, tmp = tempfile.mkstemp()
            try:
                with open(tmp, 'wb') as fw:
                    read.write_vms_profiles(profiles, tmp)
                with open(tmp, 'rb') as fw:
                    self.assertEqual(fw.read(), content)
            finally:
                os.close(fd)
                os.unlink(tmp)


if __name__ == '__main__':
    unittest.main()
