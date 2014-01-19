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
''' Deflate an headerless zlib-compressed stream

Usage::

    hwp5proc rawunz [--loglevel=<loglevel>] [--logfile=<logfile>]
    hwp5proc rawunz --help

Options::

    -h --help               Show this screen
       --loglevel=<level>   Set log level.
       --logfile=<file>     Set log file.
'''
from hwp5.proc import entrypoint


@entrypoint(__doc__)
def main(args):
    import sys
    from hwp5.zlib_raw_codec import StreamReader
    stream = StreamReader(sys.stdin)
    while True:
        buf = stream.read(64)
        if len(buf) == 0:
            break
        sys.stdout.write(buf)
