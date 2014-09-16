"""
Abstraction layer to access different kinds of file archives
using a common interface.

.. note::

    Currently the functionality is limited to the one required
    for the data extraction pipelines, i.e. file listing and
    retrieving.

    In the future, this module might be split into its own package
    and more functionality added (eg. write support, ...).
"""

import abc
import zipfile
import tarfile

from datacat.utils.tempfile import TemporaryDir

# Default extensions for archive files
DEFAULT_ARCHIVE_EXT = [
    'zip', '7z', 'tar', 'tar.gz', 'tar.bz2', 'tar.xz', 'tar.lzma', 'rar',
]


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
    """
    Base interface for the archive abstraction.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, filename):
        """
        Initialize things. This method should also already open the archive, in
        order to check whether it is a supported format or not. If not,
        it should raise an :py:exc:`ArchiveOpenFailure` exception, to tell
        :py:func:`open_archive` to try with the next opener.
        """
        pass

    @abc.abstractmethod
    def __iter__(self):
        """
        Iterate over archive members, yielding :py:class:`BaseArchivedFile`
        instances for each one.
        """
        pass

    @abc.abstractmethod
    def get(self, name):
        """
        Get a single archive member, by name, wrapped in a
        :py:class:`BaseArchivedFile` instance
        """
        pass

    # @abc.abstractmethod
    # def extract(self, path):
    #     """
    #     Extract all the archive contents to a given path.
    #     """
    #     pass


class BaseArchivedFile(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, archive, name, **attrs):
        """
        :param archive:
            The :py:obj:`BaseArchive` interface this member was extracted from.

        :param name:
            The member name inside the archive.

        :param **attrs:
            Keyword arguments will be exposed as attributes
        """
        self.archive = archive
        self.name = name
        self._attrs = {
            'size': None,
        }
        self._attrs.update(attrs)

    @abc.abstractmethod
    def open(self):
        """
        Return a file object associated with this file.
        The file will be opened in read-only mode.
        """
        pass

    def __getattr__(self, name):
        """
        Used to access attributes set via keyword arguments
        to constructor.
        """
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
        try:
            self._archive = zipfile.ZipFile(filename, mode='r')
        except zipfile.BadZipfile as e:
            raise ArchiveOpenFailure("Bad archive: {0!r}".format(e))

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


# ------------------------------------------------------------
# Other utility functions
# ------------------------------------------------------------


class ExtractedArchiveFiles(object):
    """
    Context manager class giving temporary access to a directory
    containing data from a (recursively) extracted archive.
    """

    def __init__(self, archive_file, archive_ext=DEFAULT_ARCHIVE_EXT):
        self.archive = open_archive(archive_file)

    def __enter__(self):
        self._tempdir = TemporaryDir()
        path = self._tempdir.__enter__()
        self.archive.extract(path)

    def __exit__(self, exc_type, exc_value, traceback):
        self._tempdir.__exit__(exc_type, exc_value, traceback)
