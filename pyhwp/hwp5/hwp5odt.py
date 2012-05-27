import os, os.path

def main():
    import sys
    hwpfilename = sys.argv[1]
    make(hwpfilename)

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

def hwp5file_to_odtpkg_converter(xsltproc):
    def convert(hwpfile, odtpkg):
        import tempfile
        hwpxmlfile = tempfile.TemporaryFile()
        try:
            generate_hwp5xml(hwpxmlfile, hwpfile)

            xslt_styles = xsltproc(xsl.styles)
            xslt_content = xsltproc(xsl.content)

            styles = tempfile.TemporaryFile()
            hwpxmlfile.seek(0)
            xslt_styles(hwpxmlfile, styles)
            styles.seek(0)

            content = tempfile.TemporaryFile()
            hwpxmlfile.seek(0)
            xslt_content(hwpxmlfile, content)
            content.seek(0)

            def additional_files():
                for bindata_name in hwpfile.list_bindata():
                    bindata = hwpfile.bindata(bindata_name)
                    yield bindata, 'bindata/'+bindata_name, 'application/octet-stream'

            make_odtpkg(odtpkg, styles, content, additional_files())

        finally:
            hwpxmlfile.close()
    return convert

def make(hwpfilename):
    root = os.path.basename(hwpfilename)
    if root.lower().endswith('.hwp'):
        root = root[0:-4]

    from .filestructure import open
    from ._scriptutils import open_or_exit
    hwpfile = open_or_exit(open, hwpfilename)

    hwp5file_convert_to_odtpkg = hwp5file_to_odtpkg_converter(xsltproc)

    try:
        odtpkg = ODTPackage(root+'.odt')
        try:
            hwp5file_convert_to_odtpkg(hwpfile, odtpkg)
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

def generate_hwp5xml(f, hwpfile):
    from .xmlmodel import flatxml
    from .xmlformat import XmlFormat
    flatxml(hwpfile, XmlFormat(f))

def xslt_odt_content(f, hwpxmlfilename):
    import pkg_resources
    content_xsl = pkg_resources.resource_filename('hwp5', 'xsl/odt-content.xsl')
    import subprocess
    p = subprocess.Popen(['xsltproc', content_xsl, hwpxmlfilename], stdout=f)
    p.wait()

def xslt_odt_styles(f, hwpxmlfilename):
    import pkg_resources
    styles_xsl = pkg_resources.resource_filename('hwp5', 'xsl/odt-styles.xsl')
    import subprocess
    p = subprocess.Popen(['xsltproc', styles_xsl, hwpxmlfilename], stdout=f)
    p.wait()

import pkg_resources
class XSLs(object):
    @property
    def content(self):
        return pkg_resources.resource_filename('hwp5', 'xsl/odt-content.xsl')

    @property
    def styles(self):
        return pkg_resources.resource_filename('hwp5', 'xsl/odt-styles.xsl')

xsl = XSLs()

def xsltproc(xsl_filepath):
    ''' create a XSLT function with specified XSL stylesheet file.

        xsl_filepath: a XSL Stylesheet path in filesystem

        returns a transform function
    '''

    def autoclose(p):
        ''' start a detached thread which waits the given subprocess terminates. '''
        import threading
        t = threading.Thread(target=p.wait)
        t.daemon = True
        t.start()

    def transform(infile=None, outfile=None):
        ''' transform file streams with XSL stylesheet at `%s'

            `xsltproc' executable should be in PATH directories.

            transform(infile, outfile)
                : transform infile stream into outfile stream

            transform(infile):
                : returns transformed stream (readable sink)

            transform(outfile=outfile)
                : returns stream to be transformed (writable source)

            transform():
                : returns a tuple of (writable source, readable sink) of transformation
        '''
        import subprocess
        import logging
        logging.debug('xsltproc process starting')

        stdin = infile or subprocess.PIPE
        stdout = outfile or subprocess.PIPE

        p = subprocess.Popen(['xsltproc', xsl_filepath, '-'], stdin=stdin, stdout=stdout)

        logging.debug('xsltproc process started')

        if infile is None and outfile is None:
            autoclose(p)
            return p.stdin, p.stdout # transform source, sink
        elif outfile is None:
            autoclose(p)
            return p.stdout # transformed stream
        elif infile is None:
            autoclose(p)
            return p.stdin # stream to be transformed
        else:
            p.wait()

        logging.debug('xsltproc process end')
    transform.__doc__ = transform.__doc__%xsl_filepath
    return transform

hwp5file_convert_to_odtpkg = hwp5file_to_odtpkg_converter(xsltproc)
