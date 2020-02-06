
import tempfile
import os
import unittest

import flowws

from internal import StorageTestBase

class TestDirectoryStorage(unittest.TestCase, StorageTestBase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        dirname = os.path.join(self.tempdir.name, 'test')
        self.storage = flowws.DirectoryStorage(dirname)

    def tearDown(self):
        self.tempdir.cleanup()

if __name__ == '__main__':
    unittest.main()
