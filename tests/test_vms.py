
import unittest
from io import BytesIO
import medsrtqc.vms.enc as enc

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
        self.assertEqual(f.decode(BytesIO(b'abcd '), [None]), ['abcd'])

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


if __name__ == '__main__':
    unittest.main()
