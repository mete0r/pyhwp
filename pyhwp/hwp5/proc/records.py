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
''' Print the record structure.

Usage::

    hwp5proc records [--simple | --json | --raw | --raw-header | --raw-payload]
                     [--treegroup=<treegroup> | --range=<range>]
                     [--loglevel=<loglevel>] [--logfile=<logfile>]
                     <hwp5file> <record-stream>
    hwp5proc records [--simple | --json | --raw | --raw-header | --raw-payload]
                     [--treegroup=<treegroup> | --range=<range>]
                     [--loglevel=<loglevel>] [--logfile=<logfile>]
    hwp5proc records --help

Options::

    -h --help               Show this screen
       --loglevel=<level>   Set log level.
       --logfile=<file>     Set log file.

       --simple             Print records as simple tree
       --json               Print records as json
       --raw                Print records as is
       --raw-header         Print record headers as is
       --raw-payload        Print record payloads as is

       --range=<range>      Print records specified in the <range>.
       --treegroup=<treegroup>
                            Print records specified in the <treegroup>.

    <hwp5file>              HWPv5 files (*.hwp)
    <record-stream>         Record-structured internal streams.
                            (e.g. DocInfo, BodyText/*)
    <range>                 Specifies the range of the records.
                             N-M means "from the record N to M-1 (excluding M)"
                             N means just the record N
    <treegroup>             Specifies the N-th subtree of the record structure.

Example::

    $ hwp5proc records samples/sample-5017.hwp DocInfo

Example::

    $ hwp5proc records samples/sample-5017.hwp DocInfo --range=0-2

If neither <hwp5file> nor <record-stream> is specified, the record stream is
read from the standard input with an assumption that the input is in the format
version specified by -V option.

Example::

    $ hwp5proc records --raw samples/sample-5017.hwp DocInfo --range=0-2 \
> tmp.rec
    $ hwp5proc records < tmp.rec

'''
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import sys

from ..recordstream import Hwp5File
from ..recordstream import RecordStream
from ..recordstream import encode_record_header
from ..recordstream import dump_record
from ..storage import Open2Stream
from . import parse_recordstream_name


PY2 = sys.version_info.major == 2


def main(args):
    if PY2:
        stdout_text = sys.stdout
        stdout_binary = sys.stdout
    else:
        stdout_text = sys.stdout
        stdout_binary = sys.stdout.buffer

    filename = args['<hwp5file>']
    if filename:
        hwpfile = Hwp5File(filename)
        streamname = args['<record-stream>']
        stream = parse_recordstream_name(hwpfile, streamname)
    else:
        stream = RecordStream(Open2Stream(lambda: sys.stdin), None)

    opts = dict()
    rng = args['--range']
    if rng:
        rng = rng.split('-', 1)
        rng = tuple(int(x) for x in rng)
        if len(rng) == 1:
            rng = (rng[0], rng[0] + 1)
        opts['range'] = rng
    treegroup = args['--treegroup']
    if treegroup is not None:
        opts['treegroup'] = int(treegroup)

    if args['--simple']:
        for record in stream.records(**opts):
            stdout_text.write('{:04d} {} {}\n'.format(
                record['seqno'],
                '  ' * record['level'],
                record['tagname'],
            ))
    elif args['--raw']:
        for record in stream.records(**opts):
            dump_record(stdout_binary, record)
    elif args['--raw-header']:
        for record in stream.records(**opts):
            hdr = encode_record_header(record)
            stdout_binary.write(hdr)
    elif args['--raw-payload']:
        for record in stream.records(**opts):
            stdout_binary.write(record['payload'])
    else:
        stream.records_json(**opts).dump(stdout_text)
