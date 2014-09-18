"""
Resource access abstraction.

Allows retrieving a resource in a flexible and extendable way.

The accessors distributed with the core provide support for the following urls:

+---------------------+--------------------------------------+
| Scheme              | Accessor class                       |
+=====================+======================================+
| ``internal`` [0]_   | :py:class:`InternalResourceAccessor` |
+---------------------+--------------------------------------+
| ``http``, ``https`` | :py:class:`HttpResourceAccessor`     |
+---------------------+--------------------------------------+

.. [0] Resources from the internal storage are linked using URLs like:
       ``internal:///123`` (where ``123`` is the resource id).


.. todo:: Use some configuration option to allow changing the
          resource accessors.
"""

from urlparse import urlparse
import abc
import cgi
import datetime

import requests

from datacat.db import db
from datacat.utils.const import HTTP_DATE_FORMAT
from datacat.utils.files import file_copy


def open_resource(url):
    """
    Open a resource from a URL, returning the appropriate accessor
    class instance.
    """

    accessors = get_resource_accessors()
    scheme = urlparse(url).scheme
    try:
        accessor = accessors[scheme]
    except KeyError:
        raise ResourceAccessFailure(
            "No accessor found for URL scheme: {0}"
            .format(scheme))
    else:
        return accessor(url)


def get_resource_accessors():
    """
    Get a dictionary mapping URL scheme names to accessor
    class for those urls.
    """
    return {
        'http': HttpResourceAccessor,
        'https': HttpResourceAccessor,
        'internal': InternalResourceAccessor,
    }


class ResourceAccessError(Exception):
    pass


class ResourceNotFound(ResourceAccessError):
    """
    Exception to indicate the resource was not found.

    Used eg. for HTTP error 404 or internal resource not found.
    """
    pass


class ResourceAccessDenied(ResourceAccessError):
    """
    Exception to indicate access to the resource was denied.

    Used eg. for HTTP errors 401 and 403
    """
    pass


class ResourceAccessFailure(ResourceAccessError):
    """
    Exception to indicate a generif failure to access the resource.

    To be used, eg. for connection errors or http error 500.
    """
    pass


class BaseResourceAccessor(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, url):
        """
        (Lazily) open the resource. This could merely mean storing
        the url somewhere for later, as in default implementation.
        """
        self.url = url

    def __repr__(self):
        return "{0}.{1}({2!r})".format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.url)

    @abc.abstractmethod
    def open_resource(self):
        """
        Return a file descriptor associated with the selected resource.
        """
        pass

    def save_to_file(self, dest, blocksize=4096):
        """Save the resource to file"""

        src = self.open_resource()
        file_copy(src, dest, blocksize=blocksize)

    @property
    def last_modified(self):
        """Get the last modified date for this object"""
        raise NotImplementedError('')

    @property
    def etag(self):
        """Get a value that can be used as etag for this resource"""
        raise NotImplementedError('')

    @property
    def content_type(self):
        """Return the resource mimetype"""
        raise NotImplementedError('')


class InternalResourceAccessor(BaseResourceAccessor):
    def open_resource(self):
        resource_id = self._get_resource_id()

        with db, db.cursor() as cur:
            cur.execute("""
            SELECT id, mimetype, data_oid FROM "resource" WHERE id = %(id)s;
            """, dict(id=resource_id))
            resource = cur.fetchone()

        if resource is None:
            raise ResourceNotFound(
                "The resource was not found in the database")

        return db.lobject(oid=resource['data_oid'], mode='rb')

    @property
    def last_modified(self):
        # todo: return resource "mdate" field value
        pass

    @property
    def etag(self):
        """
        Not implemented yet: might return a hash of the resource data?
        """
        raise NotImplementedError(
            "Getting etag for internal resource is not suppored yet")

    def _get_resource_id(self):
        parsed_url = urlparse(self.url)
        if parsed_url.scheme != 'internal':
            raise ValueError("Unsupported URL scheme: {0}"
                             .format(parsed_url.scheme))
        if parsed_url.netloc != '':
            raise ValueError(
                "Unsupported internal:// URL with a network location. "
                "Make sure you specified the currect number of /, i.e. "
                "internal:///123 *not* internal://123.")
        try:
            return int(parsed_url.path.strip('/'))
        except:
            raise ValueError("Invalid resource id: {0}"
                             .format(parsed_url.path.strip('/')))


class HttpResourceAccessor(BaseResourceAccessor):
    """
    Allow accessing an HTTP resource
    """

    def open_resource(self):
        if getattr(self, '_cached_resp', None) is None:
            self._do_request()
        return self._cached_resp.raw

    def _do_request(self):
        self._cached_resp = requests.get(self.url, stream=True)
        self._cached_headers = self._cached_resp.headers

    @property
    def _headers(self):
        if getattr(self, '_cached_headers', None) is None:
            self._do_request()
        return self._cached_headers

    @property
    def last_modified(self):
        val = self._headers['last-modified']
        if val is None:
            return None
        return datetime.datetime.strptime(val, HTTP_DATE_FORMAT)

    @property
    def etag(self):
        return self._headers.get('etag')

    @property
    def content_type(self):
        return cgi.parse_header(self._headers['content-type'])[0]
