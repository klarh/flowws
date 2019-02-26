import argparse
import re

from .PatternMatcher import match

class Argument:
    def __init__(self, name, abbreviation=None, type=None, default=None,
                 required=None, help=None, metavar=None,
                 cmd_type=None, cmd_help=None):
        self.name = name
        self.abbreviation = abbreviation
        self.type = type
        self.default = default
        self.required = required
        self.help = help
        self.metavar = metavar
        self.cmd_type = cmd_type
        self.cmd_help = cmd_help

        if self.abbreviation is not None:
            assert re.match('^-[a-z]$', self.abbreviation)

        if self.cmd_type is None:
            self.cmd_type = self.type

    def validate(self, value):
        return match(self.type, value)

    def validate_cmd(self, value):
        return self.validate(value)

    def register_parser(self, parser):
        args = ['--{}'.format(self.name.replace('_', '-'))]

        if self.abbreviation:
            args.append(self.abbreviation)

        kwargs = dict(type=self.cmd_type, default=self.default,
                      required=self.required, help=self.help,
                      metavar=self.metavar)

        type_ = self.cmd_type

        if isinstance(self.cmd_type, list):
            assert len(self.cmd_type) == 1, 'List arguments must be homogeneous, use a tuple instead'
            kwargs['default'] = []

            type_ = self.cmd_type[0]
            # for single types (i.e. [float]), accept a simple series
            # of values, for example "-x 1 2 3"
            if not isinstance(type_, tuple):
                kwargs['nargs'] = '*'
                kwargs['type'] = type_
            # for complex types (like [(str, float)]), use the append
            # action; for example "-x a 12 -x b 13"
            else:
                kwargs['action'] = 'append'

        if isinstance(type_, tuple):
            if any(isinstance(v, list) for v in type_):
                nargs = '*'
            else:
                nargs = len(type_)
            kwargs['type'] = None
            kwargs['nargs'] = nargs

        if self.cmd_help is not None:
            kwargs['help'] = self.cmd_help

        return parser.add_argument(*args, **kwargs)
