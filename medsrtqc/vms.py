
class VMSFieldType:

    def n_bytes(self):
        pass

    def from_bytes(self, obj: bytes):
        pass

    def to_bytes(self, obj) -> bytes:
        pass


class VMSCharacter(VMSFieldType):

    def __init__(self, length, encoding='utf-8', pad=b' '):
        self._length = length
        self._encoding = encoding
        self._pad = pad

    def n_bytes(self):
        return self._length

    def from_bytes(self, obj: bytes):
        return obj.decode(self._encoding)

    def to_bytes(self, obj) -> bytes:
        encoded = str(obj).encode(self._encoding)
        if len(encoded) <= self._length:
            encoded.ljust(self._length, self._pad)
        else:
            msg = f"Can't convert '{obj}' to '{self._encoding}' of <= {self._length} bytes"
            raise ValueError(msg)


class VMSInteger2(VMSFieldType):
    pass


class VMSInteger4(VMSFieldType):
    pass


class VMSFloat4(VMSFieldType):
    pass


class VMSStruct(VMSFieldType):
    pass


class OceanProcessingProfile(VMSStruct):
    pass
