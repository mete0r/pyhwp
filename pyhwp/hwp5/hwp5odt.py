# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2013 mete0r <mete0r@sarangbang.or.kr>
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


logger = logging.getLogger(__name__)


def main():
    import os
    import sys
    from hwp5 import __version__ as version
    from hwp5.proc import rest_to_docopt
    from hwp5.proc import init_logger
    from hwp5 import plat
    from hwp5.errors import InvalidHwp5FileError
    from docopt import docopt
    doc = rest_to_docopt(__doc__)
    args = docopt(doc, version=version)
    init_logger(args)

    if 'PYHWP_XSLTPROC' in os.environ:
        from hwp5.plat import xsltproc
        xsltproc.executable = os.environ['PYHWP_XSLTPROC']
        xsltproc.enable()

    if 'PYHWP_XMLLINT' in os.environ:
        from hwp5.plat import xmllint
        xmllint.executable = os.environ['PYHWP_XMLLINT']
        xmllint.enable()

    xslt = plat.get_xslt()
    if xslt is None:
        logger.error('no XSLT implementation is available.')
        sys.exit(1)

    rng = plat.get_relaxng()
    if rng is None:
        logger.warning('no RelaxNG implementation is available.')

    if args['--document']:
        convert = ODTSingleDocumentConverter(xslt, rng, not args['--no-embed-image'])
    elif args['--styles']:
        convert = ODTStylesConverter(xslt, rng)
    elif args['--content']:
        convert = ODTContentConverter(xslt, rng, args['--embed-image'])
    else:
        convert = ODTPackageConverter(xslt, rng, args['--embed-image'])

    hwpfilename = args['<hwp5file>']
    root = os.path.basename(hwpfilename)
    if root.lower().endswith('.hwp'):
        root = root[0:-4]
    dest_path = root + '.' + convert.dest_ext

    from hwp5.dataio import ParseError
    try:
        convert.convert(hwpfilename, dest_path)
    except ParseError, e:
        e.print_to_logger(logger)
    except InvalidHwp5FileError, e:
        logger.error('%s', e)
        sys.exit(1)


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
    from importhelper import pkg_resources_filename
    return pkg_resources_filename('hwp5', path)


def unlink_or_warning(path):
    try:
        os.unlink(path)
    except Exception, e:
        logger.exception(e)
        logger.warning('%s cannot be deleted', path)


class ConverterBase(object):
    def __init__(self, xslt, validator):
        self.xslt = xslt
        self.validator = validator

    def make_xhwp5file(self, hwp5file, embedimage):
        import os
        import tempfile
        fd, path = tempfile.mkstemp()
        try:
            f = os.fdopen(fd, 'w')
            try:
                hwp5file.xmlevents(embedbin=embedimage).dump(f)
            finally:
                f.close()
        except:
            unlink_or_warning(path)
            raise
        else:
            return path

    def transform(self, xsl_path, xhwp5_path):
        import os
        import tempfile
        fd, path = tempfile.mkstemp()
        try:
            os.close(fd)
            self.transform_to(xsl_path, xhwp5_path, path)
        except:
            unlink_or_warning(path)
            raise
        else:
            return path

    def transform_to(self, xsl_path, xhwp5_path, output_path):
        self.xslt(xsl_path, xhwp5_path, output_path)
        if self.validator is not None:
            valid = self.validator(output_path)
            if not valid:
                raise Exception('validation failed')


class ODTConverter(ConverterBase):
    def __init__(self, xslt, relaxng=None):
        rng_path = 'odf-relaxng/OpenDocument-v1.2-os-schema.rng'
        rng_path = hwp5_resources_filename(rng_path)
        if relaxng:
            validate = lambda path: relaxng(rng_path, path)
        else:
            validate = lambda path: True
        ConverterBase.__init__(self, xslt, validate)

    def convert(self, hwpfilename, dest_path):
        from .xmlmodel import Hwp5File
        hwpfile = Hwp5File(hwpfilename)
        try:
            self.convert_to(hwpfile, dest_path)
        finally:
            hwpfile.close()


class ODTStylesConverter(ODTConverter):

    dest_ext = 'styles.xml'

    def __init__(self, xslt, relaxng=None):
        ODTConverter.__init__(self, xslt, relaxng)
        self.xsl_styles = hwp5_resources_filename('xsl/odt/styles.xsl')

    def convert_to(self, hwp5file, output_path):
        xhwp5_path = self.make_xhwp5file(hwp5file, embedimage=False)
        try:
            self.transform_to(self.xsl_styles, xhwp5_path, output_path)
        finally:
            unlink_or_warning(xhwp5_path)


class ODTContentConverter(ODTConverter):

    dest_ext = 'content.xml'

    def __init__(self, xslt, relaxng=None, embedimage=False):
        ODTConverter.__init__(self, xslt, relaxng)
        self.xsl_content = hwp5_resources_filename('xsl/odt/content.xsl')
        self.embedimage = embedimage

    def convert_to(self, hwp5file, output_path):
        xhwp5_path = self.make_xhwp5file(hwp5file, embedimage=self.embedimage)
        try:
            self.transform_to(self.xsl_content, xhwp5_path, output_path)
        finally:
            unlink_or_warning(xhwp5_path)


class ODTPackageConverter(ODTConverter):

    dest_ext = 'odt'

    def __init__(self, xslt, relaxng=None, embedimage=False):
        ODTConverter.__init__(self, xslt, relaxng)
        self.xsl_styles = hwp5_resources_filename('xsl/odt/styles.xsl')
        self.xsl_content = hwp5_resources_filename('xsl/odt/content.xsl')
        self.embedimage = embedimage

    def convert_to(self, hwp5file, odtpkg_path):
        odtpkg = ODTPackage(odtpkg_path)
        try:
            self(hwp5file, odtpkg)
        finally:
            odtpkg.close()

    def __call__(self, hwp5file, odtpkg):
        xhwp5_path = self.make_xhwp5file(hwp5file, self.embedimage)
        try:
            styles, content = self.make_styles_and_content(xhwp5_path)
        finally:
            unlink_or_warning(xhwp5_path)

        try:
            with file(styles) as f:
                odtpkg.insert_stream(f, 'styles.xml', 'text/xml')
            with file(content) as f:
                odtpkg.insert_stream(f, 'content.xml', 'text/xml')
        finally:
            unlink_or_warning(styles)
            unlink_or_warning(content)

        from cStringIO import StringIO
        rdf = StringIO()
        manifest_rdf(rdf)
        rdf.seek(0)
        odtpkg.insert_stream(rdf, 'manifest.rdf', 'application/rdf+xml')

        for f, name, mimetype in self.additional_files(hwp5file):
            odtpkg.insert_stream(f, name, mimetype)

    def make_styles_and_content(self, xhwp5):
        styles = self.transform(self.xsl_styles, xhwp5)
        try:
            content = self.transform(self.xsl_content, xhwp5)
            try:
                return styles, content
            except:
                unlink_or_warning(content)
                raise
        except:
            unlink_or_warning(styles)
            raise

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
        xhwp5_path = self.make_xhwp5file(hwp5file, self.embedimage)
        try:
            self.transform_to(self.xsl_document, xhwp5_path, output_path)
        finally:
            unlink_or_warning(xhwp5_path)


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
    f.write('''<?xml version="1.0" encoding="utf-8"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><ns1:Document xmlns:ns1="http://docs.oasis-open.org/ns/office/1.2/meta/pkg#" rdf:about=""><ns1:hasPart rdf:resource="content.xml"/><ns1:hasPart rdf:resource="styles.xml"/></ns1:Document><ns2:ContentFile xmlns:ns2="http://docs.oasis-open.org/ns/office/1.2/meta/odf#" rdf:about="content.xml"/><ns3:StylesFile xmlns:ns3="http://docs.oasis-open.org/ns/office/1.2/meta/odf#" rdf:about="styles.xml"/></rdf:RDF>''')


def mimetype(f):
    f.write('application/vnd.oasis.opendocument.text')
