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
from hwp5.tagids import HWPTAG_SHAPE_COMPONENT_PICTURE
from hwp5.dataio import Struct
from hwp5.dataio import Flags
from hwp5.dataio import SHWPUNIT
from hwp5.dataio import UINT32
from hwp5.dataio import UINT16
from hwp5.dataio import INT8
from hwp5.dataio import BYTE
from hwp5.binmodel._shared import Margin
from hwp5.binmodel._shared import Coord
from hwp5.binmodel._shared import BorderLine


class PictureInfo(Struct):
    ''' 표 27 그림 정보 '''
    def attributes():
        yield INT8, 'brightness',
        yield INT8, 'contrast',
        yield BYTE, 'effect',
        yield UINT16, 'bindata_id',
    attributes = staticmethod(attributes)


class PictureEffect(Struct):
    ''' 표 103 그림 효과 속성 '''

    Flags = Flags(UINT32)

    @classmethod
    def attributes(cls):
        yield cls.Flags, 'flags'
        # TODO


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
        ''' 표 102 그림 개체 속성 '''
        yield BorderLine, 'border'
        yield ImageRect, 'rect',
        yield ImageClip, 'clip',
        yield Margin, 'padding',
        yield PictureInfo, 'picture',
        yield dict(type=BYTE, name='border_transparency', version=(5, 0, 2, 2))
        yield dict(type=UINT32, name='instance_id', version=(5, 0, 2, 5))

        # TODO: this choke on 5.0.3.3 d6dfac424525298119de54410c3b22d74aa85511
        # Strangely, its ok on 5.0.3.3 83a0ea1f9da368ff9f0b45f72e9306b776edf38a
        # and other 5.0.3.0, 5.0.3.2 and 5.0.3.4 files.
        yield dict(type=PictureEffect, name='picture_effect',
                   version=(5, 0, 3, 4))

    attributes = staticmethod(attributes)
