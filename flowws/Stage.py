import argparse
import inspect
import logging
import sys

from . import internal

logger = logging.getLogger(__name__)

def add_stage_arguments(cls):
    """Adds the arguments specified in a class's ARGS entry to its docstring"""

    if cls.__doc__ is None:
        cls.__doc__ = ''

    lines = inspect.cleandoc(cls.__doc__).splitlines()
    # have only one blank line before args
    while lines and (not lines[-1] or lines[-1].isspace()):
        lines.pop()
    lines.append('')

    for arg in cls.ARGS:
        lines.append(':param {}: {}'.format(arg.name, arg.help))

    cls.__doc__ = '\n'.join(lines)

    return cls

class Stage:
    """Base class for the building blocks of workflows

    Stage objects specify a discrete set of operations within a
    Workflow. Each Stage object has its own set of parameters and
    functionality that are then run in sequence when the workflow is
    run.

    Stages can be instantiated within python by directly passing in
    arguments they take as keyword arguments, for example::

        stages = [Initialize(seed=13), Run(parameter=1.5)]

    Stages also can be instantiated from the command line using
    `flowws.command`::

        python -m flowws.command Initialize --seed 13 Run --parameter 1.5

    """
    ArgumentSpecification = internal.ArgumentSpecification

    ARGS = []

    def __init__(self, **kwargs):
        usable_args = {arg.name: arg for arg in self.ARGS}
        unused_args = []
        arg_values = {arg.name: arg.default for arg in self.ARGS
                      if arg.default is not None}

        for arg_name in kwargs:
            if arg_name in usable_args:
                specification = usable_args[arg_name]
                value = specification.validate(kwargs[arg_name])
                arg_values[arg_name] = value
            else:
                unused_args.append(arg_name)

        self.arguments = arg_values
        self.unused_arguments = unused_args

        if self.unused_arguments:
            logger.warning(
                'Unused arguments found for stage: {}'.format(self.unused_arguments))

    @classmethod
    def from_JSON(cls, json_object):
        """Initialize this stage from a JSON representation"""
        return cls(**json_object)

    @classmethod
    def from_command(cls, args):
        """Initialize this stage from a command-line description"""
        parser = argparse.ArgumentParser(
            prog=cls.__name__, description=cls.__doc__)

        # map arg name -> Arg object
        arg_objects = {}
        for arg in cls.ARGS:
            arg_objects[arg.name] = arg
            arg.register_parser(parser)

        arguments = {key: arg_objects[key].validate_cmd(val)
                     for (key, val) in vars(parser.parse_args(args)).items()
                     if val is not None}
        return cls(**arguments)

    def run(self, scope, storage):
        """Run the contents of this stage"""
        pass
