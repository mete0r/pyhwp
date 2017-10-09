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
from hwp5.tagids import HWPTAG_SHAPE_COMPONENT_ELLIPSE
from hwp5.dataio import Flags
from hwp5.dataio import UINT32
from hwp5.binmodel._shared import Coord


class ShapeEllipse(RecordModel):
    ''' 4.2.9.2.4. 타원 개체 '''
    tagid = HWPTAG_SHAPE_COMPONENT_ELLIPSE

    ''' 표 92 타원/호 개체 속성 '''
    Flags = Flags(UINT32,
                  0, 'arc_recalc_required',
                  1, 'arc',
                  2, 9, 'arc_kind')

    def attributes(cls):
        ''' 표 91 타원 개체 속성 '''
        yield cls.Flags, 'flags'
        yield Coord, 'center'
        yield Coord, 'axis1'
        yield Coord, 'axis2'
        yield Coord, 'start1'
        yield Coord, 'end1'
        yield Coord, 'start2'
        yield Coord, 'end2'
    attributes = classmethod(attributes)
