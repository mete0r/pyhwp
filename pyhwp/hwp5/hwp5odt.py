import os, os.path

def main():
    import sys
    hwpfilename = sys.argv[1]
    make(hwpfilename)

def make(hwpfilename):
    rootname = os.path.basename(hwpfilename)
    if rootname.lower().endswith('.hwp'):
        rootname = rootname[0:-4]

    name = rootname

    if not os.path.exists(name):
        os.mkdir(name)
    if not os.path.exists(name+'/META-INF'):
        os.mkdir(name+'/META-INF')

    hwpxmlfilename = name+'.xml'
    hwpxmlfile = file(hwpxmlfilename, 'w')
    try:
        hwpxml_function(hwpxmlfile, hwpfilename)
    finally:
        hwpxmlfile.close()

    files = []
    
    f = file(name+'/content.xml', 'w')
    try:
        content_function(f, hwpxmlfilename)
    finally:
        f.close()
    files.append('content.xml')

    f = file(name+'/styles.xml', 'w')
    try:
        styles_function(f, hwpxmlfilename)
    finally:
        f.close()
    files.append('styles.xml')

    f = file(name+'/manifest.rdf', 'w')
    try:
        manifest_rdf(f)
    finally:
        f.close()
    files.append('manifest.rdf')

    f = file(name+'/mimetype', 'w')
    try:
        mimetype(f)
    finally:
        f.close()
    files.append('mimetype')

    f = file(name+'/META-INF/manifest.xml', 'w')
    try:
        manifest_xml(f)
    finally:
        f.close()
    files.append('META-INF/manifest.xml')

    from zipfile import ZipFile
    zf = ZipFile(name+'.odt', 'w')
    for filename in files:
        zf.write(name+'/'+filename, filename)
        os.unlink(name+'/'+filename)
    zf.close()

    os.unlink(name+'.xml')
    os.rmdir(name+'/META-INF')
    os.rmdir(name)

def manifest_xml(f):
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
    file_entry('content.xml', 'text/xml')
    file_entry('manifest.rdf', 'application/rdf+xml')
    file_entry('styles.xml', 'text/xml')
    endElement( 'manifest' )

    xml.endPrefixMapping(prefix)
    xml.endDocument()

#    f.write('''<?xml version="1.0" encoding="UTF-8"?><manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"><manifest:file-entry manifest:media-type="application/vnd.oasis.opendocument.text" manifest:version="1.2" manifest:full-path="/"/><manifest:file-entry manifest:media-type="text/xml" manifest:full-path="content.xml"/><manifest:file-entry manifest:media-type="application/rdf+xml" manifest:full-path="manifest.rdf"/><manifest:file-entry manifest:media-type="text/xml" manifest:full-path="styles.xml"/></manifest:manifest>''')

def manifest_rdf(f):
    f.write('''<?xml version="1.0" encoding="utf-8"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><ns1:Document xmlns:ns1="http://docs.oasis-open.org/ns/office/1.2/meta/pkg#" rdf:about=""><ns1:hasPart rdf:resource="content.xml"/><ns1:hasPart rdf:resource="styles.xml"/></ns1:Document><ns2:ContentFile xmlns:ns2="http://docs.oasis-open.org/ns/office/1.2/meta/odf#" rdf:about="content.xml"/><ns3:StylesFile xmlns:ns3="http://docs.oasis-open.org/ns/office/1.2/meta/odf#" rdf:about="styles.xml"/></rdf:RDF>''')

def mimetype(f):
    f.write('application/vnd.oasis.opendocument.text')

def hwpxml_function(f, hwpfilename):
    import logging
    from .filestructure import File
    from .hwpxml import flatxml, XmlFormat
    hwpfile = File(hwpfilename)
    flatxml(hwpfile, logging, XmlFormat(f))

def content_function(f, hwpxmlfilename):
    import subprocess
    p = subprocess.Popen(['xsltproc', 'xslt/odt-content.xsl', hwpxmlfilename], stdout=f)
    p.wait()

def styles_function(f, hwpxmlfilename):
    import subprocess
    p = subprocess.Popen(['xsltproc', 'xslt/odt-styles.xsl', hwpxmlfilename], stdout=f)
    p.wait()
