import os

from .Storage import Storage

class DirectoryStorage(Storage):
    """Stores files directly on the filesystem."""
    def __init__(self, root=os.curdir, group=None):
        self.root = root
        self.group = group

        if group is not None:
            self.full_prefix = os.path.join(root, group)
        else:
            self.full_prefix = root

        os.makedirs(self.full_prefix, exist_ok=True)

    def to_JSON(self):
        return dict(type='DirectoryStorage', root=self.root, group=self.group)

    def open_stream(self, full_name, mode):
        full_name = os.path.join(self.full_prefix, full_name)
        return open(full_name, mode)

    def open_file(self, full_name, mode):
        full_name = os.path.join(self.full_prefix, full_name)
        return open(full_name, mode)
