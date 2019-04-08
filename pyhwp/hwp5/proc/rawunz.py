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
import shutil

from ..zlib_raw_codec import StreamReader


PY2 = sys.version_info.major == 2


def main(args):
    if PY2:
        input_fp = sys.stdin
        output_fp = sys.stdout
    else:
        input_fp = sys.stdin.buffer
        output_fp = sys.stdout.buffer

    stream = StreamReader(input_fp)
    shutil.copyfileobj(stream, output_fp)


def rawunz_argparser(subparsers, _):
    parser = subparsers.add_parser(
        'rawunz',
        help=_(
            'Deflate an headerless zlib-compressed stream'
        ),
        description=_(
            'Deflate an headerless zlib-compressed stream'
        ),
    )
    parser.set_defaults(func=main)
    return parser
