# -*- coding: utf-8 -*-
#
#                   GNU AFFERO GENERAL PUBLIC LICENSE
#                      Version 3, 19 November 2007
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010 mete0r@sarangbang.or.kr
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
from unittest import TestCase
from unokit.remote import RemoteContextLayer


class TestBase(TestCase):

    layer = RemoteContextLayer


class GetSofficeProductInfoTest(TestBase):
    def test_basic(self):
        from unokit.configuration import get_soffice_product_info
        info = get_soffice_product_info()
        self.assertTrue('name' in info)
        self.assertTrue('vendor' in info)
        self.assertTrue('version' in info)
        self.assertTrue('locale' in info)
