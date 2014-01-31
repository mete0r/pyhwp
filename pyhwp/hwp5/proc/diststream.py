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

    hwp5proc diststream
    hwp5proc diststream sha1 [--raw]
    hwp5proc diststream key [[--raw]
    hwp5proc diststream [--loglevel=<loglevel>] [--logfile=<logfile>]
    hwp5proc diststream --help

Options::

    -h --help               Show this screen
       --loglevel=<level>   Set log level.
       --logfile=<file>     Set log file.

Example::

    $ hwp5proc cat --ole samples/viewtext.hwp ViewText/Section0
      | tee Section0.zraw.aes128ecb | hwp5proc diststream | tee Section0.zraw
      | hwp5proc rawunz > Section0

    $ hwp5proc diststream sha1 < Section0.zraw.aes128ecb
    $ echo -n '12345' | sha1sum

'''
from binascii import b2a_hex
from binascii import a2b_hex
import logging

from hwp5.proc import entrypoint
from hwp5.distdoc import decode
from hwp5.distdoc import decode_head_to_sha1
from hwp5.distdoc import decode_head_to_key
from hwp5.recordstream import read_record


logger = logging.getLogger(__name__)


@entrypoint(__doc__)
def main(args):
    import sys
    import shutil

    if args['sha1']:
        head = read_record(sys.stdin, 0)
        sha1ucs16le = decode_head_to_sha1(head['payload'])
        sha1 = a2b_hex(sha1ucs16le.decode('utf-16le'))
        if not args['--raw']:
            sha1 = b2a_hex(sha1)
        sys.stdout.write(sha1)
    elif args['key']:
        head = read_record(sys.stdin, 0)
        key = decode_head_to_key(head['payload'])
        if not args['--raw']:
            key = b2a_hex(key)
        sys.stdout.write(key)
    else:
        result = decode(sys.stdin)
        shutil.copyfileobj(result, sys.stdout)
