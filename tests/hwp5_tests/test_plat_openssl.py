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
from unittest import TestCase

from hwp5.errors import ImplementationNotAvailable

from .mixin_aes128ecb import AES128ECBTestMixin


class AES128ECBOnOpenSSL(TestCase, AES128ECBTestMixin):

    def setUp(self):
        from hwp5.plat.openssl import createAES128ECB
        try:
            aes128ecb = createAES128ECB(None)
        except ImplementationNotAvailable:
            self.aes128ecb = None
        else:
            self.aes128ecb = aes128ecb
