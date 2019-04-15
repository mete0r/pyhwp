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
import sys

from zope.interface.registry import Components

from ..cli import init_olestorage_opener
from ..cli import open_hwpfile
from ..storage import open_storage_item


PY2 = sys.version_info.major == 2


def main(args):
    registry = Components()
    settings = {}
    init_olestorage_opener(registry, **settings)

    if PY2:
        output_fp = sys.stdout
    else:
        output_fp = sys.stdout.buffer

    hwp5file = open_hwpfile(registry, args)
    stream = open_storage_item(hwp5file, args.stream)
    f = stream.open()
    try:
        while True:
            data = f.read(4096)
            if data:
                output_fp.write(data)
            else:
                return
    finally:
        if hasattr(f, 'close'):
            f.close()


def cat_argparser(subparsers, _):
    parser = subparsers.add_parser(
        'cat',
        help=_(
            'Extract out internal streams of .hwp files'
        ),
        description=_(
            'Extract out the specified stream in the <hwp5file> '
            'to the standard output.'
        )
    )
    parser.add_argument(
        'hwp5file',
        metavar='<hwp5file>',
        help=_('.hwp file to analyze'),
    )
    parser.add_argument(
        'stream',
        metavar='<stream>',
        help=_('Internal path of a stream to extract'),
    )
    mutex_group = parser.add_mutually_exclusive_group()
    mutex_group.add_argument(
        '--vstreams',
        action='store_true',
        help=_(
            'Process with virtual streams (i.e. parsed/converted form of '
            'real streams)'
        )
    )
    mutex_group.add_argument(
        '--ole',
        action='store_true',
        help=_(
            'Treat <hwp5file> as an OLE Compound File. As a result, '
            'some streams will be presented as-is. (i.e. not decompressed)'
        )
    )
    parser.set_defaults(func=main)
    return parser
