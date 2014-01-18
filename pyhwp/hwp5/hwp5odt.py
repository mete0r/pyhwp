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


logger = logging.getLogger(__name__)


def main():
    doc = rest_to_docopt(__doc__)
    args = docopt(doc, version=version)
    init_logger(args)

    init_with_environ()

    convert = make_converter(args)

    hwpfilename = args['<hwp5file>']
    root = os.path.basename(hwpfilename)
    if root.lower().endswith('.hwp'):
        root = root[0:-4]
    dest_path = root + '.' + convert.dest_ext

    from hwp5.dataio import ParseError
    try:
        with convert.prepare():
            convert.convert(hwpfilename, dest_path)
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


def make_converter(args):
    xslt = plat.get_xslt()
    if xslt is None:
        logger.error('no XSLT implementation is available.')
        sys.exit(1)

    rng = plat.get_relaxng()
    if rng is None:
        logger.warning('no RelaxNG implementation is available.')

    if args['--document']:
        return ODTSingleDocumentConverter(xslt, rng,
                                          not args['--no-embed-image'])
    elif args['--styles']:
        return ODTStylesConverter(xslt, rng)
    elif args['--content']:
        return ODTContentConverter(xslt, rng, args['--embed-image'])
    else:
        return ODTPackageConverter(xslt, rng, args['--embed-image'])


class ODTPackage(object):
    def __init__(self, path_or_zipfile):
        self.files = []

        if isinstance(path_or_zipfile, basestring):
            from zipfile import ZipFile
            zipfile = ZipFile(path_or_zipfile, 'w')
        else:
            zipfile = path_or_zipfile
        self.zf = zipfile

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


class ConverterBase(object):
    def __init__(self, xslt, validator):
        self.xslt = xslt
        self.validator = validator

    @contextmanager
    def make_xhwp5file(self, hwp5file, embedimage):
        with mkstemp_open(prefix='hwp5-', suffix='.xml',
                          text=True) as (path, f):
            hwp5file.xmlevents(embedbin=embedimage).dump(f)
            yield path

    @contextmanager
    def transform(self, xsl_path, xhwp5_path):
        with mkstemp_open(prefix='xslt-') as (path, f):
            f.close()
            self.transform_to(xsl_path, xhwp5_path, path)
            yield path

    def transform_to(self, xsl_path, xhwp5_path, output_path):
        self.xslt(xsl_path, xhwp5_path, output_path)
        if self.validator is not None:
            valid = self.validator(output_path)
            if not valid:
                raise Exception('validation failed')


class ODTConverter(ConverterBase):

    rng_path = 'odf-relaxng/OpenDocument-v1.2-os-schema.rng'

    def __init__(self, xslt, relaxng=None):
        self.relaxng = relaxng
        ConverterBase.__init__(self, xslt, None)

    @contextmanager
    def prepare(self):
        if self.relaxng:
            with hwp5_resources_path(self.rng_path) as rng_path:
                self.validator = lambda path: self.relaxng(rng_path, path)
                yield
                self.validator = None
        else:
            yield

    def convert(self, hwpfilename, dest_path):
        from .xmlmodel import Hwp5File
        hwpfile = Hwp5File(hwpfilename)
        try:
            self.convert_to(hwpfile, dest_path)
        finally:
            hwpfile.close()


class ODTStylesConverter(ODTConverter):

    dest_ext = 'styles.xml'
    styles_xsl_path = 'xsl/odt/styles.xsl'

    @contextmanager
    def prepare(self):
        with ODTConverter.prepare(self):
            with hwp5_resources_path(self.styles_xsl_path) as path:
                self.xsl_styles = path
                yield
                del self.xsl_styles

    def convert_to(self, hwp5file, output_path):
        with self.make_xhwp5file(hwp5file, embedimage=False) as xhwp5_path:
            self.transform_to(self.xsl_styles, xhwp5_path, output_path)


class ODTContentConverter(ODTConverter):

    dest_ext = 'content.xml'
    content_xsl_path = 'xsl/odt/content.xsl'

    def __init__(self, xslt, relaxng=None, embedimage=False):
        ODTConverter.__init__(self, xslt, relaxng)
        self.embedimage = embedimage

    @contextmanager
    def prepare(self):
        with ODTConverter.prepare(self):
            with hwp5_resources_path(self.content_xsl_path) as path:
                self.xsl_content = path
                yield
                del self.xsl_content

    def convert_to(self, hwp5file, output_path):
        with self.make_xhwp5file(hwp5file, self.embedimage) as xhwp5_path:
            self.transform_to(self.xsl_content, xhwp5_path, output_path)


class ODTPackageConverter(ODTConverter):

    dest_ext = 'odt'
    styles_xsl_path = 'xsl/odt/styles.xsl'
    content_xsl_path = 'xsl/odt/content.xsl'

    def __init__(self, xslt, relaxng=None, embedimage=False):
        ODTConverter.__init__(self, xslt, relaxng)
        self.embedimage = embedimage

    @contextmanager
    def prepare(self):
        with ODTConverter.prepare(self):
            with hwp5_resources_path(self.content_xsl_path) as path:
                self.xsl_content = path
                with hwp5_resources_path(self.styles_xsl_path) as path:
                    self.xsl_styles = path
                    yield
                    del self.xsl_styles
                del self.xsl_content

    def convert_to(self, hwp5file, odtpkg_path):
        odtpkg = ODTPackage(odtpkg_path)
        try:
            self.build_odtpkg_streams(hwp5file, odtpkg)
        finally:
            odtpkg.close()

    def build_odtpkg_streams(self, hwp5file, odtpkg):
        with self.make_xhwp5file(hwp5file, self.embedimage) as xhwp5_path:
            with self.make_styles(xhwp5_path) as f:
                odtpkg.insert_stream(f, 'styles.xml', 'text/xml')
            with self.make_content(xhwp5_path) as f:
                odtpkg.insert_stream(f, 'content.xml', 'text/xml')

        from cStringIO import StringIO
        rdf = StringIO()
        manifest_rdf(rdf)
        rdf.seek(0)
        odtpkg.insert_stream(rdf, 'manifest.rdf', 'application/rdf+xml')

        for f, name, mimetype in self.additional_files(hwp5file):
            odtpkg.insert_stream(f, name, mimetype)

    @contextmanager
    def make_styles(self, xhwp5):
        with self.transform(self.xsl_styles, xhwp5) as path:
            with open(path) as f:
                yield f

    @contextmanager
    def make_content(self, xhwp5):
        with self.transform(self.xsl_content, xhwp5) as path:
            with open(path) as f:
                yield f

    def additional_files(self, hwp5file):
        if 'BinData' in hwp5file:
            bindata = hwp5file['BinData']
            for name in bindata:
                f = bindata[name].open()
                yield f, 'bindata/' + name, 'application/octet-stream'


class ODTSingleDocumentConverter(ODTConverter):

    dest_ext = 'fodt'

    def __init__(self, xslt, relaxng=None, embedimage=False):
        ODTConverter.__init__(self, xslt, relaxng)
        self.xsl_document = hwp5_resources_filename('xsl/odt/document.xsl')
        self.embedimage = embedimage

    def convert_to(self, hwp5file, output_path):
        with self.make_xhwp5file(hwp5file, self.embedimage) as xhwp5_path:
            self.transform_to(self.xsl_document, xhwp5_path, output_path)


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
