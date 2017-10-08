# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from binascii import b2a_hex
from hashlib import sha1
from StringIO import StringIO
import zlib

from hwp5.filestructure import Hwp5DistDoc
from hwp5.distdoc import decode_head_to_sha1
from hwp5.distdoc import decode_head_to_key
from hwp5.distdoc import decrypt_tail
from hwp5.recordstream import read_record
from hwp5.tagids import HWPTAG_PARA_HEADER
import hwp5.distdoc
import hwp5.compressed

from .test_filestructure import TestBase


class TestHwp5DistDocFunctions(TestBase):

    hwp5file_name = 'viewtext.hwp'
    password_sha1 = sha1('12345').digest()

    @property
    def hwp5distdoc(self):
        return Hwp5DistDoc(self.olestg)

    @property
    def section(self):
        return self.hwp5distdoc['ViewText']['Section0']

    def test_distdoc_decode_head_to_sha1(self):
        expected = b2a_hex(self.password_sha1).upper().encode('utf-16le')
        self.assertEquals(expected, decode_head_to_sha1(self.section.head()))

    def test_distdoc_decode_head_to_key(self):
        section = self.section
        expected = b2a_hex(self.password_sha1).upper().encode('utf-16le')[:16]
        self.assertEquals(expected, decode_head_to_key(section.head()))
        self.assertEquals(expected, section.head_key())

    def test_distdoc_decrypt_tail(self):
        section = self.section

        key = section.head_key()
        tail = section.tail()
        try:
            decrypted = decrypt_tail(key, tail)
        except NotImplementedError, e:
            if e.message == 'aes128ecb_decrypt':
                # skip this test
                return
            raise
        decompressed = zlib.decompress(decrypted, -15)
        record = read_record(StringIO(decompressed), 0)
        self.assertEquals(0, record['level'])
        self.assertEquals(HWPTAG_PARA_HEADER, record['tagid'])
        self.assertEquals(22, record['size'])

        self.assertEquals(390, len(decompressed))

    def test_distdoc_decode(self):
        section = self.section

        try:
            stream = hwp5.distdoc.decode(section.wrapped.open())
        except NotImplementedError, e:
            if e.message == 'aes128ecb_decrypt':
                # skip this test
                return
            raise
        stream = hwp5.compressed.decompress(stream)
        record = read_record(stream, 0)
        self.assertEquals(0, record['level'])
        self.assertEquals(HWPTAG_PARA_HEADER, record['tagid'])
        self.assertEquals(22, record['size'])
