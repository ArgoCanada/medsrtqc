
import unittest
import medsrtqc.qc.history as hist

class TestHistory(unittest.TestCase):

    def test_qctests(self):
        hexval = hex(2**63 + 2**4)
        tests = hist.read_qc_hex(hexval)
        self.assertEqual(tests, [4, 63])

        qc_arr = hist.qc_array(hexval)
        self.assertTrue(qc_arr[hist.test_index(4)] == 1)

        fail = hex(2**62 + 2**9)
        qcpf = hist.QCx.qc_tests(hexval, fail)

        hist.QCx.update_safely(qcpf, 8, 'pass')
        self.assertEqual(qcpf[0, hist.test_index(8)], 1)

        hist.QCx.update_safely(qcpf, 2, 'fail')
        self.assertEqual(qcpf[1, hist.test_index(2)], 1)

        hist.QCx.update_safely(qcpf, 4, 'fail')
        self.assertEqual(qcpf[0, hist.test_index(4)], 0)
        self.assertEqual(qcpf[1, hist.test_index(4)], 1)

if __name__ == '__main__':
    unittest.main()
