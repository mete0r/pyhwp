# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2015 mete0r <mete0r@sarangbang.or.kr>
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

from hwp5.binmodel.controlchar import CHID
from hwp5.dataio import Enum
from hwp5.dataio import Flags
from hwp5.dataio import UINT32
from hwp5.binmodel.controls._shared import Control


class HeaderFooter(Control):
    ''' 4.2.10.3. 머리말/꼬리말 '''
    Places = Enum(BOTH_PAGES=0, EVEN_PAGE=1, ODD_PAGE=2)
    Flags = Flags(UINT32,
                  0, 1, Places, 'places')

    def attributes(cls):
        yield cls.Flags, 'flags'
    attributes = classmethod(attributes)


class Header(HeaderFooter):
    ''' 머리말 '''
    chid = CHID.HEADER


class Footer(HeaderFooter):
    ''' 꼬리말 '''
    chid = CHID.FOOTER
