# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2023 mete0r <https://github.com/mete0r>
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
from hwp5.tagids import HWPTAG_SHAPE_COMPONENT_POLYGON
from hwp5.dataio import N_ARRAY
from hwp5.dataio import UINT16
from hwp5.binmodel._shared import Coord


class ShapePolygon(RecordModel):
    ''' 4.2.9.2.5. 다각형 개체 '''
    tagid = HWPTAG_SHAPE_COMPONENT_POLYGON

    def attributes(cls):
        ''' 표 94 다각형 개체 속성 '''
        yield N_ARRAY(UINT16, Coord), 'points'
    attributes = classmethod(attributes)
