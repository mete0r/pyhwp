# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2023 mete0r <https://github.com/mete0r>
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
    hwp5proc diststream key [--raw]
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
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from binascii import b2a_hex
from binascii import a2b_hex
import logging
import shutil
import sys

from ..distdoc import decode
from ..distdoc import decode_head_to_sha1
from ..distdoc import decode_head_to_key
from ..recordstream import read_record


PY2 = sys.version_info.major == 2
logger = logging.getLogger(__name__)


def main(args):
    if PY2:
        input_fp = sys.stdin
        output_fp = sys.stdout
    else:
        input_fp = sys.stdin.buffer
        output_fp = sys.stdout.buffer

    if args.sha1:
        head = read_record(input_fp, 0)
        sha1ucs16le = decode_head_to_sha1(head['payload'])
        sha1 = a2b_hex(sha1ucs16le.decode('utf-16le'))
        if not args.raw:
            sha1 = b2a_hex(sha1)
        output_fp.write(sha1)
    elif args.key:
        head = read_record(input_fp, 0)
        key = decode_head_to_key(head['payload'])
        if not args.raw:
            key = b2a_hex(key)
        output_fp.write(key)
    else:
        result = decode(input_fp)
        shutil.copyfileobj(result, output_fp)


def diststream_argparser(subparsers, _):
    parser = subparsers.add_parser(
        'diststream',
        help=_(
            'Decode a distribute document stream.'
        ),
        description=_(
            'Decode a distribute document stream.'
        ),
    )
    op_group = parser.add_mutually_exclusive_group()
    op_group.add_argument(
        '--sha1',
        action='store_true',
        help=_('Print SHA-1 value for decryption.'),
    )
    op_group.add_argument(
        '--key',
        action='store_true',
        help=_('Print decrypted key.'),
    )
    parser.add_argument(
        '--raw',
        action='store_true',
        help=_('Print raw binary objects as is.'),
    )
    parser.set_defaults(func=main)
    return parser
