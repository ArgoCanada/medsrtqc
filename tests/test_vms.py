
import unittest
from io import BytesIO

from medsrtqc.resources import resource_path
import medsrtqc.vms.enc as enc
import medsrtqc.vms.read as read
from medsrtqc.vms.core_impl import VMSProfile, VMSProfileList, Trace


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

    def test_read(self):
        test_file = resource_path('BINARY_VMS.DAT')

        profiles = read.read_vms_profiles(test_file)
        self.assertEqual(len(profiles), 2)
        self.assertIsInstance(profiles, VMSProfileList)

        profile_count = 0
        for profile in profiles:
            self.assertIsInstance(profile, VMSProfile)
            for name, trace in profile.items():
                self.assertIsInstance(name, str)
                self.assertIsInstance(trace, Trace)
            profile_count += 1

        self.assertEqual(profile_count, len(profiles))

        with open(test_file, 'rb') as f:
            self.assertEqual(profiles._data, read.read_vms_profiles(f)._data)

        size_calc = read._file_encoding.sizeof(profiles._data)
        with open(test_file, 'rb') as f:
            self.assertEqual(size_calc, len(f.read()))


if __name__ == '__main__':
    unittest.main()
