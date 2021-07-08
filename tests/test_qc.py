
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

    def test_simple(self):
        pass


if __name__ == '__main__':
    unittest.main()
