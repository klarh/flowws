"""Save a user-defined workflow from the command line for later execution

The `flowws.freeze` utility is used to store a workflow description in
JSON form. It finds and parameterizes modules identically to
:py:mod:`flowws.run`, but saves the result to a file to run later
rather than immediately executing the workflow. Before the workflow
definition, it takes a single argument specifying the location to
store the resulting JSON file::

    python -m flowws.freeze workflow.json Module1 Module2

A `flowws_freeze` script is also installed for this command for
convenience.

"""

import argparse
import json

from . import Workflow

def main():
    parser = argparse.ArgumentParser(
        description='Save a workflow in JSON form')
    parser.add_argument('location',
        help='JSON filename to save')
    parser.add_argument('workflow', nargs=argparse.REMAINDER,
        help='Remainder of workflow description (arguments identical to flowws.run)')

    args = parser.parse_args()

    workflow = Workflow.from_command(args=args.workflow)
    json_description = workflow.to_JSON()

    with open(args.location, 'w') as f:
        json.dump(json_description, f)

if __name__ == '__main__':
    main()
