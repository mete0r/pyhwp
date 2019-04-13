# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2015,2019 mete0r <mete0r@sarangbang.or.kr>
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

from ..errors import ImplementationNotAvailable
from . import _uno
from . import gir_gsf
from . import jython_poifs
from . import olefileio


logger = logging.getLogger(__name__)


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
    aes128ecb = create_aes128ecb()
    if aes128ecb is None:
        raise ImplementationNotAvailable('aes128ecb')
    return aes128ecb.decrypt


def create_aes128ecb():
    from hwp5.plat import _cryptography
    from hwp5.plat import javax_crypto
    from hwp5.plat import openssl

    try:
        aes128ecb = _cryptography.createAES128ECB(None)
    except ImplementationNotAvailable:
        pass
    else:
        logger.info('AES128ECB: cryptography')
        return aes128ecb

    try:
        aes128ecb = javax_crypto.createAES128ECB(None)
    except ImplementationNotAvailable:
        pass
    else:
        logger.info('AES128ECB: javax.crypto')
        return aes128ecb

    try:
        aes128ecb = openssl.createAES128ECB(None)
    except ImplementationNotAvailable:
        pass
    else:
        logger.info('AES128ECB: openssl')
        return aes128ecb
