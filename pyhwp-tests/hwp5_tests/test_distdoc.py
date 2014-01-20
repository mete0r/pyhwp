# -*- coding: utf-8 -*-
from binascii import b2a_hex
from hashlib import sha1

from hwp5.filestructure import Hwp5DistDoc
from hwp5.distdoc import decode_head_to_sha1

from hwp5_tests.test_filestructure import TestBase


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
