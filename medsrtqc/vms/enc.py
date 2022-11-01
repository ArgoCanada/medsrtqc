
"""
The classes in the ``vms.enc`` module are the basis on
which the high-level structure definitions are based and are
normally not used interactively; however, they may be used
to discover the format or debug the reading of files.
The built-in types mostly use the Python ``struct``
module to encode and decode values.

>>> from io import BytesIO
>>> medsrtqc.vms.enc import *
>>> buf = BytesIO()
>>> encoding = StructEncoding(('f1', Character(4)), ('f2': Integer2()))
>>> encoding.encode(buf, {'f1': 'abc', 'f2': 0})
>>> buf.getvalue()
b'abc \\x00\\x00'
>>> buf.seek(0)
0
>>> encoding.decode(buf)
OrderedDict([('f1', 'abc'), ('f2', 0)])
"""


from io import BytesIO
from typing import BinaryIO, Iterable
from struct import pack, unpack, calcsize
from collections import OrderedDict


class Encoding:  # pragma: no cover
    """A base class for binary encoding and decoding values"""

    def sizeof(self, value=None):
        """
        The number of bytes that :meth:`decode` will write to `file`
        when called
        """
        raise NotImplementedError()

    def decode(self, file: BinaryIO, value=None):
        """Read from a file object and return a Python object"""
        raise NotImplementedError()

    def encode(self, file: BinaryIO, value):
        """Encode a Python object and send it to a file object"""
        raise NotImplementedError()


class Padding(Encoding):
    """Explicitly encode padding bytes in structure definitions"""

    def __init__(self, length) -> None:
        self._length = length

    def sizeof(self, value=None):
        return self._length

    def decode(self, file: BinaryIO, value=None):
        file.read(self._length)
        return None

    def encode(self, file: BinaryIO, value=None):
        file.write(b'\x00' * self._length)

class LineEnding(Encoding):
    """Explicitly encode carriage returns in structure definitions"""

    def sizeof(self):
        return 2

    def decode(self, file: BinaryIO, value=None):
        file.read(2)
        return None
    
    def encode(self, file: BinaryIO, value=None):
        file.write(b'\r\n')


class Character(Encoding):
    """
    A fixed-length character encoding. A fixed length
    is enforced by adding a padding character to the
    right of the string.
    """

    def __init__(self, length, encoding='utf-8', pad=b' '):
        self._length = length
        self._encoding = encoding
        self._pad = pad

    def sizeof(self, value=None):
        return self._length

    def decode(self, file: BytesIO, value=None) -> str:
        encoded = file.read(self._length).rstrip(self._pad)
        init_size = len(encoded)
        encoded = encoded.replace(b'\r\n', b'')
        diff = init_size - len(encoded)
        while diff > 0 and encoded != b'':
            encoded += file.read(diff).replace(b'\r\n', b'')
            diff = init_size - len(encoded)
        return encoded.decode(self._encoding)

    def encode(self, file: BytesIO, value):
        encoded = value if isinstance(value, bytes) else str(value).encode(self._encoding)
        if len(encoded) <= self._length:
            file.write(encoded.ljust(self._length, self._pad))
        else:
            msg = f"Can't convert '{value}' to '{self._encoding}' of <= {self._length} bytes"
            raise ValueError(msg)


class ArrayOf(Encoding):
    """An array of some other encoding"""

    def __init__(self, Encoding: Encoding, max_length=None) -> None:
        self._encoding = Encoding
        self._max_length = max_length

    def sizeof(self, value):
        size = 0
        for item in value:
            size += self._encoding.sizeof(item)
        return size

    def decode(self, file: BinaryIO, value=None) -> list:
        # If we don't know how many to expect, read until
        # the end of the file. This requires that `file`
        # is seekable which should not be a problem in practice
        if value is None:
            value = []
            peek1 = b'\x00'
            peek3 = b'\x00'
            while len(peek1) > 0 and len(peek3) > 0:
                value.append(self._encoding.decode(file))
                current_loc = file.tell()
                peek1 = file.read(1)
                if peek1 == b'\r':
                    peek2 = file.read(1)
                    if peek2 == b'\n':
                        peek3 = file.read(1)
                file.seek(current_loc)
        else:
            # if we know exactly how may to expect, read that
            for i in range(len(value)):
                value[i] = self._encoding.decode(file)

        return value

    def encode(self, file: BinaryIO, value: Iterable):
        if self._max_length is not None and len(value) > self._max_length:
            raise ValueError(f'len(value) greater than allowed max length ({self._max_length})')
        for item in value:
            self._encoding.encode(file, item)


class StructEncoding(Encoding):
    """A struct containing named values of other encodings"""

    def __init__(self, *encodings) -> None:
        self._encodings = OrderedDict()
        n_pad = 0
        n_eol = 0
        for item in encodings:
            if isinstance(item, Padding):
                name = '___padding_' + str(n_pad)
                encoding = item
                n_pad += 1
            elif isinstance(item, LineEnding):
                name = '___lineending_' + str(n_eol)
                encoding = item
                n_eol += 1
            else:
                name, encoding = item

            self._encodings[name] = encoding

    def sizeof(self, value=None):
        if value is None:
            value = {key: None for key in self._encodings.keys()}

        size = 0
        for key in self._encodings.keys():
            size += self._encodings[key].sizeof(value[key])
        return size

    def decode(self, file: BinaryIO, value=None):
        if value is None:
            value = OrderedDict()
        for name, encoding in self._encodings.items():
            if isinstance(encoding, Padding) or isinstance(encoding, LineEnding):
                encoding.decode(file)
            else:
                value[name] = encoding.decode(file)
        return value

    def encode(self, file: BinaryIO, value):
        for name, Encoding in self._encodings.items():
            
            if name == 'PR_PROFILE':
                if Encoding._encoding._ver == 'win':
                    print('\\r\\n')
                    LineEnding().encode(file)

            if name not in ['DEPTH_PRESS', 'DP_FLAG', 'PARM', 'Q_PARM']:
                print(name, Encoding)

            if name in value:
                Encoding.encode(file, value[name])
            else:
                Encoding.encode(file)

            if name == 'PROF':
                if Encoding._encoding._prof == 'PrProfile' and Encoding._encoding._ver == 'win':
                    print('\\r\\n')
                    LineEnding().encode(file)


class PythonStructEncoding(Encoding):
    """
    Encode and decode binary data using a Python struct
    module format string
    """

    def __init__(self, format) -> None:
        self._format = format

    def sizeof(self, value=None):
        return calcsize(self._format)

    def decode(self, file: BinaryIO):
        return unpack(self._format, file.read(self.sizeof()))[0]

    def encode(self, file: BinaryIO, value):
        file.write(pack(self._format, value))


class Integer2(PythonStructEncoding):
    """A 16-bit signed little-endian integer encoding"""

    def __init__(self) -> None:
        super().__init__('<h')

    def encode(self, file: BinaryIO, value):
        return super().encode(file, int(value))


class Integer4(PythonStructEncoding):
    """A 32-bit signed little-endian integer encoding"""

    def __init__(self) -> None:
        super().__init__('<i')

    def encode(self, file: BinaryIO, value):
        return super().encode(file, int(value))


class Real4(Encoding):
    """A 32-bit middle-endian VAX/-encoded float value"""

    def sizeof(self, value=None):
        return 4

    def encode(self, file: BinaryIO, value):
        float_value_big_endian = pack('>f', float(value))
        # we need to force bit 24 to be a 1 before encoding as a mid-endian float
        float_value_big_endian = pack('>l', unpack('>l', float_value_big_endian)[0] + 2 ** 24)

        float_value_mid_endian = bytearray(4)
        for i_out, i_in in enumerate([1, 0, 3, 2]):
            float_value_mid_endian[i_out] = float_value_big_endian[i_in]

        file.write(float_value_mid_endian)

    def decode(self, file: BinaryIO, value=None) -> float:
        float_value_mid_endian = file.read(4)
        float_value_big_endian = bytearray(4)
        for i_out, i_in in enumerate([1, 0, 3, 2]):
            float_value_big_endian[i_out] = float_value_mid_endian[i_in]
        # we need to zero-out bit 24 before interpreting as a big-endian float
        float_value_big_endian = pack('>l', unpack('>l', float_value_big_endian)[0] - 2 ** 24)
        return unpack('>f', float_value_big_endian)[0]
