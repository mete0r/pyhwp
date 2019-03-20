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
from hwp5.tagids import HWPTAG_SHAPE_COMPONENT_LINE
from hwp5.dataio import UINT16
from hwp5.binmodel._shared import Coord


class ShapeLine(RecordModel):
    ''' 4.2.9.2.2. 선 개체 '''
    tagid = HWPTAG_SHAPE_COMPONENT_LINE

    def attributes():
        ''' 표 87 선 개체 속성 '''
        yield Coord, 'p0'
        yield Coord, 'p1'
        yield UINT16, 'attr'
    attributes = staticmethod(attributes)
