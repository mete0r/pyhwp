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
import os.path

from .. import storage
from ..cli import open_hwpfile


def main(args):
    filename = args.hwp5file
    hwp5file = open_hwpfile(args)

    outdir = args.out_directory
    if outdir is None:
        outdir, ext = os.path.splitext(os.path.basename(filename))
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    storage.unpack(hwp5file, outdir)


def unpack_argparser(subparsers, _):
    parser = subparsers.add_parser(
        'unpack',
        help=_(
            'Extract out internal streams of .hwp files into a directory.'
        ),
        description=_(
            'Extract out streams in the specified <hwp5file> '
            'to a directory.'
        )
    )
    parser.add_argument(
        'hwp5file',
        metavar='<hwp5file>',
        help=_('.hwp file to analyze'),
    )
    parser.add_argument(
        'out_directory',
        nargs='?',
        metavar='<out-directory>',
        help=_('Output directory'),
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
