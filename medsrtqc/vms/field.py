
from io import BytesIO
from typing import BinaryIO, Iterable
from struct import pack, unpack, calcsize
from collections import OrderedDict


class VMSField:
    """A base class for binary encoding and decoding of VMS fields"""

    def n_bytes(self, value=None):
        """The size of the field in bytes"""
        raise NotImplementedError()

    def from_stream(self, file: BinaryIO, value=None):
        """Read from a file object and return a Python object"""
        raise NotImplementedError()

    def to_stream(self, file: BinaryIO, value):
        """Encode a Python object and send it to a file object"""
        raise NotImplementedError()


class VMSPadding(VMSField):
    """A field to explicitly encode padding bytes in structure definitions"""

    def __init__(self, length) -> None:
        self._length = length

    def n_bytes(self, value=None):
        return self._length

    def from_stream(self, file: BinaryIO, value=None):
        file.read(self._length)
        return None

    def to_stream(self, file: BinaryIO, value=None):
        file.write(b'\x00' * self._length)


class VMSCharacter(VMSField):
    """A field to encode strings as fixed-length character fields"""

    def __init__(self, length, encoding='utf-8', pad=b'\x00'):
        self._length = length
        self._encoding = encoding
        self._pad = pad

    def n_bytes(self, value=None):
        return self._length

    def from_stream(self, file: BytesIO, value=None) -> str:
        encoded = file.read(self._length).rstrip(self._pad)
        return encoded.decode(self._encoding)

    def to_stream(self, file: BytesIO, value):
        encoded = str(value).encode(self._encoding)
        if len(encoded) <= self._length:
            file.write(encoded.ljust(self._length, self._pad))
        else:
            msg = f"Can't convert '{value}' to '{self._encoding}' of <= {self._length} bytes"
            raise ValueError(msg)


class VMSArrayOf(VMSField):
    """An array field containing zero or more values from another field"""

    def __init__(self, field: VMSField, max_length) -> None:
        self._field = field
        self._max_length = max_length

    def n_bytes(self, value):
        return self._field.n_bytes() * len(value)

    def from_stream(self, file: BinaryIO, value: list) -> list:
        for i in range(len(value)):
            value[i] = self._field.from_stream(file)
        return value

    def to_stream(self, file: BinaryIO, value: Iterable):
        if (len(value) > self._max_length):
            raise ValueError(f'len(value) greater than allowed max length ({self._max_length})')
        for item in value:
            self._field.to_stream(file, item)


class VMSStructField(VMSField):
    """A struct field containing named values of other field types"""

    def __init__(self, *fields) -> None:
        self._fields = OrderedDict()
        n_pad = 0
        for item in fields:
            if isinstance(item, VMSPadding):
                name = '__vms_padding_' + str(n_pad)
                field = item
                n_pad += 1
            else:
                name, field = item

            self._fields[name] = field

    def n_bytes(self, value=None):
        return sum(field.n_bytes() for field in self._fields.values())

    def from_stream(self, file: BinaryIO, value=None):
        if value is None:
            value = OrderedDict()
        for name, field in self._fields.items():
            if isinstance(field, VMSPadding):
                field.from_stream(file)
            else:
                value[name] = field.from_stream(file)
        return value

    def to_stream(self, file: BinaryIO, value):
        for name, field in self._fields.items():
            if name in value:
                field.to_stream(file, value[name])
            else:
                field.to_stream(file)


class VMSPythonStructField(VMSField):
    """
    A field that encodes and decodes binary data using a Python struct
    module format string
    """

    def __init__(self, format) -> None:
        self._format = format

    def n_bytes(self):
        return calcsize(self._format)

    def from_stream(self, file: BinaryIO):
        return unpack(self._format, file.read(self.n_bytes()))[0]

    def to_stream(self, file: BinaryIO, value):
        file.write(pack(self._format, value))


class VMSInteger2(VMSPythonStructField):
    """A 16-bit signed big-endian integer field"""

    def __init__(self) -> None:
        super().__init__('>h')

    def to_stream(self, file: BinaryIO, value):
        return super().to_stream(file, int(value))


class VMSInteger4(VMSPythonStructField):
    """A 32-bit signed big-endian integer field"""

    def __init__(self) -> None:
        super().__init__('>i')

    def to_stream(self, file: BinaryIO, value):
        return super().to_stream(file, int(value))


class VMSReal4BigEndian(VMSPythonStructField):
    """A 32-bit big-endian float value"""

    def __init__(self) -> None:
        super().__init__('>f')

    def to_stream(self, file: BinaryIO, value):
        return super().to_stream(file, float(value))


class VMSReal4(VMSField):
    """A 32-bit middle-endian VAX/VMS-encoded float value"""

    def n_bytes(self, value=None):
        return 4

    def to_stream(self, file: BinaryIO, value):
        float_value_big_endian = pack('>f', float(value))
        for i in [2, 3, 0, 1]:
            file.write(float_value_big_endian[i:(i + 1)])

    def from_stream(self, file: BinaryIO, value=None) -> float:
        float_value_mid_endian = file.read(4)
        float_value_big_endian = bytearray(4)
        for i_out, i_in in enumerate([2, 3, 0, 1]):
            float_value_big_endian[i_out] = float_value_mid_endian[i_in]
        return unpack('>f', float_value_big_endian)[0]
