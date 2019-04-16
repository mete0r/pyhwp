# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from hashlib import sha1
from io import BytesIO
import zlib

from hwp5.distdoc import decode_head_to_sha1
from hwp5.distdoc import decode_head_to_key
from hwp5.distdoc import decrypt_tail
from hwp5.recordstream import read_record
from hwp5.filestructure import Hwp5DistDocStream
from hwp5.tagids import HWPTAG_PARA_HEADER
import hwp5.distdoc
import hwp5.compressed

from .test_filestructure import TestBase


class TestHwp5DistDocFunctions(TestBase):

    hwp5file_name = 'viewtext.hwp'
    password_sha1 = sha1(b'12345').hexdigest()

    @property
    def section(self):
        section = self.olestg['ViewText']['Section0']
        section = Hwp5DistDocStream(section, self.hwp5file.header.version)
        return section

    def test_distdoc_decode_head_to_sha1(self):
        password_sha1 = self.password_sha1
        password_sha1 = password_sha1.upper()
        password_sha1 = password_sha1.encode('utf-16le')
        expected = password_sha1
        section_head = self.section.head()
        decoded = decode_head_to_sha1(section_head)
        self.assertEqual(expected, decoded)

    def test_distdoc_decode_head_to_key(self):
        section = self.section
        expected = self.password_sha1.upper().encode('utf-16le')[:16]
        self.assertEqual(expected, decode_head_to_key(section.head()))
        self.assertEqual(expected, section.head_key())

    def test_distdoc_decrypt_tail(self):
        section = self.section

        key = section.head_key()
        tail = section.tail()
        decrypted = decrypt_tail(key, tail)
        decompressed = zlib.decompress(decrypted, -15)
        record = read_record(BytesIO(decompressed), 0)
        self.assertEqual(0, record['level'])
        self.assertEqual(HWPTAG_PARA_HEADER, record['tagid'])
        self.assertEqual(22, record['size'])

        self.assertEqual(390, len(decompressed))

    def test_distdoc_decode(self):
        section = self.section

        stream = hwp5.distdoc.decode(section.wrapped.open())
        stream = hwp5.compressed.decompress(stream)
        record = read_record(stream, 0)
        self.assertEqual(0, record['level'])
        self.assertEqual(HWPTAG_PARA_HEADER, record['tagid'])
        self.assertEqual(22, record['size'])
