import tempfile
import io

from .Storage import Storage

class GetarBinaryBuffer(io.BytesIO):
    def __init__(self, gtar_file, target_path, mode):
        super(GetarBinaryBuffer, self).__init__()
        self.gtar_file = gtar_file
        self.target_path = target_path

        if 'a' in mode:
            contents = self.gtar_file.readBytes(self.target_path)
            if contents:
                self.write(contents)

    def close(self):
        self.gtar_file.writeBytes(self.target_path, self.getvalue())
        super(GetarBinaryBuffer, self).close()

class GetarTextBuffer(io.StringIO):
    def __init__(self, gtar_file, target_path, mode):
        super(GetarTextBuffer, self).__init__()
        self.gtar_file = gtar_file
        self.target_path = target_path

        if 'a' in mode:
            contents = self.gtar_file.readStr(self.target_path)
            if contents:
                self.write(contents)

    def close(self):
        self.gtar_file.writeStr(self.target_path, self.getvalue())
        super(GetarTextBuffer, self).close()

class GetarStorage(Storage):
    """Class to store files as records of getar-format files.

    These can be zip, tar, or sqlite-formatted archives. Note that zip
    and tar files will currently accumulate copies of files as they
    are appended to or overwritten.
    """
    def __init__(self, target, group=None):
        try:
            import gtar
        except ImportError:
            raise ImportError('libgetar must be installed to use GetarStorage')

        self.target = target
        self.group = group

        self.gtar_file = gtar.GTAR(self.target, 'a')

    def to_JSON(self):
        return dict(type='GetarStorage', target=self.target, group=self.group)

    def open_stream(self, full_name, mode):
        if self.group is not None:
            full_name = os.path.join(self.group, full_name)

        if 'w' in mode or 'a' in mode:
            if 'b' in mode:
                return GetarBinaryBuffer(self.gtar_file, full_name, mode)

            return GetarTextBuffer(self.gtar_file, full_name, mode)

        if 'b' in mode:
            contents = self.gtar_file.readBytes(full_name)
            if not contents:
                raise FileNotFoundError()
            return io.BytesIO(contents)

        contents = self.gtar_file.readStr(full_name)
        if not contents:
            raise FileNotFoundError()
        return io.StringIO(contents)
