import json
import re
import time
import urlparse

from datacat.db import db


def test_geo_import_shapefile(configured_app, data_dir):
    # ============================================================
    # - Create a resource containing a Zip file containing
    #   some shapefiles
    # - Create a dataset configured to import data from the
    #   resource as a geographical dataset
    # - Check that everything worked as expected (give it a
    #   little time to do stuff)
    # ============================================================

    apptc = configured_app.test_client()
    with open(str(data_dir.join('geodata/roads-folders.zip')), 'rb') as fp:
        payload = fp.read()
    resp = apptc.post('/api/1/admin/resource/',
                      headers={'Content-type': 'application/zip'},
                      data=payload)

    # Obtain the resource id
    resource_url = resp.headers['Location']
    path = urlparse.urlparse(resource_url).path
    match = re.match('/api/1/admin/resource/([0-9]+)', path)
    resource_id = int(match.group(1))

    # Create geo dataset with this resource
    dataset_conf = {
        'metadata': {
            'title': 'Some Trentino roads from OpenStreetMap',
        },
        'resources': [
            {'type': 'internal', 'id': resource_id},
        ],
        'geo': {
            'enabled': True,
            'importer': 'find_shapefiles',
        }
    }

    resp = apptc.post('/api/1/admin/dataset/',
                      headers={'Content-type': 'application/json'},
                      data=json.dumps(dataset_conf))

    # Obtain the dataset id
    path = urlparse.urlparse(resp.headers['Location']).path
    match = re.match('/api/1/admin/dataset/([0-9]+)', path)
    dataset_id = int(match.group(1))

    time.sleep(3)

    # ------------------------------------------------------------
    # Now, we're ready to check!
    # ------------------------------------------------------------

    # First, check that the table exists and it is populated

    with configured_app.app_context():
        with db, db.cursor() as cur:
            cur.execute("""SELECT * FROM "geodata_{0}";""".format(dataset_id))
            assert len(list(cur)) == 40  # 10 items, 4 shapefiles
