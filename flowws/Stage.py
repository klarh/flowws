import argparse
import logging
import sys

from . import internal

logger = logging.getLogger(__name__)

class Stage:
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
        return cls(**json_object)

    @classmethod
    def from_command(cls, args):
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
        pass
