"""
Datacat Geographical Plugin

- Imports resources (from an URL or internal resource) into a PostGIS table
- Exports geographical data into various formats
"""

import os
import re

from werkzeug.exceptions import NotFound

from datacat.db import db, admin_db
from datacat.ext.base import Plugin
from datacat.utils.data_extraction import find_shapefiles, shp2pgsql
from datacat.utils.resource_access import open_resource
from datacat.utils.tempfile import TemporaryDir


class GeoPlugin(Plugin):
    def install(self):
        """
        Create required tables.

        .. todo:: write this function
        """
        # Create database schema
        # NOTE: CANNOT CREATE EXTENSION FROM NON-SUPERUSER!
        # with admin_db, admin_db.cursor() as cur:
        #     cur.execute("create extension postgis")

        # todo: we need a table to keep track of the imported datasets.
        pass

    def uninstall(self):
        """
        Remove all the previously created tables.

        .. todo:: write this function
        """
        pass


geo_plugin = GeoPlugin(__name__)


@geo_plugin.hook('make_dataset_metadata')
def make_dataset_metadata(dataset_id, config, metadata):
    """
    :hook: ``make_dataset_metadata``
    """
    if not config.get('geo', {}).get('enabled', False):
        # Not a geographical dataset
        return

    # todo: Add URLs to resources for the converted formats

    pass


@geo_plugin.hook(['dataset_create', 'dataset_update'])
def on_dataset_create_update(dataset_id, dataset_conf):
    """
    On dataset create/update, import geographical resources.

    :hook: ``dataset_create``
    :hook: ``dataset_update``

    This means:

    - download a copy of the remote resource
    - use some importer to extract geographical information from the resource
    - import the data in a postgis table named after the dataset

    .. todo:: We need a common library to download resources honoring caches
    """

    if dataset_conf.get('geo', {}).get('enabled', False):
        import_geo_dataset.delay(dataset_id)


@geo_plugin.hook(['dataset_delete'])
def on_dataset_delete(dataset_id):
    """
    On dataset delete, also delete geographical resources.

    :hook: ``dataset_delete``

    - Delete postgis tables containing the geo data

    .. todo:: related things, like cached copies, should be deleted
              by some "core" plugin -> use some kind of reference
              mechanism to "cascade" deletes.
    """
    # todo: write this


@geo_plugin.task(name=__name__ + '.import_geo_dataset')
def import_geo_dataset(dataset_id):
    """
    Task to import geographical resources from a dataset
    into a PostGIS table.

    :param dataset_id: Id of the dataset to import
    """

    with db.cursor() as cur:
        cur.execute("SELECT id, configuration FROM dataset"
                    " WHERE id=%s;", (dataset_id,))
        result = cur.fetchone()

    if result is None:
        # Should be logged as an error
        raise NotFound("Dataset not found: {0}".format(dataset_id))

    conf = result['configuration']

    if not conf.get('geo', {}).get('enabled', False):
        # Task was called from hook.. by error?
        raise ValueError("Requested import for non-geo-enabled dataset")

    if conf['geo']['importer'] == 'find_shapefiles':
        return import_dataset_find_shapefiles(dataset_id, conf)

    else:
        raise ValueError("Unsupported importer: {0}"
                         .format(conf['geo']['importer']))


@geo_plugin.route('/data/<int:dataset_id>/export/shp')
def export_geo_dataset_shp(dataset_id):
    """
    Export dataset to `Esri Shapefile
    <http://en.wikipedia.org/wiki/Shapefile>`_ format.

    :HTTP URL: ``/data/<int:dataset_id>/export/shp``

    .. warning:: Not implemented yet
    """
    pass


@geo_plugin.route('/data/<int:dataset_id>/export/geojson')
def export_geo_dataset_geojson(dataset_id):
    """
    Export dataset to `GeoJSON <http://geojson.org/>`_.

    :HTTP URL: ``/data/<int:dataset_id>/export/geojson``

    .. warning:: Not implemented yet
    """
    pass


@geo_plugin.route('/data/<int:dataset_id>/export/csv')
def export_geo_dataset_csv(dataset_id):
    """
    Export dataset to CSV, in a format suitable for use with
    `PostgreSQL COPY
    <http://www.postgresql.org/docs/9.3/static/sql-copy.html>`_
    operations.

    :HTTP URL: ``/data/<int:dataset_id>/export/csv``

    .. warning:: Not implemented yet
    """
    pass


@geo_plugin.route('/data/<int:dataset_id>/export/kml')
def export_geo_dataset_kml(dataset_id):
    """
    Export dataset to `Keyhole Markup Language
    <https://developers.google.com/kml/>`_, mostly for displaying
    on Google Earth.

    :HTTP URL: ``/data/<int:dataset_id>/export/kml``

    .. warning:: Not implemented yet
    """
    pass


@geo_plugin.route('/data/<int:dataset_id>/export/gml')
def export_geo_dataset_gml(dataset_id):
    """
    Export dataset to `Geography Markup Language
    <http://www.opengeospatial.org/standards/gml>`_.

    :HTTP URL: ``/data/<int:dataset_id>/export/gml``

    .. warning:: Not implemented yet
    """
    pass


@geo_plugin.route('/data/<int:dataset_id>/render/'
                  'tiles/<int:z>/<int:x>/<int:y>.png')
def render_geo_dataset_tiles(dataset_id, z, x, y):
    """
    Render tiles from a dataset.

    .. note:: we need some better way to configure the dataset
    """

    import math
    import mapnik
    from flask import current_app

    table_name = _get_dataset_geo_table_name(dataset_id)

    POSTGIS_TABLE = dict(
        host=current_app.config['DATABASE']['host'],
        port=current_app.config['DATABASE']['port'],
        user=current_app.config['DATABASE']['user'],
        password=current_app.config['DATABASE']['password'],
        dbname=current_app.config['DATABASE']['database'],
        table=table_name + "_900913")
    LAYER_NAME = 'geo_layer'

    # Google Mercator / EPSG:900913
    GOOGLEMERC = ('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 '
                  '+x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs')
    DATA_PROJECTION = mapnik.Projection(GOOGLEMERC)

    TILE_WIDTH = 256  # Square tiles only!


    minmax = lambda val, lower, upper: min(max(val, lower), upper)

    tile_coords = namedtuple('TileCoords', 'x,y')
    geo_coords = namedtuple('Coords', 'lat,lon')


    def deg2num(lat_deg, lon_deg, zoom):
        """Convert coordinates to tile number"""

        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((
            1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad)))
            / math.pi) / 2.0 * n)
        return tile_coords(x=xtile, y=ytile)


    def num2deg(xtile, ytile, zoom):
        """Convert tile number to coordinates (of the upper corner)"""

        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return mapnik.Coord(y=lat_deg, x=lon_deg)

    class TiledMapRenderer(object):
        def __init__(self, mapobj):
            self.m = mapobj

        def render_tile(self, z, x, y):
            """
            :param z: Zoom level
            :param x: Tile horizontal position
            :param y: Tile vertical position
            """

            topleft = num2deg(x, y, z)
            bottomright = num2deg(x + 1, y + 1, z)

            # Bounding box for the tile
            bbox = mapnik.Box2d(topleft, bottomright)

            bbox = DATA_PROJECTION.forward(bbox)

            print("Bouding box: ", bbox)

            # self.m.resize(TILE_WIDTH, TILE_WIDTH)
            self.m.zoom_to_box(bbox)

            MIN_BUFFER = 256
            self.m.buffer_size = max(self.m.buffer_size, MIN_BUFFER)

            # Render image with default Agg renderer
            im = mapnik.Image(TILE_WIDTH, TILE_WIDTH)
            mapnik.render(self.m, im)
            return im

    m = mapnik.Map(TILE_WIDTH, TILE_WIDTH)
    # m.background = mapnik.Color('steelblue')

    s = mapnik.Style()
    r = mapnik.Rule()

    # polygon_symbolizer = mapnik.PolygonSymbolizer(mapnik.Color('#00ffff'))
    # r.symbols.append(polygon_symbolizer)

    line_symbolizer = mapnik.LineSymbolizer(
        mapnik.Color('#ff00ff'), 14)
    line_symbolizer.stroke.opacity = 0.5
    r.symbols.append(line_symbolizer)

    text_symbolizer = mapnik.TextSymbolizer(
        mapnik.Expression('[desvia]'),
        'DejaVu Sans Book', 10, mapnik.Color('black'))
    text_symbolizer.halo_fill = mapnik.Color('white')
    text_symbolizer.halo_radius = 2
    text_symbolizer.label_placement = mapnik.label_placement.LINE_PLACEMENT
    r.symbols.append(text_symbolizer)

    s.rules.append(r)
    m.append_style('My Style', s)

    # Initialize layer from PostGIS table
    ds = mapnik.PostGIS(**POSTGIS_TABLE)
    layer = mapnik.Layer(LAYER_NAME)
    layer.datasource = ds
    layer.styles.append('My Style')
    m.layers.append(layer)

    m.zoom_all()

    renderer = TiledMapRenderer(m)
    im = renderer.render_tile(z, x, y)

    # im = mapnik.Image(TILE_WIDTH, TILE_WIDTH)
    # mapnik.render(m, im, 13, 0, 0)
    # # im.save('/tmp/bla.png')

    return im.tostring('png'), 200, {'Content-type': 'image/png'}

    pass


# ----------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------

def _random_file_name(ext=None):
    name = os.urandom(20).encode('hex')
    if ext is not None:
        name += '.' + ext
    return name


def _copy_resource_to_file(resource, filename):
    res_object = open_resource(resource['url'])
    with open(filename, 'wb') as fp:
        res_object.save_to_file(fp)


def import_dataset_find_shapefiles(dataset_id, dataset_conf):
    """
    Find all the Shapefiles from archives listed as dataset resources.

    :param dataset_id: The dataset id
    :param dataset_conf: The dataset configuration
    """

    destination_table = _get_dataset_geo_table_name(dataset_id)

    create_table_sqls = []
    import_data_sqls = []

    with TemporaryDir() as tempdir:
        # First, copy zip files to temporary directory

        for resource in dataset_conf['resources']:
            # We assume the file is a zip, but we should double-check that!
            dest_file = os.path.join(tempdir, _random_file_name('zip'))

            if isinstance(resource, basestring):
                resource = {'url': resource}

            # Copy the resource to disk
            _copy_resource_to_file(resource, dest_file)

            # Let's look for shapefiles inside that thing..
            found = find_shapefiles(dest_file)
            for basename, files in found.iteritems():
                if 'shp' not in files:
                    continue  # Bad match..

                # Export shapefiles to temporary files
                base_name = _random_file_name()
                for ext, item in files.iteritems():
                    dest = os.path.join(tempdir, base_name + '.' + ext)

                    with open(dest, 'wb') as fp:
                        # todo: copy file in chunks, not as a whole
                        fp.write(item.open().read())

                shp_full_path = os.path.join(tempdir, base_name + '.shp')

                create_table_sql = shp2pgsql(
                    shp_full_path,
                    table=destination_table,
                    create_table_only=True, mode='create',
                    geometry_column='geom', create_gist_index=True)

                # Use TEXT fields instead of varchar(XX)
                # todo: use a less-hackish way!!
                create_table_sql = re.sub(
                    r'varchar\([0-9]+\)', 'text', create_table_sql,
                    flags=re.IGNORECASE)

                import_data_sql = shp2pgsql(
                    shp_full_path,
                    table=destination_table,
                    mode='append',
                    geometry_column='geom',
                    create_gist_index=False)

                create_table_sqls.append(create_table_sql)
                import_data_sqls.append(import_data_sql)

    with admin_db, admin_db.cursor() as cur:
        cur.execute(create_table_sqls[0])

    with db, db.cursor() as cur:
        for sql in import_data_sqls:
            cur.execute(sql)

    # ------------------------------------------------------------
    # Now generate a view to read data in google mercator
    # projection (needed in order to render maps as OSM overlays)
    # ------------------------------------------------------------

    with db, db.cursor() as cur:
        cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position ASC;
        """, (destination_table,))

        col_names = []
        for row in cur.fetchall():
            if row['column_name'] != 'geom':
                col_names.append(row['column_name'])

    mercator_view_sql = """
    CREATE OR REPLACE VIEW "{0}_900913" AS
    SELECT {1}, st_transform(geom, 900913) as geom
    FROM "{0}";
    """.format(destination_table,
               ', '.join('"{0}"'.format(x) for x in col_names))

    with db, db.cursor() as cur:
        cur.execute(mercator_view_sql)

    wgs84_view_sql = """
    CREATE OR REPLACE VIEW "{0}_wgs84" AS
    SELECT {1}, st_transform(geom, 4326) as geom
    FROM "{0}";
    """.format(destination_table,
               ', '.join('"{0}"'.format(x) for x in col_names))

    with db, db.cursor() as cur:
        cur.execute(wgs84_view_sql)


def _get_dataset_geo_table_name(dataset_id):
    return 'geodata_{0}'.format(dataset_id)
