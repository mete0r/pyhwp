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
import codecs
import zlib  # this codec needs the optional zlib module !

_wbits = -15


def zlib_raw_encode(input, errors='strict'):
    assert errors == 'strict'
    output = zlib.compress(input)[2:-4]
    return (output, len(input))


def zlib_raw_decode(input, errors='strict'):
    assert errors == 'strict'
    output = zlib.decompress(input, _wbits)
    return (output, len(input))


class Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        return zlib_raw_encode(input, errors)

    def decode(self, input, errors='strict'):
        return zlib_raw_decode(input, errors)


class IncrementalEncoder(codecs.IncrementalEncoder):
    def __init__(self, errors='strict'):
        assert errors == 'strict'
        self.errors = errors
        self.compressobj = zlib.compressobj()
        self.initial = True

    def encode(self, input, final=False):
        c = self.compressobj.compress(input)
        if self.initial:
            c = c[2:]
            self.initial = False
        if final:
            c += self.compressobj.flush()[:-4]
        return c

    def reset(self):
        self.compressobj = zlib.compressobj()


class IncrementalDecoder(codecs.IncrementalDecoder):
    def __init__(self, errors='strict'):
        assert errors == 'strict'
        self.errors = errors
        self.decompressobj = zlib.decompressobj(_wbits)

    def decode(self, input, final=False):
        if final:
            if len(input) > 0:
                d = self.decompressobj.decompress(input)
            else:
                d = b''
            return d + self.decompressobj.flush()
        else:
            return self.decompressobj.decompress(input)

    def reset(self):
        self.decompressobj = zlib.decompressobj(_wbits)


class StreamWriter(object):
    def __init__(self, stream, errors='strict'):
        assert errors == 'strict'
        self.stream = stream
        self.encoder = IncrementalEncoder(errors)

    def write(self, data):
        raise NotImplementedError


class StreamReader(object):
    def __init__(self, stream, errors='strict'):
        assert errors == 'strict'
        self.stream = stream
        self.decoder = IncrementalDecoder(errors)
        self.buffer = b''
        self.offset = 0

    def read(self, size=-1):
        if size < 0:
            c = self.stream.read()
            d = self.buffer + self.decoder.decode(c, True)
            self.buffer = b''
            self.offset += len(d)
            return d

        final = False
        while True:
            if size <= len(self.buffer):
                d = self.buffer[:size]
                self.buffer = self.buffer[size:]
                self.offset += size
                return d

            if final:
                d = self.buffer
                self.buffer = b''
                self.offset += len(d)
                return d

            c = self.stream.read(8196)
            final = len(c) < 8196 or len(c)
            self.buffer += self.decoder.decode(c, final)

    def tell(self):
        return self.offset


_codecinfo = codecs.CodecInfo(
    name='zlib_raw',
    encode=zlib_raw_encode,
    decode=zlib_raw_decode,
    incrementalencoder=IncrementalEncoder,
    incrementaldecoder=IncrementalDecoder,
    streamreader=StreamReader,
    streamwriter=StreamWriter,
)
