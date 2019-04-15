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
''' List streams in the <hwp5file>.

Usage::

    hwp5proc ls [--loglevel=<loglevel>] [--logfile=<logfile>]
                [--vstreams | --ole]
                <hwp5file>
    hwp5proc ls --help

Options::

    -h --help               Show this screen
       --loglevel=<level>   Set log level.
       --logfile=<file>     Set log file.

       --vstreams           Process with virtual streams (i.e. parsed/converted
                            form of real streams)
       --ole                Treat <hwpfile> as an OLE Compound File. As a
                            result, some streams will be presented as-is. (i.e.
                            not decompressed)

Example: List without virtual streams::

    $ hwp5proc ls sample/sample-5017.hwp

    \\x05HwpSummaryInformation
    BinData/BIN0002.jpg
    BinData/BIN0002.png
    BinData/BIN0003.png
    BodyText/Section0
    DocInfo
    DocOptions/_LinkDoc
    FileHeader
    PrvImage
    PrvText
    Scripts/DefaultJScript
    Scripts/JScriptVersion

Example: List virtual streams too::

    $ hwp5proc ls --vstreams sample/sample-5017.hwp

    \\x05HwpSummaryInformation
    \\x05HwpSummaryInformation.txt
    BinData/BIN0002.jpg
    BinData/BIN0002.png
    BinData/BIN0003.png
    BodyText/Section0
    BodyText/Section0.models
    BodyText/Section0.records
    BodyText/Section0.xml
    BodyText.xml
    DocInfo
    DocInfo.models
    DocInfo.records
    DocInfo.xml
    DocOptions/_LinkDoc
    FileHeader
    FileHeader.txt
    PrvImage
    PrvText
    PrvText.utf8
    Scripts/DefaultJScript
    Scripts/JScriptVersion

'''
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from zope.interface.registry import Components

from ..storage import printstorage
from ..cli import init_olestorage_opener
from ..cli import open_hwpfile


def main(args):
    registry = Components()
    settings = {}
    init_olestorage_opener(registry, **settings)
    hwpfile = open_hwpfile(registry, args)
    printstorage(hwpfile)


def ls_argparser(subparsers, _):
    parser = subparsers.add_parser(
        'ls',
        help=_('List streams in .hwp files.'),
        description=_('List streams in the <hwp5file>.'),
    )
    parser.add_argument(
        'hwp5file',
        metavar='<hwp5file>',
        help=_('.hwp file to analyze'),
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
