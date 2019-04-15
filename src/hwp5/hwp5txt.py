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
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from argparse import ArgumentParser
from contextlib import closing
import gettext
import logging
import os.path
import sys

from zope.interface.registry import Components

from . import __version__ as version
from .cli import init_logger
from .cli import init_olestorage_opener
from .cli import init_xslt
from .cli import update_settings_from_environ
from .dataio import ParseError
from .errors import InvalidHwp5FileError
from .filestructure import Hwp5FileOpener
from .interfaces import IStorageOpener
from .interfaces import IXSLTFactory
from .utils import make_open_dest_file
from .utils import cached_property
from .transforms import BaseTransform
from .xmlmodel import Hwp5File


PY3 = sys.version_info.major == 3
logger = logging.getLogger(__name__)
locale_dir = os.path.join(os.path.dirname(__file__), 'locale')
locale_dir = os.path.abspath(locale_dir)
t = gettext.translation('hwp5txt', locale_dir, fallback=True)
if PY3:
    _ = t.gettext
else:
    _ = t.ugettext


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
    argparser = main_argparser()
    args = argparser.parse_args()
    init_logger(args)

    settings = {}
    registry = Components()
    update_settings_from_environ(settings)
    init_olestorage_opener(registry, **settings)
    init_xslt(registry, **settings)

    olestorage_opener = registry.getUtility(IStorageOpener)
    hwp5file_opener = Hwp5FileOpener(olestorage_opener, Hwp5File)

    hwp5path = args.hwp5file

    xsltfactory = registry.getUtility(IXSLTFactory)
    text_transform = TextTransform(xsltfactory)

    open_dest = make_open_dest_file(args.output)
    transform = text_transform.transform_hwp5_to_text

    try:
        with closing(hwp5file_opener.open_hwp5file(hwp5path)) as hwp5file:
            with open_dest() as dest:
                transform(hwp5file, dest)
    except ParseError as e:
        e.print_to_logger(logger)
    except InvalidHwp5FileError as e:
        logger.error('%s', e)
        sys.exit(1)


def main_argparser():
    parser = ArgumentParser(
        prog='hwp5txt',
        description=_('HWPv5 to txt converter'),
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(version)
    )
    parser.add_argument(
        '--loglevel',
        help=_('Set log level.'),
    )
    parser.add_argument(
        '--logfile',
        help=_('Set log file.'),
    )
    parser.add_argument(
        '--output',
        help=_('Output file'),
    )
    parser.add_argument(
        'hwp5file',
        metavar='<hwp5file>',
        help=_('.hwp file to convert'),
    )
    return parser
