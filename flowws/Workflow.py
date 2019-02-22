import argparse
import pkg_resources

from . import DirectoryStorage

class Workflow:
    def __init__(self, stages, storage):
        self.stages = stages
        self.storage = storage

    @classmethod
    def from_JSON(cls, json_object):
        stages = json_object['stages']
        return cls(stages)

    @classmethod
    def from_command(cls, args=None, module_names='flowws_modules'):
        modules = {}
        for entry_point in pkg_resources.iter_entry_points(module_names):
            modules[entry_point.name] = entry_point.load()

        parser = argparse.ArgumentParser(
            description='Run a workflow')
        parser.add_argument('--directory', help='Storage directory to use')
        parser.add_argument('workflow', nargs=argparse.REMAINDER,
            help='Workflow description')

        args = parser.parse_args(args)

        if args.directory:
            storage = DirectoryStorage(args.directory)
        else:
            storage = DirectoryStorage()

        stages = [[]]
        for word in args.workflow:
            if word in modules:
                stages.append([])

            stages[-1].append(word)

        workflow_stages = []
        for stage in stages:
            if not stage:
                continue

            stage_name, stage_args = stage[0], stage[1:]
            stage_cls = modules[stage_name]
            workflow_stages.append(stage_cls.from_command(stage_args))

        return cls(workflow_stages, storage)

    def run(self, scope={}):
        scope = dict(scope)
        for stage in self.stages:
            stage.run(scope, self.storage)
