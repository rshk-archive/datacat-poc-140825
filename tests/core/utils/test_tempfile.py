import os

import pytest

from datacat.utils.tempfile import TemporaryDir, TemporaryFile


def test_temporary_dir():
    with TemporaryDir() as tempdir:
        with open(os.path.join(tempdir, 'foobar.txt'), 'wt') as fp:
            fp.write('Hello, world!\n')

        with open(os.path.join(tempdir, 'foobar.txt'), 'rt') as fp:
            assert fp.read() == 'Hello, world!\n'

    assert not os.path.exists(os.path.join(tempdir, 'foobar.txt'))
    assert not os.path.exists(tempdir)


def test_temporary_file():
    with TemporaryFile() as tempfile:
        filename = tempfile.filename

        tempfile.open('w+').write('Hello, world!\n')

        with open(filename, 'r') as fp:
            assert fp.read() == 'Hello, world!\n'

    assert not os.path.exists(filename)


def test_disallow_reuse():
    tempdir = TemporaryDir()

    with tempdir:
        pass

    with pytest.raises(RuntimeError):
        with tempdir:
            pass

    tempfile = TemporaryFile()

    with tempfile:
        pass

    with pytest.raises(RuntimeError):
        with tempfile:
            pass
