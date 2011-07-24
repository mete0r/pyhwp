import os, os.path

def main():
    import sys
    hwpfilename = sys.argv[1]
    make(hwpfilename)

def make(hwp5_filename):
    rootname = os.path.basename(hwp5_filename)
    if rootname.lower().endswith('.hwp'):
        rootname = rootname[0:-4]

    hwp5xml_filename = rootname+'.xml'
    f = file(hwp5xml_filename, 'w')
    try:
        hwp5xml(f, hwp5_filename)
    finally:
        f.close()

    f = file(rootname+'.txt', 'w')
    try:
        xslt_plaintext(f, hwp5xml_filename)
    finally:
        f.close()

    os.unlink(hwp5xml_filename)

def hwp5xml(f, hwp5_filename):
    import logging
    from .filestructure import File
    from .hwpxml import flatxml, XmlFormat
    hwpfile = File(hwp5_filename)
    flatxml(hwpfile, logging, XmlFormat(f))

def xslt_plaintext(f, hwpxmlfilename):
    import pkg_resources
    content_xsl = pkg_resources.resource_filename('hwp5', 'xsl/plaintext.xsl')
    import subprocess
    p = subprocess.Popen(['xsltproc', content_xsl, hwpxmlfilename], stdout=f)
    p.wait()
