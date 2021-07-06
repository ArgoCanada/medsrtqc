
import unittest
import matplotlib
matplotlib.use('agg')

from medsrtqc.core import Trace, Profile
from medsrtqc.interactive import plot

class TestPlot(unittest.TestCase):

    def test_plot(self):
        trace = Trace([1.0, 2.0, 4.0], adjusted=[2.0, 3.0, 5.0])
        profile = Profile({'PARAM': trace, 'PARAM2': trace})
        self.assertEqual(type(plot(trace)).__name__, 'AxesSubplot')
        self.assertIsInstance(plot(profile), tuple)

if __name__ == '__main__':
    unittest.main()