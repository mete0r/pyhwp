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

from hwp5.binmodel._shared import RecordModel
from hwp5.tagids import HWPTAG_TAB_DEF
from hwp5.dataio import HWPUNIT
from hwp5.dataio import UINT32
from hwp5.dataio import Enum
from hwp5.dataio import Flags
from hwp5.dataio import Struct
from hwp5.dataio import N_ARRAY


class Tab(Struct):

    Kind = Enum(LEFT=0, RIGHT=1, CENTER=2, FLOAT=3)

    Flags = Flags(UINT32,
                  0, 7, Kind, 'kind',
                  8, 15, 'fill_type')

    @classmethod
    def attributes(cls):
        yield HWPUNIT, 'pos',
        yield cls.Flags, 'flags'


class TabDef(RecordModel):
    ''' 4.1.7. 탭 정의 '''

    tagid = HWPTAG_TAB_DEF

    ''' 표 32 탭 정의 속성 '''
    Flags = Flags(UINT32,
                  0, 'autotab_left',
                  1, 'autotab_right')

    @classmethod
    def attributes(cls):
        yield dict(type=cls.Flags, name='flags')
        yield dict(type=N_ARRAY(UINT32, Tab), name='tabs')
