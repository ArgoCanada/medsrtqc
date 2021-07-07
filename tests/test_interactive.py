
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
        self.assertEqual(type(plot(trace)).__name__, 'AxesSubplot')
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
        self.assertEqual(
            type(plot_trace(trace, trace_attrs=('value', 'adjusted', 'adjusted_error'))).__name__,
            'AxesSubplot'
        )


if __name__ == '__main__':
    unittest.main()
