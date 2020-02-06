
import unittest

import flowws
from flowws import Argument as Arg

class StageForTesting(flowws.Stage):
    ARGS = [
        Arg('required_value', required=True),
        Arg('defaulted_value', default='default'),
    ]

class TestStage(unittest.TestCase):
    def test_required(self):
        with self.assertRaises(ValueError):
            flowws.Workflow([StageForTesting()], flowws.DirectoryStorage()).run()

        with self.assertRaises(SystemExit):
            StageForTesting.from_command(['--defaulted-value', '3'])

    def test_default(self):
        stage = StageForTesting(required_value=1)
        self.assertEqual(stage.arguments['defaulted_value'], 'default')

        stage = StageForTesting(required_value=1, defaulted_value=3)
        self.assertEqual(stage.arguments['defaulted_value'], 3)

if __name__ == '__main__':
    unittest.main()
