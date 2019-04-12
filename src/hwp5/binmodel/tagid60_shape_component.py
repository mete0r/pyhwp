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
from hwp5.tagids import HWPTAG_SHAPE_COMPONENT
from hwp5.dataio import Flags
from hwp5.dataio import UINT32
from hwp5.dataio import UINT16
from hwp5.dataio import UINT8
from hwp5.dataio import SHWPUNIT
from hwp5.dataio import WORD
from hwp5.dataio import BYTE
from hwp5.dataio import X_ARRAY
from hwp5.dataio import N_ARRAY
from hwp5.dataio import Struct
from hwp5.dataio import DOUBLE
from hwp5.dataio import ref_member
from hwp5.dataio import HexBytes
from hwp5.binmodel.controlchar import CHID
from hwp5.binmodel._shared import Coord
from hwp5.binmodel._shared import BorderLine
from hwp5.binmodel._shared import FillColorPattern
from hwp5.binmodel._shared import FillGradation
from hwp5.binmodel._shared import FillImage
from hwp5.binmodel.controls.gshape_object_control import GShapeObjectControl


class Matrix(Struct):
    ''' 표 80 matrix 정보

    2D Transform Matrix

    [a c e][x]
    [b d f][y]
    [0 0 1][1]
    '''
    def attributes():
        yield DOUBLE, 'a'
        yield DOUBLE, 'c'
        yield DOUBLE, 'e'
        yield DOUBLE, 'b'
        yield DOUBLE, 'd'
        yield DOUBLE, 'f'
    attributes = staticmethod(attributes)


class ScaleRotationMatrix(Struct):
    def attributes():
        yield Matrix, 'scaler',
        yield Matrix, 'rotator',
    attributes = staticmethod(attributes)


def parent_must_be_gso(context, values):
    ''' parent record type is GShapeObjectControl '''
    # GSO-child ShapeComponent specific:
    # it may be a GSO model's attribute, e.g. 'child_chid'
    if 'parent' in context:
        parent_context, parent_model = context['parent']
        return parent_model['type'] is GShapeObjectControl


def chid_is_container(context, values):
    ''' chid == CHID.CONTAINER '''
    return values['chid'] == CHID.CONTAINER


def chid_is_rect(context, values):
    ''' chid == CHID.RECT '''
    return values['chid'] == CHID.RECT


def chid_is_rect_and_fill_colorpattern(context, values):
    ''' chid == CHID.RECT and fill_flags.fill_colorpattern '''
    return (values['chid'] == CHID.RECT and
            values['fill_flags'].fill_colorpattern)


def chid_is_rect_and_fill_image(context, values):
    ''' chid == CHID.RECT and fill_flags.fill_image '''
    return (values['chid'] == CHID.RECT and
            values['fill_flags'].fill_image)


def chid_is_rect_and_fill_gradation(context, values):
    ''' chid == CHID.RECT and fill_flags.fill_gradation '''
    return (values['chid'] == CHID.RECT and
            values['fill_flags'].fill_gradation)


def chid_is_line(context, values):
    ''' chid == CHID.LINE '''
    return values['chid'] == CHID.LINE


class ShapeComponent(RecordModel):
    ''' 4.2.9.2.1. 개체 요소 '''
    tagid = HWPTAG_SHAPE_COMPONENT
    FillFlags = Flags(UINT16,
                      8, 'fill_colorpattern',
                      9, 'fill_image',
                      10, 'fill_gradation')
    Flags = Flags(UINT32,
                  0, 'flip')

    def attributes(cls):
        ''' 표 78 개체 요소 속성 '''

        yield dict(type=CHID, name='chid0', condition=parent_must_be_gso)

        yield CHID, 'chid'
        yield SHWPUNIT, 'x_in_group'
        yield SHWPUNIT, 'y_in_group'
        yield WORD, 'level_in_group'
        yield WORD, 'local_version'
        yield SHWPUNIT, 'initial_width'
        yield SHWPUNIT, 'initial_height'
        yield SHWPUNIT, 'width'
        yield SHWPUNIT, 'height'
        yield cls.Flags, 'flags'
        yield WORD, 'angle'
        yield Coord, 'rotation_center'

        ''' 표 79 Rendering 정보 '''
        yield WORD, 'scalerotations_count'
        yield Matrix, 'translation'
        yield dict(type=X_ARRAY(ScaleRotationMatrix,
                                ref_member('scalerotations_count')),
                   name='scalerotations')

        #
        # Container
        #

        yield dict(type=N_ARRAY(WORD, CHID),
                   name='controls',
                   condition=chid_is_container)

        #
        # Rectangle
        #

        ''' 표 81 테두리 선 정보 '''
        yield dict(type=BorderLine, name='border', condition=chid_is_rect)
        ''' 표 83 Outline style '''
        # TODO: Outline ???
        yield dict(type=cls.FillFlags, name='fill_flags',
                   condition=chid_is_rect)
        yield dict(type=UINT16, name='unknown', condition=chid_is_rect)
        yield dict(type=UINT8, name='unknown1', condition=chid_is_rect)
        yield dict(type=FillColorPattern, name='fill_colorpattern',
                   condition=chid_is_rect_and_fill_colorpattern)
        yield dict(type=FillGradation, name='fill_gradation',
                   condition=chid_is_rect_and_fill_gradation)
        yield dict(type=FillImage, name='fill_image',
                   condition=chid_is_rect_and_fill_image)
        yield dict(type=UINT32, name='fill_shape',
                   condition=chid_is_rect)
        yield dict(type=BYTE, name='fill_blur_center',
                   condition=chid_is_rect_and_fill_gradation)

        # TODO: 아래 두 필드: chid == $rec일 때만인지 확인 필요
        yield dict(type=HexBytes(5), name='unknown2',
                   condition=chid_is_rect, version=(5, 0, 2, 4))
        yield dict(type=HexBytes(16), name='unknown3',
                   condition=chid_is_rect, version=(5, 0, 2, 4))

        #
        # Line
        #

        yield dict(type=BorderLine, name='line',
                   condition=chid_is_line)
    attributes = classmethod(attributes)
