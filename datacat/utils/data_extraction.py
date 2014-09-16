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


from collections import defaultdict
import os
import subprocess

from datacat.utils.archives import open_archive

SHP_EXT = set(['shp'])
SHP_REL_EXT = set(['shx', 'dbf', 'prj'])
ARCHIVE_EXT = set(['zip', 'tar', 'tar.gz', 'tar.bz2',
                   'tar.xz', 'tar.lzma', 'rar', '7z'])


def find_shapefiles(archive_filename):
    # ------------------------------------------------------------
    # Note: to find stuff recursively in an archive, we need
    #       to extract the sub-archives first. For that, we need
    #       a temporary directory and to make sure we delete it
    #       once we're done..
    # ------------------------------------------------------------

    found = defaultdict(dict)  # {basename: {ext: ArchivedFile()}}

    archive = open_archive(archive_filename)
    for member in archive:
        basename, ext = os.path.splitext(member.name)
        ext = ext[1:]  # Strip leading dot
        ext_low = ext.lower()

        if ext_low in SHP_EXT or ext_low in SHP_REL_EXT:
            found[basename][ext] = member

    return dict(found)


def shp2pgsql(shapefile, schema=None, table=None,
              drop=False, mode='create', create_table_only=False,
              use_dump_format=False, use_wkt=False, no_transaction=False,
              from_srid=None, srid=None, use_geography=False,
              geometry_column=None, keep_case=False, force_32bit=False,
              simple_geometries=False, encoding=None, create_gist_index=False,
              null_policy='insert', tablespace=None, index_tablespace=None):
    """
    Wrapper around shp2pgsql command.

    :param shapefile:
        Path to a shapefile to be converted

    :param schema:
        (optional) schema in which table should be created

    :param table:
        (optional, recommended) name of the table in which to import data

    :param drop:
        Drops the database table before creating a new table with the
        data in the Shape file.

    :param mode:

        A string describing the desired operation mode

        'append'
            Appends data from the Shape file into the database table.
            Note that to use this option to load multiple
            files, the files must have the same attributes and same data types.

        'create'
            Creates a new table and populates it from the Shape file.
            This is the default mode.

    :param create_table_only:
        Only  produces  the  table  creation SQL code, without adding
        any actual data.  This can be used if you need to completely
        separate the table creation and data loading steps.

    :param use_dump_format:
        Use the PostgreSQL "dump" format for the output data. This can
        be combined with -a, -c and  -d.  It  is much faster to load
        than the default "insert" SQL format. Use this for very large
        data sets.

    :param use_wkt:
        Output WKT format, instead of WKB.  Note that this can introduce
        coordinate drifts due to loss of precision.

    :param no_transaction:
        Execute each statement on its own, without using a
        transaction.  This allows loading of the majority of good
        data when there are some bad geometries that generate errors.
        Note that this cannot be used with the -D flag as the "dump"
        format always uses a transaction.

    :param from_srid:
        Specify the SRID of the original projection.

    :param srid:
        Specify the SRID to which data should be converted

    :param use_geography:
        Use  the  geography  type instead of geometry.  Geography is
        used to store lat/lon data.  At the moment the only spatial
        reference supported is 4326.

    :param geometry_column:
        Specify the name of the geometry column (mostly useful in append mode).

    :param keep_case:
        Keep idendifiers case (column, schema and attributes). Note
        that attributes in Shapefile are usually allUPPERCASE.

    :param force_32bit:
        Coerce all integers to standard 32-bit integers, do not create
        64-bit bigints, even if the DBF header signature appears to
        warrant it.

    :param simple_geometries:
        Generate simple Geometries instead of MULTIgeometries. Shape
        files don't differ between LINESTRINGs and MULTILINESTRINGs,
        so  shp2pgsql  generates  MULTILINESTRINGs  by  default.  This
        switch  will produce LINESTRINGs instead, but shp2pgsql will
        fail when it hits a real MULTILINESTRING. The  same  works
        for POLYGONs vs. MULTIPOLYGONs.

    :param encoding:
        Specify the character encoding of Shapefile's attributes.  If
        this option is used the output will be encoded in UTF-8.

    :param create_gist_index:
        Create a GiST index on the geometry column.

    :param null_policy:
        Specify NULL geometries handling policy (insert,skip,abort).

    :param tablespace:
        Specify the tablespace for the new table.  Indexes will still
        use the default tablespace unless the -X parameter is also
        used.  The PostgreSQL documentation has a good description on
        when to use custom tablespaces.

    :param index_tablespace:
        Specify the tablespace for the new table's indexes.  This
        applies to the primary key index, and the GIST spatial index
        if -I is also used.

    .. todo:: We should find some smarter way to return "chunked" output
              as soon as it is available, instead of keeping all of it
              in memory. But then we need some way to pass it to
              PostgreSQL..

    .. todo:: It would also be nice to be able to export the whole table
              as a CSV file, (Like using the dump format -D) and then passing
              it to postgres using ``cursor.copy_from()`` -> if we use
              the dump format, we need to strip content up to the "COPY ..."
              line.
    """

    args = ['shp2pgsql']
    if drop:
        args.append('-d')

    if mode == 'create':
        args.append('-c')
    elif mode == 'append':
        args.append('-a')

    if create_table_only:
        args.append('-p')

    if use_dump_format:
        args.append('-D')

    if use_wkt:
        args.append('-w')

    if no_transaction:
        args.append('-e')

    if srid is not None:
        val = str(srid)
        if from_srid is not None:
            val = str(from_srid) + ':' + val
        args.extend(['-s', val])

    if use_geography:
        args.append('-G')

    if geometry_column is not None:
        args.extend(['-g', str(geometry_column)])

    if keep_case:
        args.append('-k')

    if force_32bit:
        args.append('-i')

    if simple_geometries:
        args.append('-S')

    if encoding is not None:
        args.extend(['-W', str(encoding)])

    if create_gist_index:
        args.append('-I')

    if null_policy in ('insert', 'skip', 'abort'):
        args.extend(['-N', null_policy])

    if tablespace is not None:
        args.extend(['-T', str(tablespace)])

    if index_tablespace is not None:
        args.extend(['-T', str(index_tablespace)])

    args.append(shapefile)

    if table is not None:
        if schema is not None:
            table = '.'.join((str(schema), str(table)))
        args.append(table)

    # Make sure all arguments are converted to string
    args = [str(x) for x in args]

    return subprocess.check_output(args)
