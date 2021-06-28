
from io import BytesIO
from typing import BinaryIO
from struct import pack, unpack, calcsize
from collections import OrderedDict


class VMSField:

    def n_bytes(self, value=None):
        raise NotImplementedError()

    def from_stream(self, file: BinaryIO):
        raise NotImplementedError()

    def to_stream(self, file: BinaryIO, value):
        raise NotImplementedError()


class VMSPadding(VMSField):

    def __init__(self, length) -> None:
        self._length = length

    def n_bytes(self, value=None):
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

    def n_bytes(self, value=None):
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


class VMSArrayOf(VMSField):

    def __init__(self, field: VMSField, max_length) -> None:
        self._field = field
        self._max_length = max_length

    def n_bytes(self, value):
        return self._field.n_bytes() * len(value)

    def from_stream(self, file: BinaryIO, value):
        for i in range(len(value)):
            value[i] = self._field.from_stream(file)
        return value

    def to_stream(self, file: BinaryIO, value):
        if (len(value) > self._max_length):
            raise ValueError(f'len(value) greater than allowed max length ({self._max_length})')
        for item in value:
            self._field.to_stream(file, item)


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


class VMSPrProfileFxd(VMSStruct):
    def __init__(self) -> None:
        super().__init__(
            ('MKEY', VMSCharacter(8)),
            ('ONE_DEG_SQ', VMSInteger4()),
            ('CR_NUMBER', VMSCharacter(10)),
            ('OBS_YEAR', VMSCharacter(4)),
            ('OBS_DAY', VMSCharacter(2)),
            ('OBS_TIME', VMSCharacter(4)),
            ('DATA_TYPE', VMSCharacter(2)),
            ('IUMSGNO', VMSInteger4()),
            ('PROF_TYPE', VMSCharacter(4)),
            ('PROFILE_SEG', VMSCharacter(2)),
            ('NO_DEPTHS', VMSInteger2()),
            ('D_P_CODE', VMSCharacter(1)),
            VMSPadding(1)
        )


class VMSPrProfileProf(VMSStruct):
    def __init__(self) -> None:
        super().__init__(
            ('DEPTH_PRESS', VMSReal4()),
            ('DP_FLAG', VMSCharacter(1)),
            ('PARM', VMSReal4()),
            ('Q_PARM', VMSCharacter(1))
        )


class VMSPrStnFxd(VMSStruct):
    def __init__(self) -> None:
        super().__init__(
            ('MKEY', VMSCharacter(8)),
            ('ONE_DEG_SQ', VMSInteger4()),
            ('CR_NUMBER', VMSCharacter(10)),
            ('OBS_YEAR', VMSCharacter(4)),
            ('OBS_MONTH', VMSCharacter(2)),
            ('OBS_DAY', VMSCharacter(2)),
            ('OBS_TIME', VMSCharacter(4)),
            ('DATA_TYPE', VMSCharacter(2)),
            ('IUMSGNO', VMSInteger4()),
            ('STREAM_SOURCE', VMSCharacter(1)),
            ('U_FLAG', VMSCharacter(1)),
            ('STN_NUMBER', VMSInteger2()),
            ('LATITUDE', VMSReal4()),
            ('LONGITUDE', VMSReal4()),
            ('Q_POS', VMSCharacter(1)),
            ('Q_DATE_TIME', VMSCharacter(1)),
            ('Q_RECORD', VMSCharacter(1)),
            ('UP_DATE', VMSCharacter(8)),
            ('BUL_TIME', VMSCharacter(12)),
            ('BUL_HEADER', VMSCharacter(6)),
            ('SOURCE_ID', VMSCharacter(4)),
            ('STREAM_IDENT', VMSCharacter(4)),
            ('QC_VERSION', VMSCharacter(4)),
            ('AVAIL', VMSCharacter(1)),
            ('NO_PROF', VMSInteger2()),
            ('NPARMS', VMSInteger2()),
            ('SPARMS', VMSInteger2()),
            ('NUM_HISTS', VMSInteger2())
        )


class VMSPrStnProf(VMSStruct):
    def __init__(self) -> None:
        super().__init__(
            ('NO_SEG', VMSInteger2()),
            ('PROF_TYPE', VMSCharacter(4)),
            ('DUP_FLAG', VMSCharacter(1)),
            ('DIGIT_CODE', VMSCharacter(1)),
            ('STANDARD', VMSCharacter(1)),
            ('DEEP_DEPTH', VMSReal4()),
            VMSPadding(1)
        )


class VMSPrStnSurface(VMSStruct):
    def __init__(self) -> None:
        super().__init__(
            ('PCODE', VMSCharacter(4)),
            ('PARM', VMSReal4()),
            ('Q_PARM', VMSCharacter(1)),
            VMSPadding(1)
        )


class VMSPrStnSurfCodes(VMSStruct):
    def __init__(self) -> None:
        super().__init__(
            ('PCODE', VMSCharacter(4)),
            ('CPARM', VMSCharacter(10)),
            ('Q_PARM', VMSCharacter(1)),
            VMSPadding(1)
        )


class VMSPrStnHistory(VMSStruct):
    def __init__(self) -> None:
        super().__init__(
            ('IDENT_CODE', VMSCharacter(2)),
            ('PRC_CODE', VMSCharacter(4)),
            ('VERSION', VMSCharacter(4)),
            ('PRC_DATE', VMSInteger4()),
            ('ACT_CODE', VMSCharacter(2)),
            ('ACT_PARM', VMSCharacter(4)),
            ('AUX_ID', VMSReal4()),
            ('O_VALUE', VMSReal4())
        )


class VMSPrProfile(VMSStruct):

    def __init__(self) -> None:
        super().__init__(
            ('FXD', VMSPrProfileFxd()),
            ('PROF', VMSArrayOf(VMSPrProfileProf(), max_length=1500))
        )

    def n_bytes(self, value):
        n_prof = value['FXD']['NO_DEPTHS']
        size_fxd = self._fields['FXD'].n_bytes()
        size_prof = self._fields['PROF'].n_bytes([None] * n_prof)
        return size_fxd + size_prof

    def from_stream(self, file: BinaryIO, value=None):
        if value is None:
            value = {}

        value['FXD'] = OrderedDict()
        self._fields['FXD'].from_stream(file, value['FXD'])

        n_prof = value['FXD']['NO_DEPTHS']
        value['PROF'] = [None] * n_prof
        self._fields['PROF'].from_stream(file, value['PROF'])

        return value


class VMSPrStn(VMSStruct):

    def __init__(self) -> None:
        super().__init__(
            ('FXD', VMSPrStnFxd()),
            ('PROF', VMSArrayOf(VMSPrStnProf(), max_length=20)),
            ('SURFACE', VMSArrayOf(VMSPrStnSurface(), max_length=20)),
            ('SURF_CODES', VMSArrayOf(VMSPrStnSurfCodes(), max_length=20)),
            ('HISTORY', VMSArrayOf(VMSPrStnHistory(), max_length=100))
        )

    def n_bytes(self, value):
        n_prof = value['FXD']['NO_PROF']
        n_surface = value['FXD']['NPARMS']
        n_surf_codes = value['FXD']['SPARMS']
        n_history = value['FXD']['NUM_HIST']

        list1 = [None]
        size_fxd = self._fields['FXD'].n_bytes()
        size_prof = self._fields['PROF'].n_bytes(list1 * n_prof)
        size_surface = self._fields['SURFACE'].n_bytes(list1 * n_surface)
        size_surf_codes = self._fields['SURF_CODES'].n_bytes(list1 * n_surf_codes)
        size_history = self._fields['HISTORY'].n_bytes(list1 * n_history)

        return size_fxd + size_prof + size_surface + size_surf_codes + size_history

    def from_stream(self, file: BinaryIO, value=None):
        if value is None:
            value = OrderedDict()

        value['FXD'] = OrderedDict()
        self._fields['FXD'].from_stream(file, value['FXD'])

        n_prof = value['FXD']['NO_PROF']
        n_surface = value['FXD']['NPARMS']
        n_surf_codes = value['FXD']['SPARMS']
        n_history = value['FXD']['NUM_HIST']

        list1 = [None]
        value['PROF'] = list1 * n_prof
        value['SURFACE'] = list1 * n_surface
        value['SURF_CODES'] = list1 * n_surf_codes
        value['HISTORY'] = list1 * n_history

        self._fields['PROF'].from_stream(value['PROF'])
        self._fields['SURFACE'].from_stream(value['SURFACE'])
        self._fields['SURF_CODES'].from_stream(value['SURF_CODES'])
        self._fields['HISTORY'].from_stream(value['HISTORY'])

        return value
