
from io import BytesIO
from typing import BinaryIO
from struct import pack, unpack, calcsize
from collections import OrderedDict


class VMSField:

    def n_bytes(self):
        raise NotImplementedError()

    def from_stream(self, file: BinaryIO):
        raise NotImplementedError()

    def to_stream(self, file: BinaryIO, value):
        raise NotImplementedError()


class VMSPadding(VMSField):

    def __init__(self, length) -> None:
        self._length = length

    def n_bytes(self):
        return self._length

    def from_stream(self, file: BinaryIO):
        file.read(self._length)
        return None

    def to_stream(self, file: BinaryIO, value=None):
        file.write(b'\x00' * self._length)


class VMSCharacter(VMSField):

    def __init__(self, length, encoding='utf-8', pad=b'\x00'):
        self._length = length
        self._encoding = encoding
        self._pad = pad

    def n_bytes(self):
        return self._length

    def from_stream(self, file: BytesIO):
        encoded = file.read(self._length).rstrip(self._pad)
        return encoded.decode(self._encoding)

    def to_stream(self, file: BytesIO, value) -> bytes:
        encoded = str(value).encode(self._encoding)
        if len(encoded) <= self._length:
            file.write(encoded.ljust(self._length, self._pad))
        else:
            msg = f"Can't convert '{value}' to '{self._encoding}' of <= {self._length} bytes"
            raise ValueError(msg)


class VMSStruct(VMSField):

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

    def n_bytes(self):
        return sum(field.n_bytes() for field in self._fields.values())

    def from_stream(self, file: BinaryIO):
        result = OrderedDict()
        for name, field in self._fields.items():
            if isinstance(field, VMSPadding):
                field.from_stream(file)
            else:
                result[name] = field.from_stream(file)
        return result

    def to_stream(self, file: BinaryIO, value):
        for name, field in self._fields.items():
            if name in value:
                field.to_stream(file, value[name])
            else:
                field.to_stream(file)


class VMSPythonStructField(VMSField):

    def __init__(self, format) -> None:
        self._format = format

    def n_bytes(self):
        return calcsize(self._format)

    def from_stream(self, file: BinaryIO):
        return unpack(self._format, file.read(self.n_bytes()))[0]

    def to_stream(self, file: BinaryIO, value):
        file.write(pack(self._format, value))


class VMSInteger2(VMSPythonStructField):
    def __init__(self) -> None:
        super().__init__('>h')


class VMSInteger4(VMSPythonStructField):
    def __init__(self) -> None:
        super().__init__('>i')


class VMSReal4(VMSPythonStructField):
    def __init__(self) -> None:
        super().__init__('>f')


class VMSOceanProcessingProfileType(VMSStruct):
    pass
