import os
import shutil
import tempfile

class FileWriterBuffer:
    def __init__(self, filename, stream_target):
        self.filename = filename
        self.stream_target = stream_target
        self.temp_buffer = tempfile.NamedTemporaryFile(filename)
        self.name = self.temp_buffer.name

    def write(self, contents):
        return self.temp_buffer.write(contents)

    def __enter__(self):
        return self

    def __exit__(self):
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

    def open(self, filename, mode='r', modifiers=[], on_filesystem=False, noop=False):
        prefix, suffix = os.path.splitext(filename)
        full_name = '.'.join([prefix] + modifiers + [suffix[1:]])

        if noop:
            return NoopBuffer(full_name)

        if on_filesystem:
            return self.open_file(full_name, mode)

        return self.open_stream(full_name, mode)

    def open_stream(self, full_name, mode):
        raise NotImplementedError('Storage.open_stream')

    def open_file(self, full_name, mode):
        if 'w' in mode:
            return FileWriterBuffer(
                full_name, self.open_stream(full_name, mode))
        else:
            result = tempfile.NamedTemporaryFile(full_name)
            with self.open_stream(full_name, mode) as src:
                shutil.copyfileobj(src, result)
            result.seek(0)
            return result
