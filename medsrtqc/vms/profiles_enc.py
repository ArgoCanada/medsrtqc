
from typing import BinaryIO
from collections import OrderedDict
from . import enc
from .pr_stn_enc import PrStnEncoding
from .pr_profile_enc import PrProfileEncoding


class PrStnAndPrProfilesEncoding(enc.StructEncoding):
    """Encoding for a common grouping of PR_STN + all PR_PROFILEs"""

    def __init__(self, ver) -> None:
        super().__init__(
            ('PR_STN', PrStnEncoding(ver)),
            ('PR_PROFILE', enc.ArrayOf(PrProfileEncoding(ver))),
        )

    def decode(self, file: BinaryIO, value=None) -> OrderedDict:
        if value is None:
            value = OrderedDict()

        value['PR_STN'] = OrderedDict()
        self._encodings['PR_STN'].decode(file, value['PR_STN'])

        n_pr_profile = sum(p['NO_SEG'] for p in value['PR_STN']['PROF'])
        value['PR_PROFILE'] = [None] * n_pr_profile
        self._encodings['PR_PROFILE'].decode(file, value['PR_PROFILE'])

        return value
