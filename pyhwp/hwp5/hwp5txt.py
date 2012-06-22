# -*- coding: utf-8 -*-
'''HWPv5 to text converter

Usage::

    hwp5txt <hwp5file>
    hwp5txt -h | --help
    hwp5txt --version

Options::

    -h --help       Show this screen
    --version       Show version
'''
import os, os.path

def main():
    from hwp5 import __version__ as version
    from hwp5.proc import rest_to_docopt
    from docopt import docopt
    doc = rest_to_docopt(__doc__)
    args = docopt(doc, version=version)
    make(args)

def make(args):
    hwp5_filename = args['<hwp5file>']
    from .xmlmodel import Hwp5File
    hwp5file = Hwp5File(hwp5_filename)
    try:
        xslt = xslt_plaintext()

        rootname = os.path.basename(hwp5_filename)
        if rootname.lower().endswith('.hwp'):
            rootname = rootname[0:-4]

        hwp5xml_filename = rootname+'.xml'
        xmlfile = file(hwp5xml_filename, 'w')
        try:
            hwp5file.xmlevents().dump(xmlfile)
        finally:
            xmlfile.close()

        xmlfile = file(hwp5xml_filename, 'r')
        try:
            txtfile = file(rootname+'.txt', 'w')
            try:
                xslt(xmlfile, txtfile)
            finally:
                txtfile.close()
        finally:
            xmlfile.close()

        os.unlink(hwp5xml_filename)
    finally:
        hwp5file.close()

def xslt_plaintext():
    from .tools import xsltproc
    import pkg_resources
    content_xsl = pkg_resources.resource_filename('hwp5', 'xsl/plaintext.xsl')
    return xsltproc(content_xsl)
