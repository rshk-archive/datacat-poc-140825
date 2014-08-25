Data Catalog - PoC 2014-08-25
#############################

**Project goal:** create a service, talking via RESTful API, to
 provide facilities for storing data, adding metadata, and generating
 "derivates" from the stored data.


Technology
==========

- Python (Flask, Psycopg2)
- PostgreSQL 9.2+ (with Json column type)
- PostGIS (for the geo data plugin)
- Mapnik (for rendering geo data)


Example use cases
=================

**Tabular data:**

- store original data as (one of) CSV/ODS/XLS/...
- expose data as derivate formats:

  - normalize CSV dialect (comma as separator, double quotes, ..)
  - normalize charset (utf-8)
  - ODS/XLS/...
  - JSON (apply column types, ..)
  - Other custom formats (even on a per-dataset basis, eg. a CSV
    containing coordinates can be converted to a Shapefile)


**Geographical data:**

- store original data as (one of) Esri Shapefile, GML, KML, GeoJSON..
- import the data in a PostGIS table, to allow further queries /
  transformations.
- expose data as other formats: SHP, GML, KML, GeoJSON, ..
- use mapnik to render tile layers, according to a configuration
- clean up the data before republishing:

  - use utf-8 as encoding for the text
  - use a standard projection for the data (WGS48) (?)
  - make sure output shapefiles have projection specification (PRJ
    file, in WKT format) [hint: use `gdalsrsinfo
    <http://www.gdal.org/gdalsrsinfo.html>`_ to convert proj description]


**Textual data:**

For example, PDFs, ODT, MS DOC, ...

- Extract plain text
- Index the plain text, offer full-text search functionality
- Convert to HTML to view in the browser


**Custom, per-dataset, transforms:**

For example, we can create new datasets by aggregating other resources, ...


Data model
==========

- **Resources** describe a piece of information, usually by pointing
  at some URL from which the resource can be downloaded.

- **Datasets** describe how to take some resources and generate some
  others from them and expose them through the API.
