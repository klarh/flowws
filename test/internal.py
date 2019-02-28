import os

class StorageTestBase:
    def test_basic_creation(self):
        with self.storage.open('test_file', 'w') as f:
            f.write('1')

        with self.storage.open('test_file', 'a') as f:
            f.write('2')

        with self.storage.open('test_file', 'r') as f:
            self.assertEqual(f.read(), '12')

    def test_binary(self):
        with self.storage.open('test_file', 'wb') as f:
            f.write(b'1')

        with self.storage.open('test_file', 'ab') as f:
            f.write(b'2')

        with self.storage.open('test_file', 'rb') as f:
            self.assertEqual(f.read(), b'12')

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            with self.storage.open('new_file', 'r') as f:
                pass

        # appending to a file that doesn't exist should just create it
        with self.storage.open('new_file', 'a') as f:
            pass

    def test_has_filename(self):
        with self.storage.open('test.txt', 'a', on_filesystem=True) as f:
            self.assertTrue(os.path.exists(f.name))
