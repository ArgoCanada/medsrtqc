
from typing import BinaryIO
from struct import pack, unpack


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

class Float(Encoding):
    """Double precision float value"""

    def sizeof(self, value=None):
        return 4

    def encode(self, file: BinaryIO, value):

        float_value_big_endian = pack('>f', float(value))
        # we need to force bit 24 to be a 1 before encoding as a mid-endian float
        float_value_big_endian = pack('>l', unpack('>l', float_value_big_endian)[0] + 2 ** 24)
        # swap the byte order
        float_value_little_endian = bytes(reversed(float_value_big_endian))
        file.write(float_value_little_endian)

    def decode(self, file: BinaryIO, value=None) -> float:

        encoded = file.read(4)
        float_value_little_endian = unpack('f', encoded)[0]                
        float_value_big_endian = unpack('>l', pack('>f', float_value_little_endian))[0]  
        # we need to force bit 24 to be a 1 before encoding as a mid-endian float
        float_value_big_endian = unpack ('>f', pack('>l', float_value_big_endian - 2 ** 24))[0]
        
        return float_value_big_endian
