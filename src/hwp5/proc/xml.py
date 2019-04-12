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
from functools import partial
import logging

from ..utils import make_open_dest_file
from ..utils import wrap_open_dest_for_tty
from ..utils import wrap_open_dest
from ..utils import pager
from ..utils import syntaxhighlight
from ..utils import xmllint
from ..xmldump_flat import xmldump_flat
from ..xmlmodel import Hwp5File


logger = logging.getLogger(__name__)


def xmldump_nested(hwp5file, output, embedbin=False, xml_declaration=True):
    dump = hwp5file.xmlevents(embedbin=embedbin).dump
    dump = partial(dump, xml_declaration=xml_declaration)
    dump(output)


def main(args):
    ''' Transform <hwp5file> into an XML.
    '''

    fmt = args.format or 'nested'
    if fmt == 'flat':
        xmldump = partial(
            xmldump_flat,
            xml_declaration=not args.no_xml_decl
        )
    elif fmt == 'nested':
        xmldump = partial(
            xmldump_nested,
            xml_declaration=not args.no_xml_decl,
            embedbin=args.embedbin,
        )

    open_dest = make_open_dest_file(args.output)
    open_dest = wrap_open_dest_for_tty(open_dest, [
        pager(),
        syntaxhighlight('application/xml'),
    ] + ([
        xmllint(format=True),
    ] if not args.no_validate_wellformed else []))
    open_dest = wrap_open_dest(open_dest, [
        xmllint(encode='utf-8'),
        xmllint(c14n=True),
    ] if not args.no_validate_wellformed else [])

    hwp5file = Hwp5File(args.hwp5file)
    with open_dest() as output:
        xmldump(hwp5file, output)


def xml_argparser(subparsers, _):
    parser = subparsers.add_parser(
        'xml',
        help=_(
           'Transform .hwp files into an XML.'
        ),
        description=_(
           'Transform <hwp5file> into an XML.'
        ),
    )
    parser.add_argument(
        'hwp5file',
        metavar='<hwp5file>',
        help=_('.hwp file to analyze'),
    )
    parser.add_argument(
        '--embedbin',
        action='store_true',
        help=_('Embed BinData/* streams in the output XML.'),
    )
    parser.add_argument(
        '--no-xml-decl',
        action='store_true',
        help=_('Do not output <?xml ... ?> XML declaration.'),
    )
    parser.add_argument(
       '--output',
       metavar='<file>',
       help=_('Output filename.'),
    )
    parser.add_argument(
       '--format',
       metavar='<format>',
       help=_('"flat", "nested" (default: "nested")'),
    )
    parser.add_argument(
       '--no-validate-wellformed',
       action='store_true',
       help=_('Do not validate well-formedness of output.'),
    )
    parser.set_defaults(func=main)
    return parser
