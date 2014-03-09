# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2014 mete0r <mete0r@sarangbang.or.kr>
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
from hwp5.binmodel._shared import RecordModel
from hwp5.tagids import HWPTAG_NUMBERING
from hwp5.dataio import Enum
from hwp5.dataio import Flags
from hwp5.dataio import UINT32
from hwp5.dataio import UINT16
from hwp5.dataio import INT32
from hwp5.dataio import BSTR
from hwp5.dataio import HWPUNIT16
from hwp5.dataio import Struct
from hwp5.dataio import ARRAY


class NumberingLevel(Struct):

    # 표 35 문단 머리 정보 속성
    Align = Enum(LEFT=0, CENTER=1, RIGHT=2, UNKNOWN=3)
    DistanceType = Enum(RATIO=0, VALUE=1)
    Flags = Flags(UINT32,
                  0, 1, Align, 'paragraph_align',
                  2, 'auto_width',
                  3, 'auto_dedent',
                  4, DistanceType, 'distance_to_body_type')

    @classmethod
    def attributes(cls):
        ''' 표 34 문단 머리 정보 '''
        yield cls.Flags, 'flags'
        yield HWPUNIT16, 'width_correction'
        yield HWPUNIT16, 'distance_to_body'
        yield INT32, 'charshape_id'
        yield BSTR, 'numbering_format'  # see 표 36 문단 번호 형식


class Numbering(RecordModel):
    ''' 4.1.8. 문단 번호 '''
    tagid = HWPTAG_NUMBERING

    Align = NumberingLevel.Align
    DistanceType = NumberingLevel.DistanceType
    Flags = NumberingLevel.Flags

    def attributes(cls):
        ''' 표 33 문단 번호 '''
        yield ARRAY(NumberingLevel, 7), 'levels'
        yield UINT16, 'starting_number'
        yield dict(type=ARRAY(UINT32, 7),
                   name='unknown',
                   version=(5, 0, 3, 0))
    attributes = classmethod(attributes)
