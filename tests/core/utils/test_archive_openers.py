import itertools

from datacat.utils.archives import open_archive, ZipArchive


def test_archive_zip(data_dir):
    # .zip
    archive = open_archive(str(data_dir.join('geodata/roads-folders.zip')))
    assert isinstance(archive, ZipArchive)

    assert sorted(list(x.name for x in archive)) == sorted(itertools.chain(*([
        'roads-{0:02d}/'.format(i),
        'roads-{0:02d}/roads-{0:02d}.shp'.format(i),
        'roads-{0:02d}/roads-{0:02d}.shx'.format(i),
        'roads-{0:02d}/roads-{0:02d}.dbf'.format(i),
        'roads-{0:02d}/roads-{0:02d}.prj'.format(i),
    ] for i in xrange(4))))

    assert archive.get('roads-00/roads-00.shp').open().read(4) \
        == '\x00\x00\x27\x0a'


def test_archive_tar_builtin(data_dir):
    # .tar .tar.gz .tar.bz2
    pass


def test_archive_tar_xz(data_dir):
    # .tar.xz .tar.lzma
    pass


def test_archive_7zip(data_dir):
    # .7z
    pass
