
from medsrtqc.qc.operation import QCOperation
from medsrtqc.qc.flag import Flag
# from medsrtqc.qc.history import QCx

class pHTest(QCOperation):

    def run_impl(self):
        pH_free = self.profile['PHPH']
        pH_total = self.profile['PHTO']

        # set flags to zero, there are no QC tests for pH yet
        Flag.update_safely(pH_free.qc, Flag.NO_QC)
        Flag.update_safely(pH_total.qc, Flag.NO_QC)

        self.update_trace('PHPH', pH_free)
        self.update_trace('PHTO', pH_total)