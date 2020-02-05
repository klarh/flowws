
import importlib
import logging

logger = logging.getLogger(__name__)

class FailedImport:
    """Module that failed to import."""
    def __init__(self, exception):
        self.exception = exception

    def __getattr__(self, *args, **kwargs):
        return self

    def __call__(self, *args, **kwargs):
        raise self.exception

def try_to_import(pkg, name, current_pkg=None):
    """Import an attribute from a module, or return an error-producing fake.

    This method is provided as a convenience for libraries that want
    to easily expose modules with a variety of prerequisite libraries
    without forcing the user to install prerequisites for the modules
    they do not use. The fake is produced if an import fails while
    importing the given package.

    :param name: Name of the attribute to return from the module
    :param pkg: Package name (can be relative)
    :param current_pkg: Name of the current package to use (i.e. if `pkg` is relative)
    :returns: Either the attribute from the successfully-imported module, or a fake module object that will produce an error if evaluated

    """
    try:
        mod = importlib.import_module(pkg, current_pkg)
        result = getattr(mod, name)
    except ImportError as e:
        result = FailedImport(e)

    return result
