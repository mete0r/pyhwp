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

from ..cli import parse_recordstream_name
from ..recordstream import Hwp5File
from ..recordstream import RecordStream
from ..recordstream import encode_record_header
from ..recordstream import dump_record
from ..storage import Open2Stream


PY2 = sys.version_info.major == 2


def main(args):
    if PY2:
        stdout_text = sys.stdout
        stdout_binary = sys.stdout
    else:
        stdout_text = sys.stdout
        stdout_binary = sys.stdout.buffer

    filename = args.hwp5file
    if filename:
        hwpfile = Hwp5File(filename)
        # TODO: args.record_stream is None
        streamname = args.record_stream
        stream = parse_recordstream_name(hwpfile, streamname)
    else:
        stream = RecordStream(Open2Stream(lambda: sys.stdin), None)

    opts = dict()
    rng = args.range
    if rng:
        rng = rng.split('-', 1)
        rng = tuple(int(x) for x in rng)
        if len(rng) == 1:
            rng = (rng[0], rng[0] + 1)
        opts['range'] = rng
    treegroup = args.treegroup
    if treegroup is not None:
        opts['treegroup'] = int(treegroup)

    if args.simple:
        for record in stream.records(**opts):
            stdout_text.write('{:04d} {} {}\n'.format(
                record['seqno'],
                '  ' * record['level'],
                record['tagname'],
            ))
    elif args.raw:
        for record in stream.records(**opts):
            dump_record(stdout_binary, record)
    elif args.raw_header:
        for record in stream.records(**opts):
            hdr = encode_record_header(record)
            stdout_binary.write(hdr)
    elif args.raw_payload:
        for record in stream.records(**opts):
            stdout_binary.write(record['payload'])
    else:
        stream.records_json(**opts).dump(stdout_text)


def records_argparser(subparsers, _):
    parser = subparsers.add_parser(
        'records',
        help=_(
            'Print the record structure of .hwp file record streams.'
        ),
        description=_(
            'Print the record structure of the specified stream.'
        ),
    )
    parser.add_argument(
        'hwp5file',
        nargs='?',
        metavar='<hwp5file>',
        help=_('.hwp file to analyze'),
    )
    parser.add_argument(
        'record_stream',
        nargs='?',
        metavar='<record-stream>',
        help=_(
            'Record-structured internal streams.\n'
            '(e.g. DocInfo, BodyText/*)\n'
        ),
    )
    output_formats = parser.add_mutually_exclusive_group()
    output_formats.add_argument(
        '--simple',
        action='store_true',
        help=_(
            'Print records as simple tree'
        )
    )
    output_formats.add_argument(
        '--json',
        action='store_true',
        help=_(
            'Print records as json'
        )
    )
    output_formats.add_argument(
        '--raw',
        action='store_true',
        help=_(
            'Print records as is'
        )
    )
    output_formats.add_argument(
        '--raw-header',
        action='store_true',
        help=_(
            'Print record headers as is'
        )
    )
    output_formats.add_argument(
        '--raw-payload',
        action='store_true',
        help=_(
            'Print record payloads as is'
        )
    )
    subset = parser.add_mutually_exclusive_group()
    subset.add_argument(
        '--range',
        metavar='<range>',
        help=_(
            'Specifies the range of the records.\n'
            'N-M means "from the record N to M-1 (excluding M)"\n'
            'N means just the record N\n'
        )
    )
    subset.add_argument(
        '--treegroup',
        metavar='<treegroup>',
        help=_(
            'Specifies the N-th subtree of the record structure.'
        )
    )
    parser.set_defaults(func=main)
    return parser
