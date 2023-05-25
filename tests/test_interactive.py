
import unittest
import matplotlib
import matplotlib.pyplot as plt

from medsrtqc.core import Trace, Profile
from medsrtqc.interactive import plot, plot_trace, plot_profile

matplotlib.use('agg')


class TestPlot(unittest.TestCase):

    def test_plot(self):
        trace = Trace([1, 2, 4], adjusted=[2, 3, 5])
        profile = Profile({'PARAM': trace, 'PARAM2': trace})
        print(type(plot(trace)).__name__)
        self.assertTrue((type(plot(trace)).__name__ == 'AxesSubplot') or (type(plot(trace)).__name__ == 'Axes'))
        self.assertIsInstance(plot(profile), tuple)
        with self.assertRaises(TypeError):
            plot(None)

    def test_plot_profile(self):
        trace = Trace([1, 2, 4], adjusted=[2, 3, 5])
        profile = Profile({'PARAM': trace, 'PARAM2': trace})
        self.assertIsInstance(plot_profile(profile), tuple)
        self.assertIsInstance(plot_profile(Profile({})), tuple)

        fig, axs = plt.subplots(1, 2)
        self.assertIsInstance(plot_profile(profile, fig, axs), tuple)

    def test_plot_trace(self):
        trace = Trace(
            [1, 2, 4],
            adjusted=[2, 3, 5],
            adjusted_error=[0.5, 0.4, 0.3]
        )
        self.assertTrue((type(plot(trace)).__name__ == 'AxesSubplot') or (type(plot(trace)).__name__ == 'Axes'))

if __name__ == '__main__':
    unittest.main()
