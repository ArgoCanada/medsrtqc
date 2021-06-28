
import unittest
from io import BytesIO
from medsrtqc import vms

class TestVMSField(unittest.TestCase):

    def test_padding(self):
        field = vms.VMSPadding(3)
        self.assertEqual(field.n_bytes(), 3)
        file = BytesIO()
        field.to_stream(file, None)
        self.assertEqual(file.getvalue(), b'\x00\x00\x00')
        self.assertEqual(field.from_stream(BytesIO(b'\x00\x00\x00')), None)

    def test_character(self):
        field = vms.VMSCharacter(5)
        self.assertEqual(field.n_bytes(), 5)
        file = BytesIO()
        field.to_stream(file, 'abcd')
        self.assertEqual(file.getvalue(), b'abcd\x00')
        self.assertEqual(field.from_stream(BytesIO(b'abcd\x00')), 'abcd')

    def test_struct(self):
        field = vms.VMSStruct(
            ('name1', vms.VMSCharacter(3)),
            vms.VMSPadding(1),
            ('name2', vms.VMSCharacter(4))
        )
        self.assertEqual(field.n_bytes(), 8)
        file = BytesIO()
        field.to_stream(file, {'name1': 'abc', 'name2': 'abcd'})
        self.assertEqual(file.getvalue(), b'abc\x00abcd')
        self.assertEqual(field.from_stream(BytesIO(b'abc\x00abcd')), {'name1': 'abc', 'name2': 'abcd'})

    def test_python_struct(self):
        field = vms.VMSPythonStructFieldType('>h')
        self.assertEqual(field.n_bytes(), 2)
        file = BytesIO()
        field.to_stream(file, 16)
        self.assertEqual(file.getvalue(), b'\x00\x10')
        self.assertEqual(field.from_stream(BytesIO(b'\x00\x10')), 16)
    
    def test_integer2(self):
        field = vms.VMSInteger2()
        self.assertEqual(field.n_bytes(), 2)
        file = BytesIO()
        field.to_stream(file, 16)
        self.assertEqual(file.getvalue(), b'\x00\x10')
        self.assertEqual(field.from_stream(BytesIO(b'\x00\x10')), 16)
    
    def test_integer4(self):
        field = vms.VMSInteger4()
        self.assertEqual(field.n_bytes(), 4)
        file = BytesIO()
        field.to_stream(file, 16)
        self.assertEqual(file.getvalue(), b'\x00\x00\x00\x10')
        self.assertEqual(field.from_stream(BytesIO(b'\x00\x00\x00\x10')), 16)

    def test_float4(self):
        field = vms.VMSFloat4()
        self.assertEqual(field.n_bytes(), 4)
        file = BytesIO()
        field.to_stream(file, 1)
        self.assertEqual(file.getvalue(), b'?\x80\x00\x00')
        self.assertEqual(field.from_stream(BytesIO(b'?\x80\x00\x00')), 1)


class TestOceanProcessingProfile(unittest.TestCase):

    def test_profile(self):
        prof = vms.VMSOceanProcessingProfileType()
        self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main()
