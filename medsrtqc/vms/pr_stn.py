
from .field import *


class VMSPrStnFxd(VMSStructField):
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


class VMSPrStnProf(VMSStructField):
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


class VMSPrStnSurface(VMSStructField):
    def __init__(self) -> None:
        super().__init__(
            ('PCODE', VMSCharacter(4)),
            ('PARM', VMSReal4()),
            ('Q_PARM', VMSCharacter(1)),
            VMSPadding(1)
        )


class VMSPrStnSurfCodes(VMSStructField):
    def __init__(self) -> None:
        super().__init__(
            ('PCODE', VMSCharacter(4)),
            ('CPARM', VMSCharacter(10)),
            ('Q_PARM', VMSCharacter(1)),
            VMSPadding(1)
        )


class VMSPrStnHistory(VMSStructField):
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


class VMSPrStn(VMSStructField):

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
