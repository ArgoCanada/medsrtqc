
from medsrtqc.core import Profile, Trace
import unittest
import numpy as np
from medsrtqc.qc.flag import Flag
import medsrtqc.qc.named_tests as tests


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
        Flag.update(qc, to=Flag.BAD)
        self.assertTrue(np.all(qc == np.array([Flag.BAD, Flag.BAD, Flag.MISSING])))

        qc = np.array([Flag.GOOD, Flag.PROBABLY_BAD, Flag.MISSING])
        Flag.update(qc, to=Flag.BAD, where=np.array([False, True, False]))
        self.assertTrue(np.all(qc == np.array([Flag.GOOD, Flag.BAD, Flag.MISSING])))


class TestPressureIncreasingTest(unittest.TestCase):

    def test_definitely_increasing(self):
        qc5 = np.repeat([Flag.NO_QC], 5)
        pres =  Trace([200, 150, 100, 50, 0], qc=qc5)
        pres.pres = pres.value
        prof = Profile({
            'PRES': pres,
            'TEMP': Trace([7, 7, 7, 5, 10], qc=qc5, pres=pres.value),
            'PSAL': Trace([12, 11, 10, 9, 8], qc=qc5, pres=pres.value)
        })

        test = tests.PressureIncreasingTest(prof)
        self.assertTrue(test.run())
        self.assertTrue(np.all(prof['PRES'].qc == qc5))
        self.assertTrue(np.all(prof['TEMP'].qc == qc5))
        self.assertTrue(np.all(prof['PSAL'].qc == qc5))


if __name__ == '__main__':
    unittest.main()
