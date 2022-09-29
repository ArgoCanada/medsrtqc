
from medsrtqc.core import Profile, Trace
from medsrtqc.qc.operation import QCOperationError
import unittest
import numpy as np
from medsrtqc.qc.flag import Flag
import medsrtqc.qc.named_tests as tests
import medsrtqc.qc.util as util


class TestFlag(unittest.TestCase):

    def test_value(self):
        self.assertEqual(Flag.NO_QC, Flag.value('NO_QC'))
        self.assertEqual(Flag.label(Flag.NO_QC), 'NO_QC')
        with self.assertRaises(KeyError):
            Flag.value('not a QC key')
        with self.assertRaises(KeyError):
            Flag.label(b'def not a flag')

    def test_update(self):
        qc = np.array([Flag.GOOD, Flag.PROBABLY_BAD, Flag.MISSING])
        Flag.update_safely(qc, to=Flag.BAD)
        self.assertTrue(np.all(qc == np.array([Flag.BAD, Flag.BAD, Flag.MISSING])))

        qc = np.array([Flag.GOOD, Flag.PROBABLY_BAD, Flag.MISSING])
        Flag.update_safely(qc, to=Flag.BAD, where=np.array([False, True, False]))
        self.assertTrue(np.all(qc == np.array([Flag.GOOD, Flag.BAD, Flag.MISSING])))


class TestUtil(unittest.TestCase):

    def test_reset_qc(self):
        pres = Trace(
            [0, 50, 100, 150, 200],
            qc=[Flag.GOOD] * 5,
            adjusted_qc=[Flag.GOOD] * 5
        )
        prof = Profile({'PRES': pres})
        util.ResetQCOperation().run(prof)
        self.assertTrue(np.all(prof['PRES'].qc == Flag.NO_QC))
        self.assertTrue(np.all(prof['PRES'].adjusted_qc == Flag.GOOD))


class TestPressureIncreasingTest(unittest.TestCase):

    def test_inappropriate_traces(self):
        qc5 = np.repeat([Flag.NO_QC], 5)
        pres =  Trace([0, 50, 100, 150, 200], qc=qc5)
        pres.pres = pres.value
        prof = Profile({
            'PRES': pres,
            'TEMP': Trace([10, 5, 7, 7, 7], qc=qc5),
            'PSAL': Trace([8, 9, 10, 11, 12], qc=qc5)
        })
        with self.assertRaises(QCOperationError):
            tests.PressureIncreasingTest().run(prof)

    def test_definitely_increasing(self):
        qc5 = np.repeat([Flag.NO_QC], 5)
        pres =  Trace([0, 50, 100, 150, 200], qc=qc5)
        pres.pres = pres.value
        prof = Profile({
            'PRES': pres,
            'TEMP': Trace([10, 5, 7, 7, 7], qc=qc5, pres=pres.value),
            'PSAL': Trace([8, 9, 10, 11, 12], qc=qc5, pres=pres.value)
        })

        test = tests.PressureIncreasingTest()
        qc_expected = qc5
        self.assertTrue(test.run(prof))
        self.assertTrue(np.all(prof['PRES'].qc == qc_expected))
        self.assertTrue(np.all(prof['TEMP'].qc == qc_expected))
        self.assertTrue(np.all(prof['PSAL'].qc == qc_expected))

    def test_non_monotonic(self):
        qc5 = np.repeat([Flag.NO_QC], 5)
        pres =  Trace([50, 50, 100, 150, 200], qc=qc5)
        pres.pres = pres.value
        prof = Profile({
            'PRES': pres,
            'TEMP': Trace([10, 5, 7, 7, 7], qc=qc5, pres=pres.value),
            'PSAL': Trace([8, 9, 10, 11, 12], qc=qc5, pres=pres.value)
        })

        test = tests.PressureIncreasingTest()
        qc_expected = [Flag.NO_QC, Flag.BAD, Flag.NO_QC, Flag.NO_QC, Flag.NO_QC]
        self.assertFalse(test.run(prof))
        self.assertTrue(np.all(prof['PRES'].qc == qc_expected))
        self.assertTrue(np.all(prof['TEMP'].qc == qc_expected))
        self.assertTrue(np.all(prof['PSAL'].qc == qc_expected))

    def test_running_maximum(self):
        qc5 = np.repeat([Flag.NO_QC], 5)
        pres =  Trace([0, 50, 0, 50, 100], qc=qc5)
        pres.pres = pres.value
        prof = Profile({
            'PRES': pres,
            'TEMP': Trace([10, 5, 7, 7, 7], qc=qc5, pres=pres.value),
            'PSAL': Trace([8, 9, 10, 11, 12], qc=qc5, pres=pres.value)
        })

        test = tests.PressureIncreasingTest()
        qc_expected = [Flag.NO_QC, Flag.NO_QC, Flag.BAD, Flag.BAD, Flag.NO_QC]
        self.assertFalse(test.run(prof))
        self.assertTrue(np.all(prof['PRES'].qc == qc_expected))
        self.assertTrue(np.all(prof['TEMP'].qc == qc_expected))
        self.assertTrue(np.all(prof['PSAL'].qc == qc_expected))


if __name__ == '__main__':
    unittest.main()
