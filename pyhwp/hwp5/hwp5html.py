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
from __future__ import with_statement
from contextlib import contextmanager
import os.path
import logging
import shutil

from hwp5.importhelper import pkg_resources_filename
from hwp5.hwp5odt import mkstemp_open

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
    import os
    from tempfile import mkstemp
    from hwp5.plat import get_xslt

    xslt = get_xslt()
    fd, path = mkstemp()
    try:
        xhwp5 = os.fdopen(fd, 'w')
        try:
            hwp5file.xmlevents(embedbin=False).dump(xhwp5)
        finally:
            xhwp5.close()

        html_path = os.path.join(base_dir, 'index.xhtml')
        generate_html_file(xslt, path, html_path)

        css_path = os.path.join(base_dir, 'styles.css')
        generate_css_file(xslt, path, css_path)
    finally:
        os.unlink(path)

    bindata_dir = os.path.join(base_dir, 'bindata')
    extract_bindata_dir(hwp5file, bindata_dir)


def generate_css_file(xslt, xhwp5_path, css_path):
    with hwp5_resources_path('xsl/hwp5css.xsl') as css_xsl:
        xslt(css_xsl, xhwp5_path, css_path)


def generate_html_file(xslt, xhwp5_path, html_path):
    with hwp5_resources_path('xsl/hwp5html.xsl') as html_xsl:
        xslt(html_xsl, xhwp5_path, html_path)


def extract_bindata_dir(hwp5file, bindata_dir):
    if 'BinData' not in hwp5file:
        return
    bindata_stg = hwp5file['BinData']
    if not os.path.exists(bindata_dir):
        os.mkdir(bindata_dir)

    from hwp5.storage import unpack
    unpack(bindata_stg, bindata_dir)


@contextmanager
def hwp5_resources_path(res_path):
    try:
        path = pkg_resources_filename('hwp5', res_path)
    except Exception:
        logger.info('%s: pkg_resources_filename failed; using resource_stream',
                    res_path)
        with mkstemp_open() as (path, g):
            import pkg_resources
            f = pkg_resources.resource_stream('hwp5', res_path)
            try:
                shutil.copyfileobj(f, g)
                g.close()
                yield path
            finally:
                f.close()
    else:
        yield path
