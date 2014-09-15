import abc
import zipfile
import tarfile


def open_archive(filename):
    """
    Opens an archive using the appropriate opener depending on the type.

    Strategy:

        Try opening with the most appropriate opener for a file with the given
        extension, then fallback trying with others.

    :param filename:

        Name of the file to be opened as an archive
    """

    openers = [
        TarArchive,
        ZipArchive,
    ]

    _parts = filename.split('.')

    # This is a .zip
    if _parts[-1].lower() == 'zip':
        openers.remove(ZipArchive)
        openers.insert(0, ZipArchive)

    # This is a .tar or .tar.X
    if _parts[-1].lower() == 'tar' or (
            len(_parts) > 1 and _parts[-2].lower() == 'tar'):
        openers.remove(TarArchive)
        openers.insert(0, TarArchive)

    for opener in openers:
        try:
            return opener(filename)
        except ArchiveOpenFailure:
            pass

    raise ValueError("Unable to open archive: {0}".format(filename))


class ArchiveOpenFailure(Exception):
    pass


class BaseArchive(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, filename):
        pass

    @abc.abstractmethod
    def __iter__(self):
        pass

    def get_members(self):
        return list(self)

    @abc.abstractmethod
    def get(self, name):
        pass


class BaseArchivedFile(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, archive, name, **attrs):
        self.archive = archive
        self.name = name
        self._attrs = {
            'size': None,
        }
        self._attrs.update(attrs)

    @abc.abstractmethod
    def open(self):
        """Return a descriptor associated with this file"""
        pass

    def __getattr__(self, name):
        try:
            return self._attrs[name]
        except KeyError:
            raise AttributeError(name)


class TarArchive(BaseArchive):
    pass


class TarArchivedFile(BaseArchivedFile):
    pass


class ZipArchive(BaseArchive):
    def __init__(self, filename):
        self._archive = zipfile.ZipFile(filename, mode='r')

    def __iter__(self):
        for item in self._archive.infolist():
            yield self._wrap_zipinfo(item)

    def get(self, name):
        zipinfo = self._archive.getinfo(name)
        return self._wrap_zipinfo(zipinfo)

    def _wrap_zipinfo(self, item):
        return ZipArchivedFile(self, name=item.filename, size=item.file_size)


class ZipArchivedFile(BaseArchivedFile):
    def open(self):
        return self.archive._archive.open(self.name)
