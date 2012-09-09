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
'''HWPv5 to HTML converter

Usage::

    hwp5html [options] <hwp5file> [<out-directory>]
    hwp5html -h | --help
    hwp5html --version

Options::

    -h --help           Show this screen
    --version           Show version
    --loglevel=<level>  Set log level.
    --logfile=<file>    Set log file.
'''

import os, os.path
import logging


logger = logging.getLogger(__name__)


def main():
    import sys
    from hwp5 import __version__ as version
    from hwp5.proc import rest_to_docopt
    from hwp5.proc import init_logger
    from hwp5.errors import InvalidHwp5FileError
    from docopt import docopt
    doc = rest_to_docopt(__doc__)
    args = docopt(doc, version=version)
    init_logger(args)

    filename = args['<hwp5file>']
    from hwp5.dataio import ParseError
    from hwp5.xmlmodel import Hwp5File
    try:
        hwp5file = Hwp5File(filename)
    except ParseError, e:
        e.print_to_logger(logger)
        sys.exit(1)
    except InvalidHwp5FileError, e:
        logger.error('%s', e)
        sys.exit(1)
    else:
        outdir = args['<out-directory>']
        if outdir is None:
            outdir, ext = os.path.splitext(os.path.basename(filename))
        generate_htmldir(hwp5file, outdir)


def generate_htmldir(hwp5file, base_dir):
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    generate_htmldir_files(hwp5file, base_dir)


def generate_htmldir_files(hwp5file, base_dir):
    from tempfile import TemporaryFile

    hwp5_xml = TemporaryFile()
    try:
        hwp5file.xmlevents(embedbin=False).dump(hwp5_xml)

        hwp5_xml.seek(0)
        html_path = os.path.join(base_dir, 'index.html')
        generate_html_file(hwp5_xml, html_path)

        hwp5_xml.seek(0)
        css_path = os.path.join(base_dir, 'styles.css')
        generate_css_file(hwp5_xml, css_path)
    finally:
        hwp5_xml.close()

    bindata_dir = os.path.join(base_dir, 'bindata')
    extract_bindata_dir(hwp5file, bindata_dir)


def generate_css_file(hwp5_xml, css_path):
    from hwp5.hwp5odt import hwp5_resources_filename
    from hwp5.tools import xslt

    css_xsl = hwp5_resources_filename('xsl/hwp5css.xsl')

    css_file = file(css_path, 'w')
    try:
        transform = xslt(css_xsl)
        transform(hwp5_xml, css_file)
    finally:
        css_file.close()


def generate_html_file(hwp5_xml, html_path):
    from hwp5.hwp5odt import hwp5_resources_filename
    from hwp5.tools import xslt

    html_xsl = hwp5_resources_filename('xsl/hwp5html.xsl')

    html_file = file(html_path, 'w')
    try:
        transform = xslt(html_xsl)
        transform(hwp5_xml, html_file)
    finally:
        html_file.close()


def extract_bindata_dir(hwp5file, bindata_dir):
    bindata_stg = hwp5file['BinData']
    if not os.path.exists(bindata_dir):
        os.mkdir(bindata_dir)

    from hwp5.storage import unpack
    unpack(bindata_stg, bindata_dir)
