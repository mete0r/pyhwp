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
import os.path


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
    from hwp5.plat import get_xslt
    from hwp5.importhelper import pkg_resources_filename
    from tempfile import mkstemp
    from hwp5.xmlmodel import Hwp5File

    hwp5_filename = args['<hwp5file>']
    rootname = os.path.basename(hwp5_filename)
    if rootname.lower().endswith('.hwp'):
        rootname = rootname[0:-4]
    txt_path = rootname + '.txt'

    xslt = get_xslt()
    plaintext_xsl = pkg_resources_filename('hwp5', 'xsl/plaintext.xsl')

    hwp5file = Hwp5File(hwp5_filename)
    try:
        xhwp5_fd, xhwp5_path = mkstemp()
        try:
            xhwp5_file = os.fdopen(xhwp5_fd, 'w')
            try:
                hwp5file.xmlevents().dump(xhwp5_file)
            finally:
                xhwp5_file.close()

            xslt(plaintext_xsl, xhwp5_path, txt_path)
        finally:
            os.unlink(xhwp5_path)
    finally:
        hwp5file.close()
