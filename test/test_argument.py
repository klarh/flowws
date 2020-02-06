
import unittest

import flowws

class TestArgument(unittest.TestCase):
    def test_parse_int(self):
        arg = flowws.Argument('test', type=int)

        for test in [10, 10., '10']:
            result = arg.validate(test)
            self.assertEqual(result, 10)
            self.assertIsInstance(result, int)

    def test_parse_bool(self):
        arg = flowws.Argument('test', type=bool)

        false_values = ['0', 0, False, 'false']
        true_values = ['-1', '1', 1, True, 'true']

        for test in false_values:
            self.assertEqual(arg.validate(test), False)

        for test in true_values:
            self.assertEqual(arg.validate(test), True)

    def test_parse_complex(self):
        arg = flowws.Argument('test', type=[int])

        for test in [10, 10., '10']:
            result = arg.validate([test] + [2, 3, 4])
            self.assertEqual(len(result), 4)
            self.assertEqual(result[0], 10)
            self.assertIsInstance(result[0], int)
