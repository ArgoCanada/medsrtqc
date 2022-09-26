
from collections import OrderedDict

class QCx:

    def blank(v):

        history_qctest = OrderedDict(
            PCODE=v,
            CPARM=str(hex(0)),
            Q_PARM='0'
        )

        return history_qctest