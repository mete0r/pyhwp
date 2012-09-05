# -*- coding: utf-8 -*-
'''HWPv5 to ODT converter

Usage::

    hwp5odt [--embed-image] <hwp5file>
    hwp5odt -h | --help
    hwp5odt --version

Options::

    -h --help       Show this screen
    --version       Show version
'''

import os, os.path
from hwp5 import tools
import logging


logger = logging.getLogger(__name__)


def main():
    import sys
    from hwp5 import __version__ as version
    from hwp5.proc import rest_to_docopt
    from hwp5.errors import InvalidHwp5FileError
    from docopt import docopt
    doc = rest_to_docopt(__doc__)
    args = docopt(doc, version=version)
    logging.getLogger('hwp5').addHandler(logging.StreamHandler())

    from hwp5.dataio import ParseError
    try:
        make(args)
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
        self.zf.writestr(path, f.read())
        self.files.append(dict(full_path=path, media_type=media_type))

    def close(self):

        from cStringIO import StringIO
        manifest = StringIO()
        manifest_xml(manifest, self.files)
        manifest.seek(0)
        self.zf.writestr('META-INF/manifest.xml', manifest.getvalue())
        self.zf.writestr('mimetype', 'application/vnd.oasis.opendocument.text')

        self.zf.close()

def make_odtpkg(odtpkg, styles, content, additional_files):
    from cStringIO import StringIO

    rdf = StringIO()
    manifest_rdf(rdf)
    rdf.seek(0)
    odtpkg.insert_stream(rdf, 'manifest.rdf', 'application/rdf+xml')
    odtpkg.insert_stream(styles, 'styles.xml', 'text/xml')
    odtpkg.insert_stream(content, 'content.xml', 'text/xml')
    for additional in additional_files:
        odtpkg.insert_stream(*additional)


def hwp5_resources_filename(path):
    ''' get paths of 'hwp5' package resources '''
    from importhelper import pkg_resources_filename
    return pkg_resources_filename('hwp5', path)


class Converter(object):
    def __init__(self, xsltproc, relaxng=None):
        xsl_styles = hwp5_resources_filename('xsl/odt-styles.xsl')
        xsl_content = hwp5_resources_filename('xsl/odt-content.xsl')
        schema = 'odf-relaxng/OpenDocument-v1.2-os-schema.rng'
        schema = hwp5_resources_filename(schema)

        self.xslt_styles = xsltproc(xsl_styles)
        self.xslt_content = xsltproc(xsl_content)

        if relaxng is not None:
            self.relaxng_validate = relaxng(schema)
        else:
            self.relaxng_validate = None

    def __call__(self, hwpfile, odtpkg, embedimage=False):
        import tempfile
        hwpxmlfile = tempfile.TemporaryFile()
        try:
            hwpfile.xmlevents(embedbin=embedimage).dump(hwpxmlfile)

            styles = tempfile.TemporaryFile()
            hwpxmlfile.seek(0)
            self.xslt_styles(hwpxmlfile, styles)
            styles.seek(0)
            if self.relaxng_validate:
                self.relaxng_validate(styles)
                styles.seek(0)

            content = tempfile.TemporaryFile()
            hwpxmlfile.seek(0)
            self.xslt_content(hwpxmlfile, content)
            content.seek(0)
            if self.relaxng_validate:
                self.relaxng_validate(content)
                content.seek(0)

            def additional_files():
                if 'BinData' in hwpfile:
                    bindata = hwpfile['BinData']
                    for name in bindata:
                        f = bindata[name].open()
                        yield f, 'bindata/'+name, 'application/octet-stream'

            make_odtpkg(odtpkg, styles, content, additional_files())

        finally:
            hwpxmlfile.close()

convert = Converter(tools.xsltproc, tools.relaxng)

def make(args):
    hwpfilename = args['<hwp5file>']
    root = os.path.basename(hwpfilename)
    if root.lower().endswith('.hwp'):
        root = root[0:-4]

    from .xmlmodel import Hwp5File
    hwpfile = Hwp5File(hwpfilename)

    try:
        odtpkg = ODTPackage(root+'.odt')
        try:
            convert(hwpfile, odtpkg, args['--embed-image'])
        finally:
            odtpkg.close()
    finally:
        hwpfile.close()


def manifest_xml(f, files):
    from xml.sax.saxutils import XMLGenerator
    xml = XMLGenerator(f, 'utf-8')
    xml.startDocument()

    uri = 'urn:oasis:names:tc:opendocument:xmlns:manifest:1.0'
    prefix = 'manifest'
    xml.startPrefixMapping(prefix, uri)

    def startElement(name, attrs):
        attrs = dict( ((uri, n), v) for n, v in attrs.iteritems() )
        xml.startElementNS( (uri, name), prefix+':'+name, attrs)
    def endElement(name):
        xml.endElementNS( (uri, name), prefix+':'+name)

    def file_entry(full_path, media_type, **kwargs):
        attrs = {'media-type': media_type, 'full-path': full_path}
        attrs.update(dict((n.replace('_', '-'), v) for n, v in kwargs.iteritems()))
        startElement('file-entry', attrs)
        endElement('file-entry')

    startElement( 'manifest', dict(version='1.2') )
    file_entry('/', 'application/vnd.oasis.opendocument.text', version='1.2')
    for e in files:
        e = dict(e)
        full_path = e.pop('full_path')
        media_type = e.pop('media_type', 'application/octet-stream')
        file_entry(full_path, media_type)
    endElement( 'manifest' )

    xml.endPrefixMapping(prefix)
    xml.endDocument()

def manifest_rdf(f):
    f.write('''<?xml version="1.0" encoding="utf-8"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><ns1:Document xmlns:ns1="http://docs.oasis-open.org/ns/office/1.2/meta/pkg#" rdf:about=""><ns1:hasPart rdf:resource="content.xml"/><ns1:hasPart rdf:resource="styles.xml"/></ns1:Document><ns2:ContentFile xmlns:ns2="http://docs.oasis-open.org/ns/office/1.2/meta/odf#" rdf:about="content.xml"/><ns3:StylesFile xmlns:ns3="http://docs.oasis-open.org/ns/office/1.2/meta/odf#" rdf:about="styles.xml"/></rdf:RDF>''')

def mimetype(f):
    f.write('application/vnd.oasis.opendocument.text')
