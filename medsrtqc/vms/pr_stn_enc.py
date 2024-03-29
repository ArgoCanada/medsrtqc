
from collections import OrderedDict
from typing import BinaryIO

from . import enc
from . import enc_win

class PrStnFxdEncoding(enc.StructEncoding):
    """The encoding strategy used for the PR_STN/FXD structure"""

    def __init__(self, ver='vms') -> None:

        self._ver = ver
        self._fxd = 'PrStn'

        if ver == 'vms':
            val_encoding = enc.Real4()
        elif ver == 'win':
            val_encoding = enc_win.Float()
        else: # pragma: no cover
            raise ValueError(f'Invalid version: {ver}, must be one of "vms" or "win"')

        super().__init__(
            ('MKEY', enc.Character(8)),
            ('ONE_DEG_SQ', enc.Integer4()),
            ('CR_NUMBER', enc.Character(10)),
            ('OBS_YEAR', enc.Character(4)),
            ('OBS_MONTH', enc.Character(2)),
            ('OBS_DAY', enc.Character(2)),
            ('OBS_TIME', enc.Character(4)),
            ('DATA_TYPE', enc.Character(2)),
            ('IUMSGNO', enc.Integer4()),
            ('STREAM_SOURCE', enc.Character(1)),
            ('U_FLAG', enc.Character(1)),
            ('STN_NUMBER', enc.Integer2()),
            ('LATITUDE', val_encoding),
            ('LONGITUDE', val_encoding),
            ('Q_POS', enc.Character(1)),
            ('Q_DATE_TIME', enc.Character(1)),
            ('Q_RECORD', enc.Character(1)),
            ('UP_DATE', enc.Character(8)),
            ('BUL_TIME', enc.Character(12)),
            ('BUL_HEADER', enc.Character(6)),
            ('SOURCE_ID', enc.Character(4)),
            ('STREAM_IDENT', enc.Character(4)),
            ('QC_VERSION', enc.Character(4)),
            ('AVAIL', enc.Character(1)),
            ('NO_PROF', enc.Integer2()),
            ('NPARMS', enc.Integer2()),
            ('SPARMS', enc.Integer2()),
            ('NUM_HISTS', enc.Integer2())
        )


class PrStnProfEncoding(enc.StructEncoding):
    """The encoding strategy used for the PR_STN/PROF structure"""

    def __init__(self, ver='vms') -> None:

        self._ver = ver
        self._prof = 'PrStn'

        if ver == 'vms':
            val_encoding = enc.Real4()
        elif ver == 'win':
            val_encoding = enc_win.Float()
        else: # pragma: no cover
            raise ValueError(f'Invalid version: {ver}, must be one of "vms" or "win"')

        super().__init__(
            ('NO_SEG', enc.Integer2()),
            ('PROF_TYPE', enc.Character(4)),
            ('DUP_FLAG', enc.Character(1)),
            ('DIGIT_CODE', enc.Character(1)),
            ('STANDARD', enc.Character(1)),
            ('DEEP_DEPTH', val_encoding)
        )


class PrStnSurfaceEncoding(enc.StructEncoding):
    """The encoding strategy used for the PR_STN/SURFACE structure"""

    def __init__(self, ver='vms') -> None:
        if ver == 'vms': 
            pcode_length = 4
            val_encoding = enc.Real4()
        elif ver == 'win':
            pcode_length = 150
            val_encoding = enc_win.Float()
        else: # pragma: no cover
            raise ValueError(f'Invalid version: {ver}, must be one of "vms" or "win"')


        super().__init__(
            ('PCODE', enc.Character(pcode_length)),
            ('PARM', val_encoding),
            ('Q_PARM', enc.Character(1))
        )


class PrStnSurfCodesEncoding(enc.StructEncoding):
    """The encoding strategy used for the PR_STN/SURF_CODES structure"""

    def __init__(self, ver='vms') -> None:
        if ver == 'vms':
            pcode_length = 4
            cparm_length = 10
        elif ver == 'win':
            pcode_length = 150
            cparm_length = 512
        else: # pragma: no cover
            raise ValueError(f'Invalid version: {ver}, must be one of "vms" or "win"')

        super().__init__(
            ('PCODE', enc.Character(pcode_length)),
            ('CPARM', enc.Character(cparm_length)),
            ('Q_PARM', enc.Character(1))
        )


class PrStnHistoryEncoding(enc.StructEncoding):
    """The encoding strategy used for the PR_STN/HISTORY structure"""

    def __init__(self, ver='vms') -> None:
        if ver == 'vms':
            val_encoding = enc.Real4()
        elif ver == 'win':
            val_encoding = enc_win.Float()
        else: # pragma: no cover
            raise ValueError(f'Invalid version: {ver}, must be one of "vms" or "win"')

        super().__init__(
            ('IDENT_CODE', enc.Character(2)),
            ('PRC_CODE', enc.Character(4)),
            ('VERSION', enc.Character(4)),
            ('PRC_DATE', enc.Integer4()),
            ('ACT_CODE', enc.Character(2)),
            ('ACT_PARM', enc.Character(4)),
            ('AUX_ID', val_encoding),
            ('O_VALUE', val_encoding)
        )


class PrStnEncoding(enc.StructEncoding):
    """The encoding strategy used for the PR_STN structure"""

    def __init__(self, ver='vms') -> None:

        self._ver = ver
        
        super().__init__(
            ('FXD', PrStnFxdEncoding(ver)),
            ('PROF', enc.ArrayOf(PrStnProfEncoding(ver), max_length=1500)),
            ('SURFACE', enc.ArrayOf(PrStnSurfaceEncoding(ver), max_length=None)),
            ('SURF_CODES', enc.ArrayOf(PrStnSurfCodesEncoding(ver), max_length=None)),
            ('HISTORY', enc.ArrayOf(PrStnHistoryEncoding(ver), max_length=100))
        )

    def decode(self, file: BinaryIO, value=None):
        if value is None:  # pragma: no cover
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
