from __future__ import absolute_import

import os
import shutil
import tempfile


class TemporaryDir(object):
    def __init__(self, suffix='', prefix='tmp', dir=None):
        self._tempdir = tempfile.mkdtemp(suffix, prefix, dir)

    def __enter__(self):
        if self._tempdir is None:
            raise RuntimeError("Cannot reuse temporary directory")
        return self._tempdir

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self._tempdir)
        self._tempdir = None


class TemporaryFile(object):
    def __init__(self, suffix='', prefix='tmp', dir=None, text=False):
        fd, fname = tempfile.mkstemp(suffix, prefix, dir, text)
        self._tempfd = fd
        self._tempfilename = fname

    def __enter__(self):
        if self._tempfd is None:
            raise RuntimeError("Cannot reuse temporary file")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            try:
                os.close(self._tempfd)
            except OSError:
                # Just ignore the "bad FD", which is happening due
                # to the file descriptor being already closed by something
                pass

            os.unlink(self._tempfilename)

        finally:
            self._tempfd = None
            self._tempfilename = None

    def open(self, mode='w+b'):
        return os.fdopen(self._tempfd, mode)

    @property
    def filename(self):
        return self._tempfilename
