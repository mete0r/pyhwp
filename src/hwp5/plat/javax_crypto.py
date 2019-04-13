# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2019 mete0r <mete0r@sarangbang.or.kr>
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
import logging

from zope.interface import implementer

from ..errors import ImplementationNotAvailable
from ..interfaces import IAES128ECB


logger = logging.getLogger(__name__)


def createAES128ECB(registry, **settings):
    try:
        from javax.crypto import Cipher
        from javax.crypto.spec import SecretKeySpec
    except ImportError:
        raise ImplementationNotAvailable('aes128ecb/javax.crypto')
    else:
        return AES128ECB(Cipher, SecretKeySpec)


@implementer(IAES128ECB)
class AES128ECB:

    def __init__(self, Cipher, SecretKeySpec):
        self.Cipher = Cipher
        self.SecretKeySpec = SecretKeySpec

    def decrypt(self, key, ciphertext):
        Cipher = self.Cipher
        SecretKeySpec = self.SecretKeySpec

        secretkey = SecretKeySpec(key, 'AES')
        cipher = Cipher.getInstance('AES/ECB/NoPadding')
        cipher.init(Cipher.DECRYPT_MODE, secretkey)
        decrypted = cipher.doFinal(ciphertext)
        return decrypted.tostring()
