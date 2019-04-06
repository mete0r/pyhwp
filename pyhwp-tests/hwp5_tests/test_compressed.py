# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from io import BytesIO
from unittest import TestCase
import os
import zlib

from hwp5.compressed import ZLibIncrementalDecoder
from hwp5.compressed import decompress
from hwp5.compressed import decompress_gen
from hwp5.utils import cached_property


class TestUncompress(TestCase):

    @cached_property
    def original_data(self):
        return os.urandom(16384)

    @cached_property
    def compressed_data(self):
        return zlib.compress(self.original_data)

    def test_incremental_decode(self):
        compressed_data = self.compressed_data

        dec = ZLibIncrementalDecoder(wbits=-15)
        data = dec.decode(compressed_data[2:2048])
        data += dec.decode(compressed_data[2048:2048 + 1024])
        data += dec.decode(compressed_data[2048 + 1024:2048 + 1024 + 4096])
        data += dec.decode(compressed_data[2048 + 1024 + 4096:], True)

        self.assertEqual(self.original_data, data)

    def test_decompress(self):

        gen = decompress_gen(BytesIO(self.compressed_data[2:]))
        self.assertEqual(self.original_data, b''.join(gen))

        # print '-----'

        f = decompress(BytesIO(self.compressed_data[2:]))
        g = BytesIO(self.original_data)

        self.assertEqual(f.read(2048), g.read(2048))
        self.assertEqual(f.read(1024), g.read(1024))
        self.assertEqual(f.read(4096), g.read(4096))
        self.assertEqual(f.read(), g.read())
