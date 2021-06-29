
from .enc import *


class PrProfileFxdEncoding(StructEncoding):
    """The encoding strategy for a PR_PROFILE/FXD structure"""

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
            ('PROF_TYPE', Character(4)),
            ('PROFILE_SEG', Character(2)),
            ('NO_DEPTHS', Integer2()),
            ('D_P_CODE', Character(1))
        )


class PrProfileProfEncoding(StructEncoding):
    """The encoding strategy for the PR_PROFILE/PROF structure"""

    def __init__(self) -> None:
        super().__init__(
            ('DEPTH_PRESS', Real4()),
            ('DP_FLAG', Character(1)),
            ('PARM', Real4()),
            ('Q_PARM', Character(1))
        )


class PrProfileEncoding(StructEncoding):
    """The encoding strategy for the PR_PROFILE structure"""

    def __init__(self) -> None:
        super().__init__(
            ('FXD', PrProfileFxdEncoding()),
            ('PROF', ArrayOf(PrProfileProfEncoding(), max_length=1500))
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
