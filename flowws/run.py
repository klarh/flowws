import argparse

from . import Workflow

def main():
    workflow = Workflow.from_command()
    workflow.run()

if __name__ == '__main__':
    main()
