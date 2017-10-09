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
from io import BytesIO
import codecs
import zlib

from .utils import GeneratorReader


class ZLibIncrementalDecoder(codecs.IncrementalDecoder):
    def __init__(self, errors='strict', wbits=15):
        assert errors == 'strict'
        self.errors = errors
        self.wbits = wbits
        self.reset()

    def decode(self, input, final=False):
        c = self.decompressobj.decompress(input)
        if final:
            c += self.decompressobj.flush()
        return c

    def reset(self):
        self.decompressobj = zlib.decompressobj(self.wbits)


def decompress_gen(source, bufsize=4096):
    dec = ZLibIncrementalDecoder(wbits=-15)
    exausted = False
    while not exausted:
        input = source.read(bufsize)
        if len(input) < bufsize:
            exausted = True
        yield dec.decode(input, exausted)


def decompress_experimental(source, bufsize=4096):
    ''' decompress inputstream

        stream: a file-like readable
        returns a file-like readable
    '''
    return GeneratorReader(decompress_gen(source, bufsize))


def decompress(stream):
    ''' decompress inputstream

        stream: a file-like readable
        returns a file-like readable
    '''
    return BytesIO(zlib.decompress(stream.read(), -15))  # without gzip header
