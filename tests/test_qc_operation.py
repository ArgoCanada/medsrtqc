
import unittest
from io import StringIO
import contextlib
import sys

from medsrtqc.core import Profile, Trace
from medsrtqc.qc.operation import QCOperation, QCOperationError, QCOperationContext, QCOperationProfileContext


class TestQCOperation(unittest.TestCase):

    def test_error(self):
        with self.assertRaises(QCOperationError):
            raise QCOperationError()

    def test_default_context(self):
        context = QCOperationContext()
        profile = Profile({'key': Trace([1])})

        context.update_trace(profile, 'key', Trace([2]))
        self.assertEqual(profile['key'].value[0], 2)

        output = StringIO()
        with contextlib.redirect_stderr(output):
            context.log(profile, 'the message')
        self.assertRegex(output.getvalue(), 'the message$')

        with self.assertRaises(QCOperationError):
            context.error(profile, 'stop!')

        # test dummy matplotlib methods
        with context.pyplot(profile) as plt:
            self.assertIs(plt.plot(), plt)
            self.assertIs(plt.scatter(), plt)
            self.assertIs(plt.errorbar(), plt)
            self.assertIs(plt.subplots()[0], plt)
            self.assertIs(plt.subplot(), plt)

        # test error handling
        with context.pyplot(profile):
            raise AttributeError('this should be silently squashed')

        with self.assertRaises(ValueError):
            with context.pyplot(profile):
                raise ValueError('this error should be caught')

    def test_abstract_operation(self):
        profile = Profile({'key': Trace([1])})
        op = QCOperation()
        op.profile = profile
        op.context = QCOperationContext()

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

    def test_custom_context(self):
        class CustomContext(QCOperationContext):
            def log(self, profile, message):
                print('a completely unrelated message', file=sys.stderr)

        context = CustomContext()
        output = StringIO()
        with contextlib.redirect_stderr(output):
            context.log(Profile(), 'something')
        self.assertEqual(output.getvalue().strip(), 'a completely unrelated message')

        op = QCOperation()
        output = StringIO()
        with contextlib.redirect_stderr(output):
            with QCOperationProfileContext(op, context=context):
                op.log('something')
        self.assertEqual(output.getvalue().strip(), 'a completely unrelated message')


if __name__ == '__main__':
    unittest.main()
