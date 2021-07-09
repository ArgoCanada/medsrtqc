
import unittest
import numpy as np
import contextlib
import sys
from io import StringIO
from medsrtqc.core import QCOperation, QCOperationApplier, QCOperationError, Trace, Profile, ProfileList


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
        with self.assertRaises(NotImplementedError):
            len(profile_list)

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


class TestCoreQC(unittest.TestCase):

    def test_error(self):
        with self.assertRaises(QCOperationError):
            raise QCOperationError()

    def test_default_applier(self):
        applier = QCOperationApplier()
        profile = Profile({'key': Trace([1])})

        applier.update_trace(profile, 'key', Trace([2]))
        self.assertEqual(profile['key'].value[0], 2)

        output = StringIO()
        with contextlib.redirect_stderr(output):
            applier.log(profile, 'the message')
        self.assertRegex(output.getvalue(), 'the message$')

        with self.assertRaises(QCOperationError):
            applier.error(profile, 'stop!')

        # test dummy matplotlib methods
        with applier.pyplot(profile) as plt:
            self.assertIs(plt.plot(), plt)
            self.assertIs(plt.scatter(), plt)
            self.assertIs(plt.errorbar(), plt)
            self.assertIs(plt.subplots()[0], plt)
            self.assertIs(plt.subplot(), plt)

        # test error handling
        with applier.pyplot(profile):
            raise AttributeError('this should be silently squashed')

        with self.assertRaises(ValueError):
            with applier.pyplot(profile):
                raise ValueError('this error should be caught')

    def test_abstract_operation(self):
        profile = Profile({'key': Trace([1])})
        op = QCOperation()
        op.profile = profile

        op.update_trace('key', Trace([2]))
        self.assertEqual(profile['key'].value[0], 2)

        output = StringIO()
        with contextlib.redirect_stderr(output):
            op.log('the message')
        self.assertRegex(output.getvalue(), 'the message$')

        with self.assertRaises(QCOperationError):
            op.error('stop!')

        with op.pyplot() as plt:
            self.assertIs(plt.plot(), plt)

        with self.assertRaises(NotImplementedError):
            op.run(profile)

    def test_custom_applier(self):
        class CustomApplier(QCOperationApplier):
            def log(self, profile, message):
                print('a completely unrelated message', file=sys.stderr)

        applier = CustomApplier()
        output = StringIO()
        with contextlib.redirect_stderr(output):
            applier.log(Profile(), 'something')
        self.assertEqual(output.getvalue().strip(), 'a completely unrelated message')

        op = QCOperation(applier=applier)
        output = StringIO()
        with contextlib.redirect_stderr(output):
            op.log('something')
        self.assertEqual(output.getvalue().strip(), 'a completely unrelated message')


if __name__ == '__main__':
    unittest.main()
