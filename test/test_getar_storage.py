
import tempfile
import os
import unittest

import flowws

from internal import StorageTestBase

class TestTarStorage(unittest.TestCase, StorageTestBase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        filename = os.path.join(self.tempdir.name, 'test.tar')
        self.storage = flowws.GetarStorage(filename)

    def tearDown(self):
        self.tempdir.cleanup()

class TestZipStorage(unittest.TestCase, StorageTestBase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        filename = os.path.join(self.tempdir.name, 'test.zip')
        self.storage = flowws.GetarStorage(filename)

    def tearDown(self):
        self.tempdir.cleanup()

class TestSqliteStorage(unittest.TestCase, StorageTestBase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        filename = os.path.join(self.tempdir.name, 'test.sqlite')
        self.storage = flowws.GetarStorage(filename)

    def tearDown(self):
        self.tempdir.cleanup()

if __name__ == '__main__':
    unittest.main()
