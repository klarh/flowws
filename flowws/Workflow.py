import argparse
import pkg_resources

from .DirectoryStorage import DirectoryStorage
from .GetarStorage import GetarStorage

class Workflow:
    """Specify a complete sequence of operations to perform

    Workflow objects specify a sequence of stages (operations to
    perform) and a storage object to use (which could be a database,
    archive file, or simply a directory on the filesystem). In
    addition to direct creation within python, Workflows can be
    deserialized from command line and JSON-based descriptions.

    :param stages: List of `Stage` objects specifying the operations to perform
    :param storage: `Storage` object specifying where results should be saved
    """
    def __init__(self, stages, storage):
        self.stages = stages
        self.storage = storage

    @classmethod
    def from_JSON(cls, json_object):
        """Construct a Workflow from a JSON object"""
        stages = json_object['stages']
        # TODO add storage deserialization
        return cls(stages)

    @classmethod
    def run_from_command(cls, args=None, module_names='flowws_modules', scope={}):
        """Construct a Workflow from a command-line description.

        Stages are found based on setuptools entry_point specified
        under `module_names`

        :param args: List of command-line arguments (list of strings)
        :param module_names: setuptools entry_point to use for module searches
        :param scope: Dictionary of initial key-value pairs to pass to child Stages
        """
        modules = {}
        for entry_point in pkg_resources.iter_entry_points(module_names):
            modules[entry_point.name] = entry_point.load()

        parser = argparse.ArgumentParser(
            description='Run a workflow')
        parser.add_argument('--storage', help='Storage location to use')
        parser.add_argument('-d', '--define', nargs=2, action='append', default=[],
            help='Define a workflow-specific value')
        parser.add_argument('workflow', nargs=argparse.REMAINDER,
            help='Workflow description')

        args = parser.parse_args(args)

        scope = dict(scope)
        for (name, val) in args.define:
            try:
                val = eval(val)
            except:
                pass

            scope[name] = val

        if args.storage:
            location = args.storage

            if any(location.endswith(suffix)
                   for suffix in ('.zip', '.tar', '.sqlite')):
                storage = GetarStorage(location)
            else:
                storage = DirectoryStorage(location)
        else:
            storage = DirectoryStorage()

        stages = []
        for word in args.workflow:
            if word in modules:
                stages.append([])

            stages[-1].append(word)

        workflow_stages = []
        for description in stages:
            if not description:
                continue

            stage_name, stage_args = description[0], description[1:]
            stage_cls = modules[stage_name]
            stage = stage_cls.from_command(stage_args)
            assert stage is not None, 'Stage.from_command returned None'

            workflow_stages.append(stage)

        return cls(workflow_stages, storage).run(scope)

    def run(self, scope={}):
        """Run each stage inside this workflow"""
        scope = dict(scope)
        for stage in self.stages:
            stage.run(scope, self.storage)
