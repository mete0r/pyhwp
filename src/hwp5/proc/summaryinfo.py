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
import sys

from zope.interface.registry import Components

from ..filestructure import Hwp5File
from ..filestructure import Hwp5FileOpener
from ..cli import init_olestorage_opener
from ..interfaces import IStorageOpener
from ..summaryinfo import HwpSummaryInfoTextFormatter


PY2 = sys.version_info.major == 2


def main(args):
    registry = Components()
    settings = {}
    init_olestorage_opener(registry, **settings)

    olestorage_opener = registry.getUtility(IStorageOpener)
    hwp5file_opener = Hwp5FileOpener(olestorage_opener, Hwp5File)

    if PY2:
        output_fp = sys.stdout
    else:
        output_fp = sys.stdout.buffer

    formatter = HwpSummaryInfoTextFormatter()
    with closing(hwp5file_opener.open_hwp5file(args.hwp5file)) as hwpfile:
        for textline in formatter.formatTextLines(hwpfile.summaryinfo):
            line = textline.encode('utf-8')
            output_fp.write(line)
            output_fp.write(b'\n')


def summaryinfo_argparser(subparsers, _):
    parser = subparsers.add_parser(
        'summaryinfo',
        help=_(
            'Print summary informations of .hwp files.'
        ),
        description=_(
            'Print the summary information of <hwp5file>.'
        ),
    )
    parser.add_argument(
        'hwp5file',
        metavar='<hwp5file>',
        help=_('.hwp file to analyze'),
    )
    parser.set_defaults(func=main)
    return parser
