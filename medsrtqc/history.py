
from collections import OrderedDict
import numpy as np

def read_qc_hex(hex_code):
    num = int(hex_code, 16)
    # list to save test number in
    tests = []
    for i in range(63, 56, -1):
        qc_binary_id = 2**i
        if qc_binary_id <= num:
            num -= qc_binary_id
            tests.append(i)

    for i in range(26, 0, -1):
        qc_binary_id = 2**i
        if qc_binary_id <= num:
            num -= qc_binary_id
            tests.append(i)
    
    if num != 0:
        raise ValueError('Invalid input, decoding QC tests left a non-zero remainder')

    return tests[::-1]

def test_index(test):

    test_numbers = list(range(1, 24)) + list(range(57, 64))
    return test_numbers.index(test)

def qc_array(qc):

    QC_array = np.zeros((30,))

    # hex to numeric
    tests = read_qc_hex(qc)
    if len(tests) != 0:
        test_indices = [i-1 for i in tests]
        QC_array[test_indices] = 1

    return QC_array

class QCx:

    @staticmethod
    def blank(v):

        history_qctest = OrderedDict(
            PCODE=v,
            CPARM=str(hex(0)),
            Q_PARM='0'
        )

        return history_qctest

    @staticmethod
    def qc_tests(qcp, qcf):
        output_array = np.zeros((2, 30))
        output_array[0,:] = qc_array(qcp)
        output_array[1,:] = qc_array(qcf)

        return output_array

    @staticmethod
    def update_safely(qc, test, passfail):
        qcp = 0
        qcf = 1
        ix = test_index(test)
        pass_list = ['p', 'P', 'PASS', 'pass', 1, '1']
        fail_list = ['f', 'F', 'FAIL', 'fail', 0, '0']

        if passfail in pass_list:
            if qc[qcp, ix] == 0 and qc[qcf, ix] == 0:
                qc[qcp, ix] = 1
        elif passfail in fail_list:
            if qc[qcp, ix] == 0 and qc[qcf, ix] == 0:
                qc[qcf, ix] = 1
            elif qc[qcp, ix] == 1:
                qc[qcf, ix] = 1
                qc[qcp, ix] = 0
        else: # pragma: no cover
            raise ValueError(f'passfail input not recognized, must be one of {pass_list} or {fail_list}')

    @staticmethod
    def array_to_hex(qcx):
        test_numbers = list(range(1, 24)) + list(range(57, 64))
        num = 0

        for i in qcx:
            if i == 1:
                num += 2**test_numbers[i]
        
        return hex(num)

    test_descriptions = [
        '1. Platform Identification test',
        '2. Impossible Date test',
        '3. Impossible Location test',
        '4. Position on Land test',
        '5. Impossible Speed test',
        '6. Global Range test',
        '7. Regional Global Parameter test',
        '8. Pressure Increasing test',
        '9. Spike test',
        '10. Top and Bottom Spike test (obsolete)',
        '11. Gradient test',
        '12. Digit Rollover test',
        '13. Stuck Value test',
        '14. Density Inversion test',
        '15. Grey List test',
        '16. Gross Salinity or Temperature Sensor Drift test',
        '17. Visual QC test',
        '18. Frozen profile test',
        '19. Deepest pressure test',
        '20. Questionable Argos position test',
        '21. Near-surface unpumped CTD salinity test',
        '22. Near-surface mixed air/water test',
        '23. Real-time Quality Control Flag Scheme for float data deeper than 2000 dbar',
        '57. DOXY specific test',
        '58. CDOM specific test',
        '59. NITRATE specific test',
        '60. PAR specific test',
        '61. IRRADIANCE specific test',
        '62. BBP specific tests',
        '63. CHLA specific tests',
    ]