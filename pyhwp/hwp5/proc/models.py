# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2014 mete0r <mete0r@sarangbang.or.kr>
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

    hwp5proc models [--simple | --json]
                    [--treegroup=<treegroup>]
                    [--loglevel=<loglevel>] [--logfile=<logfile>]
                    <hwp5file> <record-stream>
    hwp5proc models [--simple | --json]
                    [--treegroup=<treegroup>]
                    [--loglevel=<loglevel>] [--logfile=<logfile>] -V <version>
    hwp5proc models --help

Options::

    -h --help               Show this screen
       --loglevel=<level>   Set log level.
       --logfile=<file>     Set log file.

       --simple             Print records as simple tree
       --json               Print records as json

       --treegroup=<treegroup>
                            Print records in the <treegroup>.
                            <treegroup> specifies the N-th subtree of the
                            record structure.

    -V <version>, --formatversion=<version>
                            Specifies HWPv5 format version

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

Example::

    $ hwp5proc models --simple --treegroup=1 samples/sample-5017.hwp bodytext/0

If neither <hwp5file> nor <record-stream> is specified, the record stream is
read from the standard input with an assumption that the input is in the format
version specified by -V option.

Example::

    $ hwp5proc cat samples/sample-5017.hwp BodyText/Section0 > Section0.bin
    $ hwp5proc models -V 5.0.1.7 < Section0.bin

'''
from hwp5.proc import entrypoint


@entrypoint(__doc__)
def main(args):
    import sys
    filename = args['<hwp5file>']
    if filename:
        from hwp5.binmodel import Hwp5File
        from hwp5.proc import parse_recordstream_name
        streamname = args['<record-stream>']
        hwpfile = Hwp5File(filename)
        stream = parse_recordstream_name(hwpfile, streamname)
    else:
        version = args['--formatversion'] or '5.0.0.0'
        version = version.split('.')
        version = tuple(int(x) for x in version)

        from hwp5.storage import Open2Stream
        from hwp5.binmodel import ModelStream
        stream = ModelStream(Open2Stream(lambda: sys.stdin), version)

    opts = dict()

    treegroup = args['--treegroup']
    if treegroup is not None:
        opts['treegroup'] = int(treegroup)

    if args['--simple']:
        for model in stream.models(**opts):
            print '%04d' % model['seqno'],
            print ' '*model['level']+model['type'].__name__
    else:
        stream.models_json(**opts).dump(sys.stdout)
