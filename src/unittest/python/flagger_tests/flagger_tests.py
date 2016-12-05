from unittest import TestCase

from flaggers.flagger import Flagger


class FlaggerTest(TestCase):
    def setUp(self):
        class TestClass(Flagger):
            pass

        self.TestClass = TestClass

    def test_should_raise_error_if_method_not_implemented(self):
        test_class = self.TestClass('ms_file')
        with self.assertRaisesRegexp(NotImplementedError, 'Should have implemented this'):
            test_class.get_bad_baselines()