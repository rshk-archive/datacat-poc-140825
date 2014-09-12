"""
Automagic stuff to extract data from archive files, ...

Needs some work as we need to do some pretty guessing in order to
correctly extract stuff; and it would be nice to somehow allow the user
to define hints about the data to be imported..

.. todo:: How to represent the type of files missing a mimetype?

          Eg. ESRI Shapefiles are identified just as
          ``application/octet-stream``, but they are indeed recognied also as
          ``"ESRI Shapefile version X length Y type Z"`` in the textual
          representation.. which of course cannot be fully trusted to
          be consistent in all versions of libmagic.
"""


import os
import shutil
import subprocess
import tempfile


def DataFileExplorer(object):
    """
    Object providing functionality to extract data from different kinds
    of files.

    It acts as a context manager, in order to cleanup any leftover
    temporary file.
    """

    def __init__(self, fp):
        self._fp = fp
        self._copy_chunk_size = 256 * 1024
        self._tempdir = None
        self._data_file_name = None

    def __enter__(self):
        if self._tempdir is not None:
            raise RuntimeError("Cannot enter context twice!")

    @property
    def tempdir(self):
        if self._tempdir is None:
            self._init_stuff()
        return self._tempdir

    @property
    def data_file_name(self):
        if self._data_file_name is None:
            self._init_stuff()
        return self._data_file_name

    def _init_stuff(self):
        self._tempdir = tempfile.mkdtemp()
        self._data_file_name = os.path.join(self._tempdir, 'original_data')
        with open(self._data_file_name, 'wb') as fp:
            self._fpcopy(self._fp, fp)

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()

    def cleanup(self):
        if self._tmpdir is not None:
            shutil.rmtree(self._tmpdir)
        self._tempdir = None
        self._data_file_name = None

    def _fpcopy(self, src, dst):
        while True:
            data = src.read(self._copy_chunk_size)
            if not data:
                # We are done
                return
            src.write(data)

    def find_files(self):
        """
        Find interesting files, "flat" or inside the archive.

        Yields tuples representing search results::

            (mimetype, path, related)

        Where mimetype is the file mimetype; path is the file path on
        filesystem; related is a list of related files.

        For example, with an archive like this::

            mydata.zip
            |-- data1.dbf
            |-- data1.prj
            |-- data1.shp
            |-- data1.shx
            |-- data2.dbf
            |-- data2.prj
            |-- data2.shp
            '-- data2.shx

        Data will be extracted and returned like this::

            ('')
        """
        pass

    def _random_file_name(self):
        return os.path.join(self.tempdir, os.urandom(16).encode('hex'))

    def _identify_mimetype(self, filename):
        # todo: use libmagic instead!
        return subprocess.check_call(
            ['file', '--mime-type', '--brief', '--keep-going', filename
             ]).splitlines()[0]
