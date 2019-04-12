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
from itertools import islice
import sys

from ..binmodel import Hwp5File
from ..binmodel import ModelStream
from ..binmodel import RecordModel
from ..binmodel import model_to_json
from ..cli import parse_recordstream_name
from ..dataio import hexdump
from ..storage import Open2Stream
from ..treeop import ENDEVENT
from ..utils import generate_json_array
from ..utils import unicode_unescape


PY2 = sys.version_info.major == 2


def main(args):
    stream = stream_from_args(args)
    if args.events:
        for event, item in stream.parse_model_events():
            type = item['type'].__name__
            if event is not None:
                if item['type'] is RecordModel:
                    record = item['record']
                    fmt = '     %s Record %s level=%s %s'
                    print(fmt % (event.__name__,
                                 record['seqno'],
                                 record['level'],
                                 record['tagname']))
                    if event is ENDEVENT:
                        leftover = item['leftover']
                        print('%04x' % leftover['offset'])
                        if len(leftover['bytes']):
                            print('')
                            print('leftover:')
                            print(hexdump(leftover['bytes']))
                        print('-' * 20)
                else:
                    print('    ', event.__name__, type, item.get('name', ''))
            else:
                offset = item['bin_offset']
                name = item.get('name', '-')
                value = item.get('value', '-')
                print('%04x' % offset, type, name, repr(value))
        return

    models_from_stream = models_from_args(args)
    models = models_from_stream(stream)

    print_models = print_models_from_args(args)
    print_models(models)


def models_argparser(subparsers, _):
    parser = subparsers.add_parser(
        'models',
        help=_(
            'Print parsed binary models of .hwp file record streams.'
        ),
        description=_(
            'Print parsed binary models in the specified <record-stream>.'
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
    parser.add_argument(
        '--file-format-version',
        '-V',
        metavar='<version>',
        help=_(
            'Specifies HWPv5 file format version of the standard input stream'
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
        '--format',
        metavar='<format>',
        help=_(
            'Print records formatted'
        )
    )
    output_formats.add_argument(
        '--events',
        action='store_true',
        help=_(
            'Print records as events'
        )
    )
    subset = parser.add_mutually_exclusive_group()
    subset.add_argument(
        '--treegroup',
        metavar='<treegroup>',
        help=_(
            'Specifies the N-th subtree of the record structure.'
        )
    )
    subset.add_argument(
        '--seqno',
        metavar='<treegroup>',
        help=_(
            'Print a model of <seqno>-th record'
        )
    )
    parser.set_defaults(func=main)
    return parser


def stream_from_args(args):
    filename = args.hwp5file
    if filename:
        # TODO: args.record_stream is None
        streamname = args.record_stream
        hwpfile = Hwp5File(filename)
        return parse_recordstream_name(hwpfile, streamname)
    else:
        version = args.file_format_version or '5.0.0.0'
        version = version.split('.')
        version = tuple(int(x) for x in version)

        if PY2:
            stdin_binary = sys.stdin
        else:
            stdin_binary = sys.stdin.buffer

        return ModelStream(Open2Stream(lambda: stdin_binary), version)


def models_from_args(args):

    if args.treegroup:
        treegroup = int(args.treegroup)
        return lambda stream: stream.models(treegroup=treegroup)

    if args.seqno:
        seqno = int(args.seqno)
        return lambda stream: islice(stream.models(),
                                     seqno, seqno + 1)

    return lambda stream: stream.models()


def print_models_from_args(args):

    if args.simple:
        return print_models_with_print_model(print_model_simple)

    if args.format:
        fmt = args.format
        fmt = unicode_unescape(fmt)
        print_model = print_model_with_format(fmt)
        return print_models_with_print_model(print_model)

    return print_models_json


def print_models_json(models):
    jsonobjects = (model_to_json(model, sort_keys=True, indent=2)
                   for model in models)
    for s in generate_json_array(jsonobjects):
        sys.stdout.write(s)


def print_models_with_print_model(print_model):
    def models_printer(models):
        for model in models:
            print_model(model)
    return models_printer


def print_model_simple(model):
    sys.stdout.write('%04d ' % model['seqno'])
    sys.stdout.write(' ' * model['level'] + model['type'].__name__)
    sys.stdout.write('\n')


def print_model_with_format(fmt):
    def print_model(model):
        model = transform_model_formattable(model)
        sys.stdout.write(fmt % model)
    return print_model


def transform_model_formattable(model):
    return dict(model, type=model['type'].__name__)
