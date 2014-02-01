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
import logging
from hwp5.plat import olefileio
from hwp5.plat import _lxml
from hwp5.plat import xsltproc
from hwp5.plat import xmllint
from hwp5.plat import javax_transform
from hwp5.plat import jython_poifs
from hwp5.plat import _uno
from hwp5.plat import gir_gsf


logger = logging.getLogger(__name__)


def get_xslt():
    if javax_transform.is_enabled():
        return javax_transform.xslt
    if _lxml.is_enabled():
        return _lxml.xslt
    if xsltproc.is_enabled():
        return xsltproc.xslt
    if _uno.is_enabled():
        return _uno.xslt


def get_relaxng():
    if _lxml.is_enabled():
        return _lxml.relaxng
    if xmllint.is_enabled():
        return xmllint.relaxng


def get_olestorage_class():
    if jython_poifs.is_enabled():
        return jython_poifs.OleStorage
    if olefileio.is_enabled():
        return olefileio.OleStorage
    if _uno.is_enabled():
        return _uno.OleStorage
    if gir_gsf.is_enabled():
        return gir_gsf.OleStorage


def get_aes128ecb_decrypt():
    try:
        return get_aes128ecb_decrypt_pycrypto()
    except Exception:
        pass

    try:
        return get_aes128ecb_decrypt_javax()
    except Exception:
        pass

    raise NotImplementedError('aes128ecb_decrypt')


def get_aes128ecb_decrypt_pycrypto():
    from Crypto.Cipher import AES

    def decrypt(key, ciphertext):
        cipher = AES.new(key, AES.MODE_ECB)
        return cipher.decrypt(ciphertext)

    return decrypt


def get_aes128ecb_decrypt_javax():
    from javax.crypto import Cipher
    from javax.crypto.spec import SecretKeySpec

    def decrypt(key, ciphertext):
        secretkey = SecretKeySpec(key, 'AES')
        cipher = Cipher.getInstance('AES/ECB/NoPadding')
        cipher.init(Cipher.DECRYPT_MODE, secretkey)
        decrypted = cipher.doFinal(ciphertext)
        return decrypted.tostring()

    return decrypt
