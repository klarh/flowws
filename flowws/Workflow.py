import argparse
import pkg_resources

from .DirectoryStorage import DirectoryStorage
from .GetarStorage import GetarStorage

class Workflow:
    def __init__(self, stages, storage):
        self.stages = stages
        self.storage = storage

    @classmethod
    def from_JSON(cls, json_object):
        stages = json_object['stages']
        return cls(stages)

    @classmethod
    def run_from_command(cls, args=None, module_names='flowws_modules', scope={}):
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
        scope = dict(scope)
        for stage in self.stages:
            stage.run(scope, self.storage)
