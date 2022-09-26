
import copy
from collections import OrderedDict
import numpy as np

from medsrtqc.qc.chla import ChlaTest
from medsrtqc.qc.bbp import bbpTest
from medsrtqc.qc.history import QCx
from medsrtqc.qc.operation import QCOperation

class preTestCheck(QCOperation):

    def run_impl(self):

        self.list_tests()
        self.check_vars()

        return self.tests

    def list_tests(self):

        tests = list()
        if 'FLU1' in self.profile.keys():
            tests.append(ChlaTest())
        if 'BBP$' in self.profile.keys():
            tests.append(bbpTest())

        self.tests = tests
    
    def check_vars(self):

        # check if QCF or QCP exist, if not, make them
        data = copy.deepcopy(self.profile._data)
        current_vars = [d['PCODE'] for d in data['PR_STN']['SURF_CODES']]
        for v in ['QCP$', 'QCF$']:
            if v not in current_vars:
                data['PR_STN']['SURF_CODES'].append(QCx.blank(v))
        

        # add FLUA to data if FLU1 exists
        if 'FLU1' in self.profile.keys() and 'FLUA' not in self.profile.keys():
            # find where FLU1 is
            ix = np.where(np.array(self.profile.keys()) == 'FLU1')[0][0] - 1
            FLUA = OrderedDict()
            FLUA['FXD'] = data['PR_PROFILE'][ix]['FXD']
            FLUA['FXD']['PROF_TYPE'] = 'FLUA'
            FLUA['PROF'] = [\
                OrderedDict([\
                    ('DEPTH_PRESS', d['DEPTH_PRESS']),\
                    ('DP_FLAG', d['DP_FLAG']), ('PARM', 99999.),\
                    ('Q_PARM', d['Q_PARM'])])\
                for d in data['PR_PROFILE'][ix]['PROF']\
            ]
            data['PR_PROFILE'].append(FLUA)

        # update data with new variable
        self.profile._data = data
        self.profile._update_by_param_from_data()