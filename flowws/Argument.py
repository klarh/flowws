import argparse
import re

from .PatternMatcher import identity, match, parse_bool

class Range:
    """Define a range of numeric values.

    :param min: minimum value of the range
    :param max: maximum value of the range
    :param inclusive: boolean or two booleans indicating whether the left and right endpoints should be included (True) or not in the range
    """
    def __init__(self, min, max, inclusive=False):
        self.min = min
        self.max = max
        try:
            self.inclusive = [bool(x) for x in inclusive[:2]]
        except TypeError:
            self.inclusive = [bool(inclusive), bool(inclusive)]

    def __contains__(self, x):
        result = self.min < x < self.max
        if self.inclusive[0]:
            result = result or self.min <= x
        if self.inclusive[1]:
            result = result or x <= self.max
        return result

_type_parser_remap = {bool: parse_bool}

class Argument:
    def __init__(self, name, abbreviation=None, type=identity, default=None,
                 required=None, help=None, metavar=None,
                 cmd_type=None, cmd_help=None, valid_values=None):
        """Encode the type and documentation for a stage argument.

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
        :param valid_values: If given, the value for this argument should lie within the given parameter
        """
        self.name = name
        self.abbreviation = abbreviation
        self.type = type
        self.default = default
        self.required = required
        self.help = help
        self.metavar = metavar
        try:
            self.cmd_type = _type_parser_remap.get(cmd_type, cmd_type)
        except TypeError: # cmd_type was unhashable
            self.cmd_type = cmd_type
        self.cmd_help = cmd_help
        self.valid_values = valid_values

        if self.abbreviation is not None:
            assert re.match('^-[a-z]$', self.abbreviation)

        if self.cmd_type is None:
            try:
                self.cmd_type = _type_parser_remap.get(self.type, self.type)
            except TypeError: # type was unhashable
                self.cmd_type = self.type

    def validate(self, value):
        """Coerce argument values into the pattern given for this argument."""
        result = match(self.type, value)
        if self.valid_values is not None and result not in self.valid_values:
            msg = ('Value of parameter {} ("{}") not within the given '
                   'valid set {}'.format(self.name, result, self.valid_values))
            raise ValueError(msg)
        return result

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
