
from io import BytesIO
from typing import BinaryIO, Iterable
from struct import pack, unpack, calcsize
from collections import OrderedDict


class VMSEncoding:
    """A base class for binary encoding and decoding of field values"""

    def sizeof(self, value=None):
        """The size of the Encoding in bytes"""
        raise NotImplementedError()

    def decode(self, file: BinaryIO, value=None):
        """Read from a file object and return a Python object"""
        raise NotImplementedError()

    def encode(self, file: BinaryIO, value):
        """Encode a Python object and send it to a file object"""
        raise NotImplementedError()


class VMSPadding(VMSEncoding):
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


class VMSCharacter(VMSEncoding):
    """Fixed-length character encodings"""

    def __init__(self, length, encoding='utf-8', pad=b' '):
        self._length = length
        self._encoding = encoding
        self._pad = pad

    def sizeof(self, value=None):
        return self._length

    def decode(self, file: BytesIO, value=None) -> str:
        encoded = file.read(self._length).rstrip(self._pad)
        return encoded.decode(self._encoding)

    def encode(self, file: BytesIO, value):
        encoded = str(value).encode(self._encoding)
        if len(encoded) <= self._length:
            file.write(encoded.ljust(self._length, self._pad))
        else:
            msg = f"Can't convert '{value}' to '{self._encoding}' of <= {self._length} bytes"
            raise ValueError(msg)


class VMSArrayOf(VMSEncoding):
    """An array of some other encoding"""

    def __init__(self, Encoding: VMSEncoding, max_length) -> None:
        self._Encoding = Encoding
        self._max_length = max_length

    def sizeof(self, value):
        return self._Encoding.sizeof() * len(value)

    def decode(self, file: BinaryIO, value: list) -> list:
        for i in range(len(value)):
            value[i] = self._Encoding.decode(file)
        return value

    def encode(self, file: BinaryIO, value: Iterable):
        if (len(value) > self._max_length):
            raise ValueError(f'len(value) greater than allowed max length ({self._max_length})')
        for item in value:
            self._Encoding.encode(file, item)


class VMSStructEncoding(VMSEncoding):
    """A struct containing named values of other encodings"""

    def __init__(self, *Encodings) -> None:
        self._Encodings = OrderedDict()
        n_pad = 0
        for item in Encodings:
            if isinstance(item, VMSPadding):
                name = '__vms_padding_' + str(n_pad)
                Encoding = item
                n_pad += 1
            else:
                name, Encoding = item

            self._Encodings[name] = Encoding

    def sizeof(self, value=None):
        return sum(Encoding.sizeof() for Encoding in self._Encodings.values())

    def decode(self, file: BinaryIO, value=None):
        if value is None:
            value = OrderedDict()
        for name, Encoding in self._Encodings.items():
            if isinstance(Encoding, VMSPadding):
                Encoding.decode(file)
            else:
                value[name] = Encoding.decode(file)
        return value

    def encode(self, file: BinaryIO, value):
        for name, Encoding in self._Encodings.items():
            if name in value:
                Encoding.encode(file, value[name])
            else:
                Encoding.encode(file)


class VMSPythonStructEncoding(VMSEncoding):
    """
    Encode and decode binary data using a Python struct
    module format string
    """

    def __init__(self, format) -> None:
        self._format = format

    def sizeof(self):
        return calcsize(self._format)

    def decode(self, file: BinaryIO):
        return unpack(self._format, file.read(self.sizeof()))[0]

    def encode(self, file: BinaryIO, value):
        file.write(pack(self._format, value))


class VMSInteger2(VMSPythonStructEncoding):
    """A 16-bit signed little-endian integer encoding"""

    def __init__(self) -> None:
        super().__init__('<h')

    def encode(self, file: BinaryIO, value):
        return super().encode(file, int(value))


class VMSInteger4(VMSPythonStructEncoding):
    """A 32-bit signed little-endian integer encoding"""

    def __init__(self) -> None:
        super().__init__('<i')

    def encode(self, file: BinaryIO, value):
        return super().encode(file, int(value))


class VMSReal4BigEndian(VMSPythonStructEncoding):
    """A 32-bit big-endian float value"""

    def __init__(self) -> None:
        super().__init__('>f')

    def encode(self, file: BinaryIO, value):
        return super().encode(file, float(value))


class VMSReal4(VMSEncoding):
    """A 32-bit middle-endian VAX/VMS-encoded float value"""

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
