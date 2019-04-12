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
import shutil
import sys


PY2 = sys.version_info.major == 2


def main(args):
    if PY2:
        output_fp = sys.stdout
    else:
        output_fp = sys.stdout.buffer

    from hwp5.filestructure import Hwp5File
    hwp5file = Hwp5File(args.hwp5file)
    f = hwp5file.header.open_text()
    try:
        shutil.copyfileobj(f, output_fp)
    finally:
        hwp5file.close()


def header_argparser(subparsers, _):
    parser = subparsers.add_parser(
        'header',
        help=_('Print file headers of .hwp files.'),
        description=_('Print the file header of <hwp5file>.'),
    )
    parser.add_argument(
        'hwp5file',
        metavar='<hwp5file>',
        help=_('.hwp file to analyze'),
    )
    parser.set_defaults(func=main)
    return parser
