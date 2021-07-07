
import unittest
import numpy as np
from medsrtqc.core import Trace, Profile, ProfileList


class TestCore(unittest.TestCase):

    def test_trace(self):
        trace = Trace([1, 2, 3])
        self.assertTrue(np.all(trace.value == np.array([1, 2, 3])))
        with self.assertRaises(ValueError):
            Trace([1, 2, 3], [1, 2, 3, 4])

    def test_trace_repr(self):
        self.assertRegex(repr(Trace([])), r'^Trace\(\s*value=\[\]')
        self.assertRegex(repr(Trace([1, 2, 3])), r'^Trace\(')
        self.assertRegex(repr(Trace([1, 2, 3, 4, 5, 6, 7])), r'\[1 values\]')

    def test_profile(self):
        trace = Trace([1, 2, 3])
        profile = Profile({'some_param': trace})
        self.assertTrue(np.all(profile['some_param'].value == trace.value))
        self.assertEqual(list(profile.keys()), ['some_param'])
        for key in profile:
            self.assertTrue(np.all(profile[key].value == trace.value))
        self.assertTrue('some_param' in profile)

        profile['some other param'] = Trace([])
        self.assertTrue('some other param' in profile)

    def test_abstract_profile(self):
        profile = Profile()
        with self.assertRaises(NotImplementedError):
            profile['some key']
        with self.assertRaises(NotImplementedError):
            profile['some key'] = 'some value'
        with self.assertRaises(NotImplementedError):
            profile.keys()
        with self.assertRaises(NotImplementedError):
            'some key' in profile

    def test_abstract_profile_list(self):
        profile_list = ProfileList()
        with self.assertRaises(NotImplementedError):
            profile_list[0]
        with self.assertRaises(NotImplementedError):
            profile_list[0] = 'some value'

    def test_profile_list(self):
        profile = Profile()
        profile_list = ProfileList([profile])
        self.assertEqual(len(profile_list), 1)
        self.assertIsNot(profile_list[0], profile)
        self.assertIsNone(profile_list[0]._Profile__data)
        for p in profile_list:
            self.assertIsNone(p._Profile__data)

        profile_list[0] = Profile({'param': Trace([])})
        self.assertIsNotNone(profile_list[0]._Profile__data)


if __name__ == '__main__':
    unittest.main()
