import os
import shutil
import tempfile

class FileWriterBuffer:
    def __init__(self, filename, stream_target):
        self.filename = filename
        self.stream_target = stream_target
        self.temp_buffer = tempfile.NamedTemporaryFile(suffix=filename)
        self.name = self.temp_buffer.name

    def write(self, contents):
        return self.temp_buffer.write(contents)

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def close(self):
        self.temp_buffer.seek(0)
        shutil.copyfileobj(self.temp_buffer, self.stream_target)
        self.stream_target.close()
        self.temp_buffer.close()

class NoopBuffer:
    def __init__(self, filename):
        self.name = filename

    def write(self, *args, **kwargs):
        pass

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def close(self):
        pass

class Storage:
    """Base class for file storage.

    Storage objects expose methods for reading and writing of files
    which could actually be backed by a database or archive file, for
    example.

    """
    def open(self, filename, mode='r', modifiers=[], on_filesystem=False, noop=False):
        """Open a file stored within this object.

        :param filename: Name of the (internal) file
        :param mode: One of 'r' (read), 'w' (write/overwrite), 'a' (append) and, optionally, 'b' (open in binary mode)
        :param modifiers: List of filename modifiers which will be appended to the filename, respecting the file suffix
        :param on_filesystem: If True, the file must exist as a real file on the filesystem; otherwise, a python stream object may be returned
        :param noop: If True, return a dummy file object instead that does nothing
        """
        prefix, suffix = os.path.splitext(filename)
        full_name = '.'.join([prefix] + modifiers + [suffix[1:]])

        if noop:
            return NoopBuffer(full_name)

        if on_filesystem:
            return self.open_file(full_name, mode)

        return self.open_stream(full_name, mode)

    def open_stream(self, full_name, mode):
        """Open a file stored within this object as a stream."""
        raise NotImplementedError('Storage.open_stream')

    def open_file(self, full_name, mode):
        """Open a file stored within this object as a real file on the filesystem.

        The default implementation simply copies a stream object onto
        the filesystem.
        """
        if 'w' in mode or 'a' in mode:
            return FileWriterBuffer(
                full_name, self.open_stream(full_name, mode))

        result = tempfile.NamedTemporaryFile(suffix=full_name)
        with self.open_stream(full_name, mode) as src:
            shutil.copyfileobj(src, result)
        result.seek(0)
        return result
