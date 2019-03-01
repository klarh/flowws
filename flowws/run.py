"""Directly run a user-defined workflow from the command line

The `flowws.run` utility is used to execute a workflow from a brief,
text-only description. It works by finding modules installed using a
particular setuptools `entry_point`, which each parse their own
command-line parameters in their own way. Automatically-generated
documentation can be accessed in the standard way for `flowws.run`
via::

    python -m flowws.run -h

Automatically-generated documentation for any module (for this
example, simply named Module) as::

    python -m flowws.run Module -h

A complete workflow specification using modules Module1 and Module2
may look something like this::

    python -m flowws.run Module1 --param-1 x --param-2 y Module2

JSON workflows defined by :py:mod:`flowws.freeze` can also be executed
using `flowws.run`::

    python -m flowws.run workflow.json

A `flowws_run` script is also installed for this command for
convenience.

"""

import argparse

from . import Workflow

def main():
    workflow = Workflow.from_command()
    workflow.run()

if __name__ == '__main__':
    main()
