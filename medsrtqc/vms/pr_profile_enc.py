
from collections import OrderedDict
from typing import BinaryIO
from . import enc


class PrProfileFxdEncoding(enc.StructEncoding):
    """The encoding strategy for a PR_PROFILE/FXD structure"""

    def __init__(self) -> None:
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
            ('PROF_TYPE', enc.Character(4)),
            ('PROFILE_SEG', enc.Character(2)),
            ('NO_DEPTHS', enc.Integer2()),
            ('D_P_CODE', enc.Character(1))
        )


class PrProfileProfEncoding(enc.StructEncoding):
    """The encoding strategy for the PR_PROFILE/PROF structure"""

    def __init__(self) -> None:
        super().__init__(
            ('DEPTH_PRESS', enc.Real4()),
            ('DP_FLAG', enc.Character(1)),
            ('PARM', enc.Real4()),
            ('Q_PARM', enc.Character(1))
        )


class PrProfileEncoding(enc.StructEncoding):
    """The encoding strategy for the PR_PROFILE structure"""

    def __init__(self) -> None:
        super().__init__(
            ('FXD', PrProfileFxdEncoding()),
            ('PROF', enc.ArrayOf(PrProfileProfEncoding(), max_length=1500))
        )

    def sizeof(self, value):
        n_prof = value['FXD']['NO_DEPTHS']
        size_fxd = self._encodings['FXD'].sizeof()
        size_prof = self._encodings['PROF'].sizeof([None] * n_prof)
        return size_fxd + size_prof

    def decode(self, file: BinaryIO, value=None):
        if value is None:
            value = OrderedDict()

        value['FXD'] = OrderedDict()
        self._encodings['FXD'].decode(file, value['FXD'])

        n_prof = value['FXD']['NO_DEPTHS']
        value['PROF'] = [None] * n_prof
        self._encodings['PROF'].decode(file, value['PROF'])

        return value
