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
from hwp5.dataio import WCHAR
from hwp5.binmodel.controls._shared import Control


class PageNumberPosition(Control):
    ''' 4.2.10.9. 쪽 번호 위치 '''
    chid = CHID.PGNP
    Position = Enum(NONE=0,
                    TOP_LEFT=1, TOP_CENTER=2, TOP_RIGHT=3,
                    BOTTOM_LEFT=4, BOTTOM_CENTER=5, BOTTOM_RIGHT=6,
                    OUTSIDE_TOP=7, OUTSIDE_BOTTOM=8,
                    INSIDE_TOP=9, INSIDE_BOTTOM=10)
    Flags = Flags(UINT32,
                  0, 7, 'shape',
                  8, 11, Position, 'position')

    def attributes(cls):
        yield cls.Flags, 'flags'
        yield WCHAR, 'usersymbol'
        yield WCHAR, 'prefix'
        yield WCHAR, 'suffix'
        yield WCHAR, 'dash'
    attributes = classmethod(attributes)
