
from .enc import *


class VMSPrStnFxdEncoding(VMSStructEncoding):
    """The encoding strategy used for the PR_STN/FXD structure"""

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


class VMSPrStnProfEncoding(VMSStructEncoding):
    """The encoding strategy used for the PR_STN/PROF structure"""

    def __init__(self) -> None:
        super().__init__(
            ('NO_SEG', VMSInteger2()),
            ('PROF_TYPE', VMSCharacter(4)),
            ('DUP_FLAG', VMSCharacter(1)),
            ('DIGIT_CODE', VMSCharacter(1)),
            ('STANDARD', VMSCharacter(1)),
            ('DEEP_DEPTH', VMSReal4())
        )


class VMSPrStnSurfaceEncoding(VMSStructEncoding):
    """The encoding strategy used for the PR_STN/SURFACE structure"""

    def __init__(self) -> None:
        super().__init__(
            ('PCODE', VMSCharacter(4)),
            ('PARM', VMSReal4()),
            ('Q_PARM', VMSCharacter(1))
        )


class VMSPrStnSurfCodesEncoding(VMSStructEncoding):
    """The encoding strategy used for the PR_STN/SURF_CODES structure"""

    def __init__(self) -> None:
        super().__init__(
            ('PCODE', VMSCharacter(4)),
            ('CPARM', VMSCharacter(10)),
            ('Q_PARM', VMSCharacter(1))
        )


class VMSPrStnHistoryEncoding(VMSStructEncoding):
    """The encoding strategy used for the PR_STN/HISTORY structure"""

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


class VMSPrStnEncoding(VMSStructEncoding):
    """The encoding strategy used for the PR_STN structure"""

    def __init__(self) -> None:
        super().__init__(
            ('FXD', VMSPrStnFxdEncoding()),
            ('PROF', VMSArrayOf(VMSPrStnProfEncoding(), max_length=20)),
            ('SURFACE', VMSArrayOf(VMSPrStnSurfaceEncoding(), max_length=20)),
            ('SURF_CODES', VMSArrayOf(VMSPrStnSurfCodesEncoding(), max_length=20)),
            ('HISTORY', VMSArrayOf(VMSPrStnHistoryEncoding(), max_length=100))
        )

    def sizeof(self, value):
        n_prof = value['FXD']['NO_PROF']
        n_surface = value['FXD']['NPARMS']
        n_surf_codes = value['FXD']['SPARMS']
        n_history = value['FXD']['NUM_HISTS']

        list1 = [None]
        size_fxd = self._encodings['FXD'].sizeof()
        size_prof = self._encodings['PROF'].sizeof(list1 * n_prof)
        size_surface = self._encodings['SURFACE'].sizeof(list1 * n_surface)
        size_surf_codes = self._encodings['SURF_CODES'].sizeof(list1 * n_surf_codes)
        size_history = self._encodings['HISTORY'].sizeof(list1 * n_history)

        return size_fxd + size_prof + size_surface + size_surf_codes + size_history

    def decode(self, file: BinaryIO, value=None):
        if value is None:
            value = OrderedDict()

        value['FXD'] = OrderedDict()
        self._encodings['FXD'].decode(file, value['FXD'])

        n_prof = value['FXD']['NO_PROF']
        n_surface = value['FXD']['NPARMS']
        n_surf_codes = value['FXD']['SPARMS']
        n_history = value['FXD']['NUM_HISTS']

        list1 = [None]
        value['PROF'] = list1 * n_prof
        value['SURFACE'] = list1 * n_surface
        value['SURF_CODES'] = list1 * n_surf_codes
        value['HISTORY'] = list1 * n_history

        self._encodings['PROF'].decode(file, value['PROF'])
        self._encodings['SURFACE'].decode(file, value['SURFACE'])
        self._encodings['SURF_CODES'].decode(file, value['SURF_CODES'])
        self._encodings['HISTORY'].decode(file, value['HISTORY'])

        return value
