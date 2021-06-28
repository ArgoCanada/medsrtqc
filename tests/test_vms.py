
import unittest
from io import BytesIO
from medsrtqc.vms import field

class TestVMSField(unittest.TestCase):

    def test_padding(self):
        f = field.VMSPadding(3)
        self.assertEqual(f.n_bytes(), 3)
        file = BytesIO()
        f.to_stream(file, None)
        self.assertEqual(file.getvalue(), b'\x00\x00\x00')
        self.assertEqual(f.from_stream(BytesIO(b'\x00\x00\x00')), None)

    def test_character(self):
        f = field.VMSCharacter(5)
        self.assertEqual(f.n_bytes(), 5)
        file = BytesIO()
        f.to_stream(file, 'abcd')
        self.assertEqual(file.getvalue(), b'abcd\x00')
        self.assertEqual(f.from_stream(BytesIO(b'abcd\x00')), 'abcd')

    def test_struct(self):
        f = field.VMSStructField(
            ('name1', field.VMSCharacter(3)),
            field.VMSPadding(1),
            ('name2', field.VMSCharacter(4))
        )
        self.assertEqual(f.n_bytes(), 8)
        file = BytesIO()
        f.to_stream(file, {'name1': 'abc', 'name2': 'abcd'})
        self.assertEqual(file.getvalue(), b'abc\x00abcd')
        self.assertEqual(f.from_stream(BytesIO(b'abc\x00abcd')), {'name1': 'abc', 'name2': 'abcd'})

    def test_array(self):
        f = field.VMSArrayOf(field.VMSCharacter(5), max_length=10)
        self.assertEqual(f.n_bytes([None]), 5)
        file = BytesIO()
        f.to_stream(file, ['abcd'])
        self.assertEqual(file.getvalue(), b'abcd\x00')
        self.assertEqual(f.from_stream(BytesIO(b'abcd\x00'), [None]), ['abcd'])

    def test_python_struct(self):
        f = field.VMSPythonStructField('>h')
        self.assertEqual(f.n_bytes(), 2)
        file = BytesIO()
        f.to_stream(file, 16)
        self.assertEqual(file.getvalue(), b'\x00\x10')
        self.assertEqual(f.from_stream(BytesIO(b'\x00\x10')), 16)

    def test_integer2(self):
        f = field.VMSInteger2()
        self.assertEqual(f.n_bytes(), 2)
        file = BytesIO()
        f.to_stream(file, 16)
        self.assertEqual(file.getvalue(), b'\x00\x10')
        self.assertEqual(f.from_stream(BytesIO(b'\x00\x10')), 16)

    def test_integer4(self):
        f = field.VMSInteger4()
        self.assertEqual(f.n_bytes(), 4)
        file = BytesIO()
        f.to_stream(file, 16)
        self.assertEqual(file.getvalue(), b'\x00\x00\x00\x10')
        self.assertEqual(f.from_stream(BytesIO(b'\x00\x00\x00\x10')), 16)

    def test_real4(self):
        f = field.VMSReal4()
        self.assertEqual(f.n_bytes(), 4)
        file = BytesIO()
        f.to_stream(file, 1)
        self.assertEqual(file.getvalue(), b'?\x80\x00\x00')
        self.assertEqual(f.from_stream(BytesIO(b'?\x80\x00\x00')), 1)


class TestOceanProcessingProfile(unittest.TestCase):

    def test_profile(self):
        self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main()
