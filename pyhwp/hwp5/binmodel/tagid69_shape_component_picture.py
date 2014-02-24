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
from hwp5.tagids import HWPTAG_SHAPE_COMPONENT_PICTURE
from hwp5.dataio import Struct
from hwp5.dataio import SHWPUNIT
from hwp5.dataio import UINT16
from hwp5.dataio import INT8
from hwp5.dataio import BYTE
from hwp5.binmodel._shared import Margin
from hwp5.binmodel._shared import Coord
from hwp5.binmodel._shared import BorderLine


class PictureInfo(Struct):
    def attributes():
        yield INT8, 'brightness',
        yield INT8, 'contrast',
        yield BYTE, 'effect',
        yield UINT16, 'bindata_id',
    attributes = staticmethod(attributes)


# HWPML에서의 이름 사용
class ImageRect(Struct):
    ''' 이미지 좌표 정보 '''

    def attributes():
        yield Coord, 'p0'
        yield Coord, 'p1'
        yield Coord, 'p2'
        yield Coord, 'p3'
    attributes = staticmethod(attributes)


# HWPML에서의 이름 사용
class ImageClip(Struct):
    ''' 이미지 자르기 정보 '''

    def attributes():
        yield SHWPUNIT, 'left',
        yield SHWPUNIT, 'top',
        yield SHWPUNIT, 'right',
        yield SHWPUNIT, 'bottom',
    attributes = staticmethod(attributes)


class ShapePicture(RecordModel):
    ''' 4.2.9.4. 그림 개체 '''
    tagid = HWPTAG_SHAPE_COMPONENT_PICTURE

    def attributes():
        yield BorderLine, 'border'
        yield ImageRect, 'rect',
        yield ImageClip, 'clip',
        yield Margin, 'padding',
        yield PictureInfo, 'picture',
        # DIFFSPEC
            # BYTE, 'transparency',
            # UINT32, 'instanceId',
            # PictureEffect, 'effect',
    attributes = staticmethod(attributes)
