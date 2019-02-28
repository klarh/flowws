import argparse
import re

from .PatternMatcher import match

class Argument:
    def __init__(self, name, abbreviation=None, type=None, default=None,
                 required=None, help=None, metavar=None,
                 cmd_type=None, cmd_help=None):
        """Encode the type and documentation for a stage argument

        Argument objects store the details and parsing logic for
        Stages, which can be given arguments directly within python,
        via a JSON specification, or by command-line arguments.

        Argument types are specified by *patterns*, which are simply
        python type callables in the simplest case (i.e. str, float,
        int). More complex types can be specified; for example, a type
        of (str, float) indicates that two arguments should be taken
        on the command line and that the first should be parsed as a
        string and the second as a floating-point number.

        :param name: short name of the argument
        :param abbreviation: Short string for the command line parser, if needed (i.e. '-a')
        :param type: Pattern to coerce the argument into. See the section on patterns above.
        :param default: Default value
        :param required: Set to True to make this argument be required for the stage
        :param help: Documentation string for the argument
        :param metavar: If given, indicate the names of argument values on the command line
        :param cmd_type: If given, use a different pattern for command-line parsing
        :param cmd_help: If given, use a different documentation string for command-line parsing
        """
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
        """Coerce argument values into the pattern given for this argument"""
        return match(self.type, value)

    def validate_cmd(self, value):
        """Coerce argument values from the command line into the pattern given for this argument.

        By default this uses the same logic as `validate`, but it can
        be overridden for custom command line parsing (i.e. if a
        specialized `cmd_type` was given).
        """
        return self.validate(value)

    def register_parser(self, parser):
        """Register the contents of this argument into an argparse parser."""
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
