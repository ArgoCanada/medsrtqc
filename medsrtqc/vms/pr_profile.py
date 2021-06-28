
from .field import *


class VMSPrProfileFxdField(VMSStructField):
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


class VMSPrProfileProfField(VMSStructField):
    def __init__(self) -> None:
        super().__init__(
            ('DEPTH_PRESS', VMSReal4()),
            ('DP_FLAG', VMSCharacter(1)),
            ('PARM', VMSReal4()),
            ('Q_PARM', VMSCharacter(1))
        )


class VMSPrProfile(VMSStructField):

    def __init__(self) -> None:
        super().__init__(
            ('FXD', VMSPrProfileFxdField()),
            ('PROF', VMSArrayOf(VMSPrProfileProfField(), max_length=1500))
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
