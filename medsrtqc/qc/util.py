
from ..core import QCOperation
from .flag import Flag


class ResetQCOperation(QCOperation):

    def __init__(self, profile, previous_profile=None, applier=None):
        super().__init__(profile, previous_profile, applier=applier)
        self._vars = None
        self._flag = Flag.NO_QC
        self._qc = True
        self._adjusted_qc = False

    def run(self):
        if self._vars is None:
            reset_vars = set(self.profile.keys())
        else:
            reset_vars = set(self.profile.keys).intersection(self._vars)

        for var in reset_vars:
            trace = self.profile[var]

            if self._qc:
                trace.qc[:] = Flag.NO_QC
            if self._adjusted_qc:
                trace.adjusted_qc[:] = Flag.NO_QC

            self.update_trace(var, trace)
