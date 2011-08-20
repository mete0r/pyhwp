import os, os.path

def main():
    import sys
    hwpfilename = sys.argv[1]
    make(hwpfilename)

def make(hwpfilename):
    root = os.path.basename(hwpfilename)
    if root.lower().endswith('.hwp'):
        root = root[0:-4]

    from .filestructure import open
    from ._scriptutils import open_or_exit
    hwpfile = open_or_exit(open, hwpfilename)

    if not os.path.exists(root):
        os.mkdir(root)
    if not os.path.exists(root+'/META-INF'):
        os.mkdir(root+'/META-INF')
    if not os.path.exists(root+'/bindata'):
        os.mkdir(root+'/bindata')

    hwpxmlfilename = root+'.xml'
    hwpxmlfile = file(hwpxmlfilename, 'w')
    try:
        generate_hwp5xml(hwpxmlfile, hwpfile)
    finally:
        hwpxmlfile.close()

    files = []

    for bindata_name in hwpfile.list_bindata():
        bindata = hwpfile.bindata(bindata_name)

        f = file(root+'/bindata/'+bindata_name, 'w')
        try:
            f.write(bindata.read())
        finally:
            f.close()
        files.append(dict(full_path='bindata/'+bindata_name))
    
    f = file(root+'/content.xml', 'w')
    try:
        xslt_odt_content(f, hwpxmlfilename)
    finally:
        f.close()
    files.append(dict(full_path='content.xml', media_type='text/xml'))

    f = file(root+'/styles.xml', 'w')
    try:
        xslt_odt_styles(f, hwpxmlfilename)
    finally:
        f.close()
    files.append(dict(full_path='styles.xml', media_type='text/xml'))

    f = file(root+'/manifest.rdf', 'w')
    try:
        manifest_rdf(f)
    finally:
        f.close()
    files.append(dict(full_path='manifest.rdf', media_type='application/rdf+xml'))

    f = file(root+'/META-INF/manifest.xml', 'w')
    try:
        manifest_xml(f, files)
    finally:
        f.close()
    files.append('META-INF/manifest.xml')

    f = file(root+'/mimetype', 'w')
    try:
        mimetype(f)
    finally:
        f.close()
    files.append('mimetype')

    from zipfile import ZipFile
    zf = ZipFile(root+'.odt', 'w')
    for filename in files:
        if isinstance(filename, dict):
            filename = filename['full_path']
        zf.write(root+'/'+filename, filename)
        os.unlink(root+'/'+filename)
    zf.close()

    os.unlink(root+'.xml')
    os.rmdir(root+'/META-INF')
    os.rmdir(root+'/bindata')
    os.rmdir(root)

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

    startElement( 'manifest', dict() )
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
    import logging
    from .hwpxml import flatxml, XmlFormat
    flatxml(hwpfile, logging, XmlFormat(f))

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
