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
from binascii import b2a_hex
from subprocess import CalledProcessError
import logging
import os
import subprocess
import tempfile

from zope.interface import implementer

from ..errors import ImplementationNotAvailable
from ..interfaces import IAES128ECB


logger = logging.getLogger(__name__)


def createAES128ECB(registry, **settings):
    executable = settings.get('openssl.path', 'openssl')
    if not openssl_is_reachable(executable):
        raise ImplementationNotAvailable(
            'aes128ecb/openssl: openssl not found', executable
        )
    return AES128ECB(executable)


@implementer(IAES128ECB)
class AES128ECB:

    def __init__(self, executable):
        self.executable = executable

    def decrypt(self, key, ciphertext):
        fd, name = tempfile.mkstemp()
        fp = os.fdopen(fd, 'wb')
        try:
            fp.write(ciphertext)
        finally:
            fp.close()

        args = [
            self.executable,
            'enc',
            '-d',
            '-in', name,
            '-aes-128-ecb',
            '-K', b2a_hex(key),
            '-nopad',
        ]
        try:
            p = subprocess.Popen(args, stdout=subprocess.PIPE)
            try:
                return p.stdout.read()
            finally:
                p.wait()
                p.stdout.close()
                if p.returncode != 0:
                    raise Exception('Decryption failed')
        finally:
            os.unlink(name)


def openssl_is_reachable(executable):
    args = [executable, 'version']
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
