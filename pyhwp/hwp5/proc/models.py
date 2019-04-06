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
''' Print parsed binary models in the specified <record-stream>.

Usage::

    hwp5proc models [--simple | --json | --format=<format> | --events]
                    [--treegroup=<treegroup> | --seqno=<seqno>]
                    [--loglevel=<loglevel>] [--logfile=<logfile>]
                    (<hwp5file> <record-stream> | -V <version>)
    hwp5proc models --help

Options::

    -h --help               Show this screen
       --loglevel=<level>   Set log level.
       --logfile=<file>     Set log file.

       --simple             Print records as simple tree
       --json               Print records as json
       --format=<format>    Print records as formatted

       --treegroup=<treegroup>
                            Print records in the <treegroup>.
                            <treegroup> specifies the N-th subtree of the
                            record structure.
       --seqno=<seqno>      Print a model of <seqno>-th record

    -V <version>, --file-format-version=<version>
                            Specifies HWPv5 file format version

    <hwp5file>              HWPv5 files (*.hwp)
    <record-stream>         Record-structured internal streams.
                            (e.g. DocInfo, BodyText/*)

Example::

    $ hwp5proc models samples/sample-5017.hwp DocInfo
    $ hwp5proc models samples/sample-5017.hwp BodyText/Section0

    $ hwp5proc models samples/sample-5017.hwp docinfo
    $ hwp5proc models samples/sample-5017.hwp bodytext/0

Example::

    $ hwp5proc models --simple samples/sample-5017.hwp bodytext/0
    $ hwp5proc models --format='%(level)s %(tagname)s\\n' \\
            samples/sample-5017.hwp bodytext/0

Example::

    $ hwp5proc models --simple --treegroup=1 samples/sample-5017.hwp bodytext/0
    $ hwp5proc models --simple --seqno=4 samples/sample-5017.hwp bodytext/0

If neither <hwp5file> nor <record-stream> is specified, the record stream is
read from the standard input with an assumption that the input is in the format
version specified by -V option.

Example::

    $ hwp5proc cat samples/sample-5017.hwp BodyText/Section0 > Section0.bin
    $ hwp5proc models -V 5.0.1.7 < Section0.bin

'''
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from itertools import islice
import sys

from ..binmodel import Hwp5File
from ..binmodel import ModelStream
from ..binmodel import RecordModel
from ..binmodel import model_to_json
from ..dataio import hexdump
from ..storage import Open2Stream
from ..treeop import ENDEVENT
from ..utils import generate_json_array
from ..utils import unicode_unescape
from . import parse_recordstream_name


PY2 = sys.version_info.major == 2


def main(args):
    stream = stream_from_args(args)
    if args['--events']:
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


def stream_from_args(args):
    filename = args['<hwp5file>']
    if filename:
        streamname = args['<record-stream>']
        hwpfile = Hwp5File(filename)
        return parse_recordstream_name(hwpfile, streamname)
    else:
        version = args['--file-format-version'] or '5.0.0.0'
        version = version.split('.')
        version = tuple(int(x) for x in version)

        if PY2:
            stdin_binary = sys.stdin
        else:
            stdin_binary = sys.stdin.buffer

        return ModelStream(Open2Stream(lambda: stdin_binary), version)


def models_from_args(args):

    if args['--treegroup']:
        treegroup = int(args['--treegroup'])
        return lambda stream: stream.models(treegroup=treegroup)

    if args['--seqno']:
        seqno = int(args['--seqno'])
        return lambda stream: islice(stream.models(),
                                     seqno, seqno + 1)

    return lambda stream: stream.models()


def print_models_from_args(args):

    if args['--simple']:
        return print_models_with_print_model(print_model_simple)

    if args['--format']:
        fmt = args['--format']
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
