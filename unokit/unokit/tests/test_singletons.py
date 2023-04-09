# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010,2011,2012 https://github.com/mete0r
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


class TestBase(TestCase):
    pass


class TestSingletons(TestBase):
    def test_extman(self):
        from unokit.singletons import css
        extman = css.deployment.ExtensionManager
        self.assertTrue(extman is not None)

    def test_pkginfo_prov(self):
        from unokit.singletons import css
        pkginfo_prov = css.deployment.PackageInformationProvider
        self.assertTrue(pkginfo_prov is not None)

        for ext_id, ext_ver in pkginfo_prov.ExtensionList:
            ext_loc = pkginfo_prov.getPackageLocation(ext_id)
            print ext_id, ext_ver, ext_loc
            self.assertTrue(ext_loc != '')
