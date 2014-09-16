from datacat.utils.data_extraction import find_shapefiles


def test_find_shapefiles(data_dir):
    found = find_shapefiles(str(data_dir.join('geodata/roads-folders.zip')))
    assert sorted(found.keys()) == [
        'roads-{0:02d}/roads-{0:02d}'.format(i) for i in xrange(4)]

    for name, item in found.iteritems():
        assert sorted(item.keys()) == ['dbf', 'prj', 'shp', 'shx']

        assert item['shp'].open().read(4) == b'\x00\x00\x27\x0a'
        assert item['shx'].open().read(4) == b'\x00\x00\x27\x0a'
        assert item['dbf'].open().read(4) == b'\x03\x5f\x07\x1a'
        assert item['prj'].open().read(4) == b'PROJ'
