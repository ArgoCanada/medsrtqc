
from medsrtqc.qc.chla import ChlaTest
from medsrtqc.qc.bbp import bbpTest
from medsrtqc.qc.ph import pHTest
from medsrtqc.qc.radio import radiometryTest
from medsrtqc.qc.operation import QCOperation

class preTestCheck(QCOperation):

    def run_impl(self):

        self.list_tests()

        return self.tests

    def list_tests(self):

        tests = list()
        if 'FLU1' in self.profile.keys() or 'CHLA' in self.profile.keys():
            tests.append(ChlaTest())
        if 'BBP$' in self.profile.keys() or 'BBP700' in self.profile.keys():
            tests.append(bbpTest())
        if 'PHPH' in self.profile.keys() or 'PH_IN_SITU' in self.profile.keys():
            tests.append(pHTest())
        if any(x in self.profile.keys() for x in ['P380', 'P412', 'P443', 'P490', 'PAR$']):
            tests.append(radiometryTest())

        self.tests = tests
