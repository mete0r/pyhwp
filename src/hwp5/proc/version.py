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
from contextlib import closing

from zope.interface.registry import Components

from ..cli import init_olestorage_opener
from ..filestructure import Hwp5File
from ..filestructure import Hwp5FileOpener
from ..interfaces import IStorageOpener


def main(args):
    registry = Components()
    settings = {}
    init_olestorage_opener(registry, **settings)

    olestorage_opener = registry.getUtility(IStorageOpener)

    hwp5file_opener = Hwp5FileOpener(olestorage_opener, Hwp5File)
    with closing(hwp5file_opener.open_hwp5file(args.hwp5file)) as hwp5file:
        h = hwp5file.fileheader
        print('%d.%d.%d.%d' % h.version)


def version_argparser(subparsers, _):
    parser = subparsers.add_parser(
        'version',
        help=_(
            'Print the file format version of .hwp files.'
        ),
        description=_(
            'Print the file format version of <hwp5file>.'
        ),
    )
    parser.add_argument(
        'hwp5file',
        metavar='<hwp5file>',
        help=_('.hwp file to analyze'),
    )
    parser.set_defaults(func=main)
    return parser
