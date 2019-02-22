import os

from .Storage import Storage

class DirectoryStorage(Storage):
    def __init__(self, root=os.curdir, group=None):
        if group is not None:
            self.root = os.path.join(root, group)
        else:
            self.root = root

        os.makedirs(self.root, exist_ok=True)

    def open_stream(self, full_name, mode):
        full_name = os.path.join(self.root, full_name)
        return open(full_name, mode)

    def open_file(self, full_name, mode):
        full_name = os.path.join(self.root, full_name)
        return open(full_name, mode)
