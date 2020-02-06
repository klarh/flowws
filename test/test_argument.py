
import argparse
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

    def test_argparse(self):
        args = [
            flowws.Argument('float', type=float),
            flowws.Argument('boolean', type=bool),
            flowws.Argument('complex_list', type=[(int, float)]),
        ]
        arg_names = {arg.name: arg for arg in args}

        parser = argparse.ArgumentParser()
        for arg in args:
            arg.register_parser(parser)

        command_line = ('--float 13 --boolean FaLse --complex-list 1 2 '
                        '--complex-list 3 4')
        result = {key: arg_names[key].validate_cmd(val)
                  for (key, val) in
                  vars(parser.parse_args(command_line.split())).items()}

        self.assertEqual(result['float'], 13.)
        self.assertIsInstance(result['float'], float)
        self.assertEqual(result['boolean'], False)
        self.assertIsInstance(result['boolean'], bool)
        self.assertEqual(result['complex_list'], [(1, 2.), (3, 4.)])

if __name__ == '__main__':
    unittest.main()
