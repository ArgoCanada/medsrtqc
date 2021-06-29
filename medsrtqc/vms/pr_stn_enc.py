
from .enc import *


class PrStnFxdEncoding(StructEncoding):
    """The encoding strategy used for the PR_STN/FXD structure"""

    def __init__(self) -> None:
        super().__init__(
            ('MKEY', Character(8)),
            ('ONE_DEG_SQ', Integer4()),
            ('CR_NUMBER', Character(10)),
            ('OBS_YEAR', Character(4)),
            ('OBS_MONTH', Character(2)),
            ('OBS_DAY', Character(2)),
            ('OBS_TIME', Character(4)),
            ('DATA_TYPE', Character(2)),
            ('IUMSGNO', Integer4()),
            ('STREAM_SOURCE', Character(1)),
            ('U_FLAG', Character(1)),
            ('STN_NUMBER', Integer2()),
            ('LATITUDE', Real4()),
            ('LONGITUDE', Real4()),
            ('Q_POS', Character(1)),
            ('Q_DATE_TIME', Character(1)),
            ('Q_RECORD', Character(1)),
            ('UP_DATE', Character(8)),
            ('BUL_TIME', Character(12)),
            ('BUL_HEADER', Character(6)),
            ('SOURCE_ID', Character(4)),
            ('STREAM_IDENT', Character(4)),
            ('QC_VERSION', Character(4)),
            ('AVAIL', Character(1)),
            ('NO_PROF', Integer2()),
            ('NPARMS', Integer2()),
            ('SPARMS', Integer2()),
            ('NUM_HISTS', Integer2())
        )


class PrStnProfEncoding(StructEncoding):
    """The encoding strategy used for the PR_STN/PROF structure"""

    def __init__(self) -> None:
        super().__init__(
            ('NO_SEG', Integer2()),
            ('PROF_TYPE', Character(4)),
            ('DUP_FLAG', Character(1)),
            ('DIGIT_CODE', Character(1)),
            ('STANDARD', Character(1)),
            ('DEEP_DEPTH', Real4())
        )


class PrStnSurfaceEncoding(StructEncoding):
    """The encoding strategy used for the PR_STN/SURFACE structure"""

    def __init__(self) -> None:
        super().__init__(
            ('PCODE', Character(4)),
            ('PARM', Real4()),
            ('Q_PARM', Character(1))
        )


class PrStnSurfCodesEncoding(StructEncoding):
    """The encoding strategy used for the PR_STN/SURF_CODES structure"""

    def __init__(self) -> None:
        super().__init__(
            ('PCODE', Character(4)),
            ('CPARM', Character(10)),
            ('Q_PARM', Character(1))
        )


class PrStnHistoryEncoding(StructEncoding):
    """The encoding strategy used for the PR_STN/HISTORY structure"""

    def __init__(self) -> None:
        super().__init__(
            ('IDENT_CODE', Character(2)),
            ('PRC_CODE', Character(4)),
            ('VERSION', Character(4)),
            ('PRC_DATE', Integer4()),
            ('ACT_CODE', Character(2)),
            ('ACT_PARM', Character(4)),
            ('AUX_ID', Real4()),
            ('O_VALUE', Real4())
        )


class PrStnEncoding(StructEncoding):
    """The encoding strategy used for the PR_STN structure"""

    def __init__(self) -> None:
        super().__init__(
            ('FXD', PrStnFxdEncoding()),
            ('PROF', ArrayOf(PrStnProfEncoding(), max_length=20)),
            ('SURFACE', ArrayOf(PrStnSurfaceEncoding(), max_length=20)),
            ('SURF_CODES', ArrayOf(PrStnSurfCodesEncoding(), max_length=20)),
            ('HISTORY', ArrayOf(PrStnHistoryEncoding(), max_length=100))
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
