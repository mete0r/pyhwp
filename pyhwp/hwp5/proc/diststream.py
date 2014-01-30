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
''' Decode distribute doc stream.

Usage::

    hwp5proc diststream sha1 [--raw]
    hwp5proc diststream [--loglevel=<loglevel>] [--logfile=<logfile>]
    hwp5proc diststream --help

Options::

    -h --help               Show this screen
       --loglevel=<level>   Set log level.
       --logfile=<file>     Set log file.
'''
from binascii import b2a_hex
import logging

from hwp5.proc import entrypoint
from hwp5.distdoc import decode_head_to_sha1


logger = logging.getLogger(__name__)


@entrypoint(__doc__)
def main(args):
    import sys

    # skip record header
    sys.stdin.read(4)

    payload = sys.stdin.read(256)

    if args['sha1']:
        result = decode_head_to_sha1(payload)

    if not args['--raw']:
        result = b2a_hex(result)

    sys.stdout.write(result)
