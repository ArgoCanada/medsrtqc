
import unittest
import numpy as np
from medsrtqc.core import Trace, Profile, ProfileList


class TestCore(unittest.TestCase):

    def test_trace(self):
        trace = Trace([1, 2, 3])
        self.assertTrue(np.all(trace.value == np.array([1, 2, 3])))

    def test_trace_repr(self):
        self.assertRegex(repr(Trace(np.array([]))), r'^Trace\(\s*value=\[\]')

    def test_profile(self):
        trace = Trace(np.array([1, 2, 3]))
        profile = Profile({'some_param': trace})
        self.assertTrue(np.all(profile['some_param'].value == trace.value))
        self.assertEqual(list(profile.keys()), ['some_param'])
        for key in profile:
            self.assertTrue(np.all(profile[key].value == trace.value))

    def test_abstract_profile(self):
        profile = Profile()
        with self.assertRaises(NotImplementedError):
            profile['some key']
        with self.assertRaises(NotImplementedError):
            profile.keys()

    def test_profile_list(self):
        profile = Profile()
        profile_list = ProfileList([profile])
        self.assertEqual(len(profile_list), 1)
        self.assertIs(profile_list[0], profile)
        for p in profile_list:
            self.assertIs(p, profile)


if __name__ == '__main__':
    unittest.main()