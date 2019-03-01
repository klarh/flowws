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
