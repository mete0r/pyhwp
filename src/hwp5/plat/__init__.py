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
from binascii import b2a_hex
from functools import partial
from subprocess import CalledProcessError
from subprocess import Popen
import logging
import os
import subprocess
import tempfile

from . import _lxml
from . import _uno
from . import gir_gsf
from . import javax_transform
from . import jython_poifs
from . import olefileio
from . import xmllint
from . import xsltproc


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


def get_xslt_compile():
    modules = [
        javax_transform,
        _lxml,
        xsltproc,
        _uno
    ]
    for module in modules:
        if module.is_enabled():
            xslt_compile = getattr(module, 'xslt_compile', None)
            if xslt_compile:
                return xslt_compile
            xslt = getattr(module, 'xslt', None)
            if xslt:
                def xslt_compile(xsl_path):
                    return partial(xslt, xsl_path)


def get_relaxng():
    if _lxml.is_enabled():
        return _lxml.relaxng
    if xmllint.is_enabled():
        return xmllint.relaxng


def get_relaxng_compile():
    modules = [
        _lxml,
        xmllint,
    ]
    for module in modules:
        if module.is_enabled():
            relaxng_compile = getattr(module, 'relaxng_compile', None)
            if relaxng_compile:
                return relaxng_compile
            relaxng = getattr(module, 'relaxng', None)
            if relaxng:
                def relaxng_compile(rng_path):
                    return partial(relaxng, rng_path)


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
        return get_aes128ecb_decrypt_cryptography()
    except Exception:
        pass

    try:
        return get_aes128ecb_decrypt_javax()
    except Exception:
        pass

    try:
        return get_aes128ecb_decrypt_openssl()
    except Exception:
        pass

    raise NotImplementedError('aes128ecb_decrypt')


def get_aes128ecb_decrypt_cryptography():
    from cryptography.hazmat.primitives.ciphers import Cipher
    from cryptography.hazmat.primitives.ciphers import algorithms
    from cryptography.hazmat.primitives.ciphers import modes
    from cryptography.hazmat.backends import default_backend

    def decrypt(key, ciphertext):
        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend)
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()

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


def get_aes128ecb_decrypt_openssl():
    if not openssl_reachable():
        raise NotImplementedError()

    def decrypt(key, ciphertext):
        fd, name = tempfile.mkstemp()
        fp = os.fdopen(fd, 'wb')
        try:
            fp.write(ciphertext)
        finally:
            fp.close()

        args = [
            'openssl',
            'enc',
            '-d',
            '-in',
            name,
            '-aes-128-ecb',
            '-K',
            b2a_hex(key),
            '-nopad',
        ]
        try:
            p = Popen(args, stdout=subprocess.PIPE)
            try:
                return p.stdout.read()
            finally:
                p.wait()
                p.stdout.close()
        finally:
            os.unlink(name)

    return decrypt


def openssl_reachable():
    args = ['openssl', 'version']
    try:
        subprocess.check_output(args)
    except OSError:
        return False
    except CalledProcessError:
        return False
    except Exception as e:
        logger.exception(e)
        return False
    else:
        return True
