import argparse
import collections
import contextlib
import copy
import datetime
import functools
import importlib
import json
import pkg_resources

from .DirectoryStorage import DirectoryStorage
from .GetarStorage import GetarStorage

class Scope(dict):
    """Simple dictionary that can parse callbacks.

    A callback can be registered for a key via `set_call`. Subsequent
    calls to `scope[key]` or `scope.get(key)` will cause the callback
    to populate the scope with the callback result. Calling `set_call`
    will not necessarily add a key to the set of keys produced when
    iterating over the dictionary for performance purposes.
    """

    def __init__(self, *args, **kwargs):
        self._callbacks = {}
        super().__init__(*args, **kwargs)

    def __contains__(self, key):
        return super().__contains__(key) or key in self._callbacks

    def __copy__(self):
        result = Scope(self)
        result._callbacks = copy.copy(self._callbacks)
        return result

    def __getitem__(self, key):
        if key in self._callbacks:
            self[key] = self._callbacks.pop(key)()
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key in self._callbacks:
            return self[key]
        return super().get(key, default)

    def set_call(self, key, callback):
        """Register a callback to later retrieve a value.

        :param key: dictionary key for this object to associate the callback with
        :param callback: a parameter-free callable that returns the value to set
        """
        self._callbacks[key] = callback

class Workflow:
    """Specify a complete sequence of operations to perform.

    Workflow objects specify a sequence of stages (operations to
    perform) and a storage object to use (which could be a database,
    archive file, or simply a directory on the filesystem). In
    addition to direct creation within python, Workflows can be
    deserialized from command line and JSON-based descriptions.

    Stages are executed sequentially in the order they are given and
    each stage can pass information to later stages in a freeform way
    by settings elements of a *scope*, which is a dictionary of named
    values.

    :param stages: List of `Stage` objects specifying the operations to perform
    :param storage: `Storage` object specifying where results should be saved (default: create a DirectoryStorage using the current working directory)
    :param scope: Dictionary of key-value pairs specifying external input parameters

    """

    _additional_entry_points = collections.defaultdict(lambda: {})

    class _FakeEntryPoint:
        def __init__(self, target):
            self.target = target

        def load(self):
            return self.target

    def __init__(self, stages, storage=None, scope={}):
        if storage is None:
            storage = DirectoryStorage()

        self.stages = stages
        self.storage = storage
        self.scope = dict(scope)

    @classmethod
    def from_JSON(cls, json_object, module_names='flowws_modules'):
        """Construct a Workflow from a JSON object."""
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
            stage_type = stage_json.pop('type')
            try:
                module_name = stage_json.pop('module_name')
                module = importlib.import_module(module_name)
                stage_cls = getattr(module, stage_type)
            except (KeyError, AttributeError, ModuleNotFoundError):
                stage_cls = modules[stage_type].load()
            stages.append(stage_cls.from_JSON(stage_json))

        scope = dict(json_object.get('scope', {}))

        metadata = dict(scope.get('metadata', {}))
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

    @classmethod
    def get_named_modules(cls, module_names):
        modules = {}
        for entry_point in pkg_resources.iter_entry_points(module_names):
            modules[entry_point.name] = entry_point
        for name, entry_point in cls._additional_entry_points[module_names].items():
            modules[name] = entry_point
        return modules

    @classmethod
    def from_command(cls, args=None, module_names='flowws_modules', scope={}):
        """Construct a Workflow from a command-line description.

        Stages are found based on setuptools entry_point specified
        under `module_names`.

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

    @classmethod
    def register_module(cls, *args, module_names='flowws_modules', name=None):
        """Register a named module to be loaded inside `from_JSON` or other functions.

        This method is intended to be used as a decorator for Stage
        classes in situations such as REPL loops or notebooks, where
        modules need to be deserialized without necessarily creating a
        standalone package and registering the endpoints through the
        setuptools machinery.

        Examples::

            @flowws.Workflow.register_module
            class TestStage(flowws.Stage):
                pass

            @flowws.Workflow.register_module(name='OverruledName')
            class Stage(flowws.Stage):
                pass

        """
        if len(args) == 1:
            module = args[0]
            name = name or module.__name__
            cls._additional_entry_points[module_names][name] = \
                cls._FakeEntryPoint(module)
            return module
        elif len(args) > 1:
            raise ValueError('Too many positional arguments: {}'.format(args))

        return functools.partial(
            cls.register_module, module_names=module_names, name=name)

    def run(self):
        """Run each stage inside this workflow.

        Returns the scope after running all stages.
        """
        scope = Scope(self.scope)
        scope['workflow'] = scope['flowws.workflow'] = self
        with contextlib.ExitStack() as stack:
            scope['flowws.exit_stack'] = stack
            for stage in self.stages:
                stage.run(scope, self.storage)

        return scope

register_module = Workflow.register_module
