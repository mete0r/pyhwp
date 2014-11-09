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

    --output=<file>     Output file
'''
from __future__ import with_statement
from contextlib import closing
import logging
import sys

from .transforms import BaseTransform
from .utils import cached_property


logger = logging.getLogger(__name__)


RESOURCE_PATH_XSL_TEXT = 'xsl/plaintext.xsl'


class TextTransform(BaseTransform):

    @property
    def transform_hwp5_to_text(self):
        transform_xhwp5 = self.transform_xhwp5_to_text
        return self.make_transform_hwp5(transform_xhwp5)

    @cached_property
    def transform_xhwp5_to_text(self):
        '''
        >>> T.transform_xhwp5_to_css('hwp5.xml', 'styles.css')
        '''
        resource_path = RESOURCE_PATH_XSL_TEXT
        return self.make_xsl_transform(resource_path)


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

    text_transform = TextTransform()

    open_dest = make_open_dest_file(args['--output'])
    transform = text_transform.transform_hwp5_to_text

    try:
        with closing(Hwp5File(hwp5path)) as hwp5file:
            with open_dest() as dest:
                transform(hwp5file, dest)
    except ParseError, e:
        e.print_to_logger(logger)
    except InvalidHwp5FileError, e:
        logger.error('%s', e)
        sys.exit(1)
