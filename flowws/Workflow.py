import argparse
import datetime
import json
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
    :param scope: Dictionary of key-value pairs specifying external input parameters
    """
    def __init__(self, stages, storage, scope={}):
        self.stages = stages
        self.storage = storage
        self.scope = dict(scope)

    @classmethod
    def from_JSON(cls, json_object, module_names='flowws_modules'):
        """Construct a Workflow from a JSON object"""
        modules = cls.get_named_modules(module_names)

        storage_args = dict(json_object['storage'])
        storage_type = storage_args.pop('type', 'DirectoryStorage')
        if storage_type == 'DirectoryStorage':
            storage = DirectoryStorage(**storage_args)
        elif storage_type == 'GetarStorage':
            storage = GetarStorage(**storage_args)
        else:
            raise NotImplementedError()

        stages_json = json_object['stages']
        stages = []
        for stage_json in stages_json:
            stage_json = dict(stage_json)
            stage_cls = modules[stage_json.pop('type')].load()
            stages.append(stage_cls.from_JSON(stage_json))

        scope = json_object.get('scope', {})

        metadata = scope.get('metadata', {})
        metadata['invocation'] = dict(
            name='from_JSON', source=json_object,
            module_names=module_names,
            time=datetime.datetime.now().isoformat(),
            time_utc=datetime.datetime.utcnow().isoformat(),
        )
        scope['metadata'] = metadata

        return cls(stages, storage, scope)

    def to_JSON(self):
        stages = [stage.to_JSON() for stage in self.stages]
        result = dict(storage=self.storage.to_JSON(),
                      stages=stages,
                      scope=self.scope)
        return result

    @staticmethod
    def get_named_modules(module_names):
        modules = {}
        for entry_point in pkg_resources.iter_entry_points(module_names):
            modules[entry_point.name] = entry_point
        return modules

    @classmethod
    def from_command(cls, args=None, module_names='flowws_modules', scope={}):
        """Construct a Workflow from a command-line description.

        Stages are found based on setuptools entry_point specified
        under `module_names`

        :param args: List of command-line arguments (list of strings)
        :param module_names: setuptools entry_point to use for module searches
        :param scope: Dictionary of initial key-value pairs to pass to child Stages
        """
        parser = argparse.ArgumentParser(
            description='Run a workflow')
        parser.add_argument('--storage', help='Storage location to use')
        parser.add_argument('-d', '--define', nargs=2, action='append', default=[],
            help='Define a workflow-specific value')
        parser.add_argument('-m', '--module-names', default=module_names,
            help='Registered module entry_point to search')
        parser.add_argument('workflow', nargs=argparse.REMAINDER,
            help='Workflow description')

        args_str = args
        args = parser.parse_args(args)

        modules = cls.get_named_modules(args.module_names)

        scope = dict(scope)
        storage = None

        metadata = scope.get('metadata', {})
        metadata['invocation'] = dict(
            name='from_command', arguments=args_str,
            module_names=module_names, initial_scope=dict(scope),
            time=datetime.datetime.now().isoformat(),
            time_utc=datetime.datetime.utcnow().isoformat(),
        )
        scope['metadata'] = metadata

        if args.storage:
            location = args.storage

            if any(location.endswith(suffix)
                   for suffix in ('.zip', '.tar', '.sqlite')):
                storage = GetarStorage(location)
            else:
                storage = DirectoryStorage(location)
        elif storage is None:
            storage = DirectoryStorage()

        if len(args.workflow) == 1 and args.workflow[0].endswith('.json'):
            with open(args.workflow[0], 'r') as f:
                json_description = json.load(f)
            template_workflow = cls.from_JSON(json_description, module_names)
            scope.update(template_workflow.scope)
            storage = template_workflow.storage
            workflow_stages = template_workflow.stages
        else:
            stages = []
            for word in args.workflow:
                if word in modules:
                    stages.append([])

                try:
                    stages[-1].append(word)
                except IndexError:
                    raise RuntimeError(
                        'Failed finding module {}'.format(word))

            workflow_stages = []
            for description in stages:
                if not description:
                    continue

                stage_name, stage_args = description[0], description[1:]
                stage_cls = modules[stage_name].load()
                stage = stage_cls.from_command(stage_args)
                assert stage is not None, 'Stage.from_command returned None'

                workflow_stages.append(stage)

        for (name, val) in args.define:
            try:
                val = eval(val)
            except:
                pass

            scope[name] = val

        return cls(workflow_stages, storage, scope)

    def run(self):
        """Run each stage inside this workflow"""
        scope = dict(self.scope)
        for stage in self.stages:
            stage.run(scope, self.storage)
