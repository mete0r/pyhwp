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
from hwp5.tagids import HWPTAG_PARA_RANGE_TAG
from hwp5.dataio import UINT32
from hwp5.dataio import Flags
from hwp5.dataio import Struct
from hwp5.dataio import X_ARRAY
from hwp5.binmodel._shared import ref_parent_member


class RangeTag(Struct):
    ''' 표 58 문단의 영역 태그 '''

    Tag = Flags(UINT32,
                0, 23, 'data',
                24, 31, 'kind')

    @classmethod
    def attributes(cls):
        yield UINT32, 'start'
        yield UINT32, 'end'
        yield cls.Tag, 'tag'


class ParaRangeTag(RecordModel):
    ''' 4.2.5. 문단의 영역 태그 '''

    tagid = HWPTAG_PARA_RANGE_TAG

    @staticmethod
    def attributes():
        yield dict(name='range_tags',
                   type=X_ARRAY(RangeTag, ref_parent_member('rangetags')))
