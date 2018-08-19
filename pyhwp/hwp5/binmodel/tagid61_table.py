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
from hwp5.tagids import HWPTAG_TABLE
from hwp5.dataio import Enum
from hwp5.dataio import Flags
from hwp5.dataio import UINT32
from hwp5.dataio import UINT16
from hwp5.dataio import HWPUNIT16
from hwp5.dataio import N_ARRAY
from hwp5.dataio import X_ARRAY
from hwp5.dataio import ref_member
from hwp5.dataio import Struct
from hwp5.binmodel._shared import Margin


class ZoneInfo(Struct):
    def attributes():
        ''' 표 73 영역 속성 '''
        yield UINT16, 'starting_column'
        yield UINT16, 'starting_row'
        yield UINT16, 'end_column'
        yield UINT16, 'end_row'
        yield UINT16, 'borderfill_id'
    attributes = staticmethod(attributes)


class TableBody(RecordModel):
    ''' 4.2.9.1. 표 개체 '''
    tagid = HWPTAG_TABLE

    # 표 71 표 속성의 속성
    Split = Enum(NONE=0, BY_CELL=1, SPLIT=2)
    Flags = Flags(UINT32,
                  0, 1, Split, 'split_page',
                  2, 'repeat_header')

    def attributes(cls):
        ''' 표 70 표 개체 속성 '''
        yield cls.Flags, 'flags'
        yield UINT16, 'rows'
        yield UINT16, 'cols'
        yield HWPUNIT16, 'cellspacing'

        # 표 72 안쪽 여백 정보
        yield Margin, 'padding'

        yield dict(type=X_ARRAY(UINT16, ref_member('rows')),
                   name='rowcols')
        yield UINT16, 'borderfill_id'
        yield dict(type=N_ARRAY(UINT16, ZoneInfo),
                   name='validZones',
                   version=(5, 0, 0, 7))
    attributes = classmethod(attributes)
