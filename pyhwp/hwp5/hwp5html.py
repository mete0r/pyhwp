# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2015 mete0r <mete0r@sarangbang.or.kr>
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

    hwp5html [options] <hwp5file>
    hwp5html [options] <hwp5file> --html
    hwp5html [options] <hwp5file> --css
    hwp5html -h | --help
    hwp5html --version

Options::

    -h --help           Show this screen
    --version           Show version
    --loglevel=<level>  Set log level.
    --logfile=<file>    Set log file.

    --output=<output>   Output file / directory
'''
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from contextlib import contextmanager
from contextlib import closing
from functools import partial
import gettext
import io
import logging
import os.path
import shutil
import sys

from .transforms import BaseTransform
from .utils import cached_property


PY3 = sys.version_info.major == 3
logger = logging.getLogger(__name__)
locale_dir = os.path.join(os.path.dirname(__file__), 'locale')
locale_dir = os.path.abspath(locale_dir)
t = gettext.translation('hwp5html', locale_dir, fallback=True)
if PY3:
    _ = t.gettext
else:
    _ = t.ugettext


RESOURCE_PATH_XSL_CSS = 'xsl/hwp5css.xsl'
RESOURCE_PATH_XSL_XHTML = 'xsl/hwp5html.xsl'


class HTMLTransform(BaseTransform):

    @property
    def transform_hwp5_to_css(self):
        '''
        >>> T.transform_hwp5_to_css(hwp5file, 'styles.css')
        '''
        transform_xhwp5 = self.transform_xhwp5_to_css
        return self.make_transform_hwp5(transform_xhwp5)

    @property
    def transform_hwp5_to_xhtml(self):
        '''
        >>> T.transform_hwp5_to_xhtml(hwp5file, 'index.xhtml')
        '''
        transform_xhwp5 = self.transform_xhwp5_to_xhtml
        return self.make_transform_hwp5(transform_xhwp5)

    def transform_hwp5_to_dir(self, hwp5file, outdir):
        '''
        >>> T.transform_hwp5_to_dir(hwp5file, 'output')
        '''
        with self.transformed_xhwp5_at_temp(hwp5file) as xhwp5path:
            self.transform_xhwp5_to_dir(xhwp5path, outdir)

        bindata_dir = os.path.join(outdir, 'bindata')
        self.extract_bindata_dir(hwp5file, bindata_dir)

    @cached_property
    def transform_xhwp5_to_css(self):
        '''
        >>> T.transform_xhwp5_to_css('hwp5.xml', 'styles.css')
        '''
        resource_path = RESOURCE_PATH_XSL_CSS
        return self.make_xsl_transform(resource_path)

    @cached_property
    def transform_xhwp5_to_xhtml(self):
        '''
        >>> T.transform_xhwp5_to_xhtml('hwp5.xml', 'index.xhtml')
        '''
        resource_path = RESOURCE_PATH_XSL_XHTML
        return self.make_xsl_transform(resource_path)

    def transform_xhwp5_to_dir(self, xhwp5path, outdir):
        '''
        >>> T.transform_xhwp5_to_dir('hwp5.xml', 'output')
        '''
        html_path = os.path.join(outdir, 'index.xhtml')
        with io.open(html_path, 'wb') as f:
            self.transform_xhwp5_to_xhtml(xhwp5path, f)

        css_path = os.path.join(outdir, 'styles.css')
        with io.open(css_path, 'wb') as f:
            self.transform_xhwp5_to_css(xhwp5path, f)

    def extract_bindata_dir(self, hwp5file, bindata_dir):
        if 'BinData' not in hwp5file:
            return
        bindata_stg = hwp5file['BinData']
        if not os.path.exists(bindata_dir):
            os.mkdir(bindata_dir)

        from hwp5.storage import unpack
        unpack(bindata_stg, bindata_dir)


def main():
    from docopt import docopt

    from . import __version__ as version
    from .dataio import ParseError
    from .errors import InvalidHwp5FileError
    from .proc import rest_to_docopt
    from .proc import init_logger
    from .utils import make_open_dest_file
    from .xmlmodel import Hwp5File

    doc = rest_to_docopt(__doc__)
    args = docopt(doc, version=version)
    init_logger(args)

    hwp5path = args['<hwp5file>']

    html_transform = HTMLTransform()

    open_dest = make_open_dest_file(args['--output'])
    if args['--css']:
        transform = html_transform.transform_hwp5_to_css
        open_dest = wrap_for_css(open_dest)
    elif args['--html']:
        transform = html_transform.transform_hwp5_to_xhtml
        open_dest = wrap_for_xml(open_dest)
    else:
        transform = html_transform.transform_hwp5_to_dir
        dest_path = args['--output']
        if not dest_path:
            dest_path = os.path.splitext(os.path.basename(hwp5path))[0]
        open_dest = partial(open_dir, dest_path)

    try:
        with closing(Hwp5File(hwp5path)) as hwp5file:
            with open_dest() as dest:
                transform(hwp5file, dest)
    except ParseError as e:
        e.print_to_logger(logger)
    except InvalidHwp5FileError as e:
        logger.error('%s', e)
        sys.exit(1)


@contextmanager
def open_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
    yield path


def wrap_for_css(open_dest):
    from .utils import wrap_open_dest_for_tty
    from .utils import pager
    from .utils import syntaxhighlight
    return wrap_open_dest_for_tty(open_dest, [
        pager(),
        syntaxhighlight('text/css'),
    ])


def wrap_for_xml(open_dest):
    from .utils import wrap_open_dest_for_tty
    from .utils import pager
    from .utils import syntaxhighlight
    from .utils import xmllint
    return wrap_open_dest_for_tty(open_dest, [
        pager(),
        syntaxhighlight('application/xml'),
        xmllint(format=True, nonet=True),
    ])
