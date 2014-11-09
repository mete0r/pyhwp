# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2014 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
'''HWPv5 to ODT converter

Usage::

    hwp5odt [options] [--embed-image] <hwp5file>
    hwp5odt [options] --styles <hwp5file>
    hwp5odt [options] --content [--embed-image] <hwp5file>
    hwp5odt [options] --document [--no-embed-image] <hwp5file>
    hwp5odt -h | --help
    hwp5odt --version

Options::

    -h --help           Show this screen
    --version           Show version
    --loglevel=<level>  Set log level.
    --logfile=<file>    Set log file.

    --document          Produce single OpenDocument XML file (.fodt)
    --styles            Produce *.styles.xml
    --content           Produce *.content.xml

    --output=<file>     Output file.
'''
from __future__ import with_statement
import os
import os.path
import logging
import sys
import tempfile
from contextlib import contextmanager

from docopt import docopt

from hwp5 import plat
from hwp5 import __version__ as version
from hwp5.proc import rest_to_docopt
from hwp5.proc import init_logger
from hwp5.errors import InvalidHwp5FileError
from hwp5.importhelper import pkg_resources_filename
from .utils import cached_property
from .xmlmodel import Hwp5File


logger = logging.getLogger(__name__)


RESOURCE_PATH_RNG = 'odf-relaxng/OpenDocument-v1.2-os-schema.rng'
RESOURCE_PATH_XSL_SINGLE_DOCUMENT = 'xsl/odt/document.xsl'
RESOURCE_PATH_XSL_STYLE = 'xsl/odt/styles.xsl'
RESOURCE_PATH_XSL_CONTENT = 'xsl/odt/content.xsl'


def main():
    doc = rest_to_docopt(__doc__)
    args = docopt(doc, version=version)
    init_logger(args)

    init_with_environ()

    hwp5path = args['<hwp5file>']
    root = os.path.basename(hwp5path)
    if root.lower().endswith('.hwp'):
        root = root[0:-4]

    odt_transform = ODTTransform()

    if args['--document']:
        odt_transform.embedbin = not args['--no-embed-image']
        transform = odt_transform.transform_to_single_document
        dest_path = root + '.fodt'
    elif args['--styles']:
        odt_transform.embedbin = args['--embed-image']
        transform = odt_transform.transform_to_style
        dest_path = root + '.styles.xml'
    elif args['--content']:
        odt_transform.embedbin = args['--embed-image']
        transform = odt_transform.transform_to_content
        dest_path = root + '.content.xml'
    else:
        odt_transform.embedbin = args['--embed-image']
        transform = odt_transform.transform_to_package
        dest_path = root + '.odt'

    dest_path = args['--output'] or dest_path

    from hwp5.dataio import ParseError
    try:
        transform(hwp5path, dest_path)
    except ParseError, e:
        e.print_to_logger(logger)
    except InvalidHwp5FileError, e:
        logger.error('%s', e)
        sys.exit(1)


def init_with_environ():
    if 'PYHWP_XSLTPROC' in os.environ:
        from hwp5.plat import xsltproc
        xsltproc.executable = os.environ['PYHWP_XSLTPROC']
        xsltproc.enable()

    if 'PYHWP_XMLLINT' in os.environ:
        from hwp5.plat import xmllint
        xmllint.executable = os.environ['PYHWP_XMLLINT']
        xmllint.enable()


class ImplementationNotAvailable(Exception):
    pass


class ODTTransform:

    def __init__(self, xslt_compile=None, relaxng_compile=None,
                 embedbin=False):
        '''
        >>> from hwp5.hwp5odt import ODTTransform
        >>> T = ODTTransform()
        '''
        self.xslt_compile = xslt_compile or self.get_default_xslt_compile()
        if relaxng_compile is None:
            try:
                relaxng_compile = self.get_default_relaxng_compile()
            except ImplementationNotAvailable:
                relaxng_compile = None
        self.relaxng_compile = relaxng_compile
        self.embedbin = embedbin

    @classmethod
    def get_default_xslt_compile(cls):
        xslt_compile = plat.get_xslt_compile()
        if not xslt_compile:
            raise ImplementationNotAvailable('xslt')
        return xslt_compile

    @classmethod
    def get_default_relaxng_compile(cls):
        relaxng_compile = plat.get_relaxng_compile()
        if not relaxng_compile:
            raise ImplementationNotAvailable('relaxng')
        return relaxng_compile

    @property
    def transform_to_style(self):
        '''
        >>> T.transform_to_style(HWP5PATH, 'style.xml')
        '''
        transform_xhwp5 = self.transform_xhwp5_to_style
        return self.make_transform_hwp5(transform_xhwp5)

    @property
    def transform_to_content(self):
        '''
        >>> T.transform_to_content(HWP5PATH, 'content.xml')
        '''
        transform_xhwp5 = self.transform_xhwp5_to_content
        return self.make_transform_hwp5(transform_xhwp5)

    @property
    def transform_to_single_document(self):
        '''
        >>> T.transform_to_single_document(HWP5PATH, 'transformed.fodt')
        '''
        transform_xhwp5 = self.transform_xhwp5_to_single_document
        return self.make_transform_hwp5(transform_xhwp5)

    def transform_to_package(self, hwp5path, odt_path):
        '''
        >>> T.transform_to_package(HWP5PATH, 'transformed.odt')
        '''
        odtpkg = ODTPackage(odt_path)
        try:
            hwp5file = Hwp5File(hwp5path)
            try:
                with self.transformed_xhwp5_at_temp(hwp5file) as xml_path:
                    self.transform_xhwp5_into_package(xml_path, odtpkg)

                if 'BinData' in hwp5file:
                    bindata = hwp5file['BinData']
                    for name in bindata:
                        f = bindata[name].open()
                        path = 'bindata/' + name
                        mimetype = 'application/octet-stream'
                        odtpkg.insert_stream(f, path, mimetype)
            finally:
                hwp5file.close()
        finally:
            odtpkg.close()

    @cached_property
    def transform_xhwp5_to_style(self):
        '''
        >>> T.transform_xhwp5_to_style(HWP5XML, 'style.xml')
        '''
        resource_path = RESOURCE_PATH_XSL_STYLE
        return self.make_odf_transform(resource_path)

    @cached_property
    def transform_xhwp5_to_content(self):
        '''
        >>> T.transform_xhwp5_to_content(HWP5XML, 'content.xml')
        '''
        resource_path = RESOURCE_PATH_XSL_CONTENT
        return self.make_odf_transform(resource_path)

    @cached_property
    def transform_xhwp5_to_single_document(self):
        '''
        >>> T.transform_xhwp5_to_single_document(HWP5XML, 'transformed.fodf')
        '''
        resource_path = RESOURCE_PATH_XSL_SINGLE_DOCUMENT
        return self.make_odf_transform(resource_path)

    @cached_property
    def validate_odf(self):
        '''
        >>> T.validate_odf('style.xml')
        '''
        return self.make_odf_validate()

    @property
    def transform_xhwp5_into_package(self):
        '''
        >>> with closing(ODTPackage('transformed.odt')) as odtpkg:
        >>>     T.transform_xhwp5_into_package(HWP5XML, odtpkg)
        '''
        def transform(xhwp5path, odtpkg):
            with self.transformed_style_at_temp(xhwp5path) as path:
                odtpkg.insert_path(path, 'styles.xml', 'text/xml')
            with self.transformed_content_at_temp(xhwp5path) as path:
                odtpkg.insert_path(path, 'content.xml', 'text/xml')

            from cStringIO import StringIO
            rdf = StringIO()
            manifest_rdf(rdf)
            rdf.seek(0)
            odtpkg.insert_stream(rdf, 'manifest.rdf',
                                 'application/rdf+xml')
        return transform

    def transformed_style_at_temp(self, xhwp5path):
        '''
        >>> with T.transformed_style_at_temp(HWP5XML) as tmp_path:
        ...     odt_transform.validate_odf(tmp_path)
        '''
        transform_xhwp5 = self.transform_xhwp5_to_style
        return transformed_at_temp_path(xhwp5path, transform_xhwp5)

    def transformed_content_at_temp(self, xhwp5path):
        '''
        >>> with T.transformed_content_at_temp(HWP5XML) as tmp_path:
        ...     odt_transform.validate_odf(tmp_path)
        '''
        transform_xhwp5 = self.transform_xhwp5_to_content
        return transformed_at_temp_path(xhwp5path, transform_xhwp5)

    def transformed_single_document_at_temp(self, xhwp5path):
        '''
        >>> with T.transformed_single_document_at_temp(HWP5XML) as tmp_path:
        ...     odt_transform.validate_odf(tmp_path)
        '''
        transform_xhwp5 = self.transform_xhwp5_to_single_document
        return transformed_at_temp_path(xhwp5path, transform_xhwp5)

    @contextmanager
    def transformed_xhwp5_at_temp(self, hwp5file):
        with mkstemp_open() as (tmp_path, f):
            hwp5file.xmlevents(embedbin=self.embedbin).dump(f)
            yield tmp_path

    def make_transform_hwp5(self, transform_xhwp5):
        def transform_hwp5(hwp5path, out_path):
            hwp5file = Hwp5File(hwp5path)
            try:
                with self.transformed_xhwp5_at_temp(hwp5file) as xhwp5path:
                    return transform_xhwp5(xhwp5path, out_path)
            finally:
                hwp5file.close()
        return transform_hwp5

    def make_odf_transform(self, resource_path):
        transform = self.make_xsl_transform(resource_path)
        validate = self.validate_odf
        if validate:
            def validating_transform(inp, out):
                transform(inp, out)
                validate(out)
            return validating_transform
        else:
            return transform

    def make_xsl_transform(self, resource_path):
        with hwp5_resources_path(resource_path) as xsl_path:
            return self.xslt_compile(xsl_path)

    def make_odf_validate(self):
        if self.relaxng_compile:
            with hwp5_resources_path(RESOURCE_PATH_RNG) as rng_path:
                return self.relaxng_compile(rng_path)


@contextmanager
def transformed_at_temp_path(inp_path, transform):
    with mkstemp_open() as (tmp_path, f):
        f.close()
        transform(inp_path, tmp_path)
        yield tmp_path


class ODTPackage(object):
    def __init__(self, path_or_zipfile):
        self.files = []

        if isinstance(path_or_zipfile, basestring):
            from zipfile import ZipFile
            zipfile = ZipFile(path_or_zipfile, 'w')
        else:
            zipfile = path_or_zipfile
        self.zf = zipfile

    def insert_path(self, src_path, path, media_type):
        with file(src_path, 'rb') as f:
            self.insert_stream(f, path, media_type)

    def insert_stream(self, f, path, media_type):
        if isinstance(path, unicode):
            path_bytes = path.encode('utf-8')
            path_unicode = path
        else:
            path_bytes = path
            path_unicode = unicode(path)
        self.zf.writestr(path_bytes, f.read())
        self.files.append(dict(full_path=path_unicode, media_type=media_type))

    def close(self):

        from cStringIO import StringIO
        manifest = StringIO()
        manifest_xml(manifest, self.files)
        manifest.seek(0)
        self.zf.writestr('META-INF/manifest.xml', manifest.getvalue())
        self.zf.writestr('mimetype', 'application/vnd.oasis.opendocument.text')

        self.zf.close()


def hwp5_resources_filename(path):
    ''' get paths of 'hwp5' package resources '''
    return pkg_resources_filename('hwp5', path)


@contextmanager
def hwp5_resources_path(path):
    yield pkg_resources_filename('hwp5', path)


def unlink_or_warning(path):
    try:
        os.unlink(path)
    except Exception, e:
        logger.exception(e)
        logger.warning('%s cannot be deleted', path)


@contextmanager
def mkstemp_open(*args, **kwargs):

    if (kwargs.get('text', False) or (len(args) >= 4 and args[3])):
        text = True
    else:
        text = False

    mode = 'w+' if text else 'wb+'
    fd, path = tempfile.mkstemp(*args, **kwargs)
    try:
        f = os.fdopen(fd, mode)
        try:
            yield path, f
        finally:
            try:
                f.close()
            except Exception:
                pass
    finally:
        unlink_or_warning(path)


def manifest_xml(f, files):
    from xml.sax.saxutils import XMLGenerator
    xml = XMLGenerator(f, 'utf-8')
    xml.startDocument()

    uri = 'urn:oasis:names:tc:opendocument:xmlns:manifest:1.0'
    prefix = 'manifest'
    xml.startPrefixMapping(prefix, uri)

    def startElement(name, attrs):
        attrs = dict(((uri, n), v) for n, v in attrs.iteritems())
        xml.startElementNS((uri, name), prefix + ':' + name, attrs)

    def endElement(name):
        xml.endElementNS((uri, name), prefix + ':' + name)

    def file_entry(full_path, media_type, **kwargs):
        attrs = {'media-type': media_type, 'full-path': full_path}
        attrs.update(dict((n.replace('_', '-'), v)
                          for n, v in kwargs.iteritems()))
        startElement('file-entry', attrs)
        endElement('file-entry')

    startElement('manifest', dict(version='1.2'))
    file_entry('/', 'application/vnd.oasis.opendocument.text', version='1.2')
    for e in files:
        e = dict(e)
        full_path = e.pop('full_path')
        media_type = e.pop('media_type', 'application/octet-stream')
        file_entry(full_path, media_type)
    endElement('manifest')

    xml.endPrefixMapping(prefix)
    xml.endDocument()


def manifest_rdf(f):
    f.write('''<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:pkg="http://docs.oasis-open.org/ns/office/1.2/meta/pkg#"
    xmlns:odf="http://docs.oasis-open.org/ns/office/1.2/meta/odf#">
    <pkg:Document rdf:about="">
        <pkg:hasPart rdf:resource="content.xml"/>
        <pkg:hasPart rdf:resource="styles.xml"/>
    </pkg:Document>
    <odf:ContentFile rdf:about="content.xml"/>
    <odf:StylesFile rdf:about="styles.xml"/>
</rdf:RDF>''')


def mimetype(f):
    f.write('application/vnd.oasis.opendocument.text')
