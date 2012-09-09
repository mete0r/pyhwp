# -*- coding: utf-8 -*-
#
#                   GNU AFFERO GENERAL PUBLIC LICENSE
#                      Version 3, 19 November 2007
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010 mete0r@sarangbang.or.kr
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
'''HWPv5 to text converter

Usage::

    hwp5txt [options] <hwp5file>
    hwp5txt -h | --help
    hwp5txt --version

Options::

    -h --help           Show this screen
    --version           Show version
    --loglevel=<level>  Set log level.
    --logfile=<file>    Set log file.
'''
import os, os.path

def main():
    from hwp5 import __version__ as version
    from hwp5.proc import rest_to_docopt
    from hwp5.proc import init_logger
    from docopt import docopt
    doc = rest_to_docopt(__doc__)
    args = docopt(doc, version=version)
    init_logger(args)

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
    from hwp5.tools import xslt
    import pkg_resources
    content_xsl = pkg_resources.resource_filename('hwp5', 'xsl/plaintext.xsl')
    return xslt(content_xsl)
