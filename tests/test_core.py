
import unittest
import numpy as np
from medsrtqc.core import Trace, Profile


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
        profile = Profile({'some_param': trace}, {'some_meta': 'some_value'})
        self.assertTrue(np.all(profile['some_param'].value == trace.value))
        self.assertEqual(list(profile.keys()), ['some_param'])
        for key in profile:
            self.assertTrue(np.all(profile[key].value == trace.value))
        self.assertTrue('some_param' in profile)

        profile['some other param'] = Trace([])
        self.assertTrue('some other param' in profile)

        self.assertEqual(profile.meta_keys(), ('some_meta', ))
        self.assertEqual(profile.meta('some_meta'), 'some_value')
        profile.set_meta('other meta', 'other value')
        self.assertEqual(profile.meta('other meta'), 'other value')

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
        with self.assertRaises(NotImplementedError):
            profile.meta('some key')
        with self.assertRaises(NotImplementedError):
            profile.set_meta('some key', 'some value')
        with self.assertRaises(NotImplementedError):
            profile.meta_keys()


if __name__ == '__main__':
    unittest.main()
