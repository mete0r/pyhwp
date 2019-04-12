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

import logging

from six import with_metaclass

from hwp5.dataio import StructType
from hwp5.dataio import Struct
from hwp5.dataio import Enum
from hwp5.dataio import Flags
from hwp5.dataio import PrimitiveType
from hwp5.dataio import UINT32
from hwp5.dataio import UINT16
from hwp5.dataio import UINT8
from hwp5.dataio import INT32
from hwp5.dataio import INT8
from hwp5.dataio import BYTE
from hwp5.dataio import HWPUNIT16
from hwp5.dataio import SHWPUNIT
from hwp5.dataio import N_ARRAY


logger = logging.getLogger(__name__)


tag_models = dict()


class RecordModelType(StructType):

    def __new__(mcs, name, bases, attrs):
        cls = StructType.__new__(mcs, name, bases, attrs)
        if 'tagid' in attrs:
            tagid = attrs['tagid']
            assert tagid not in tag_models
            tag_models[tagid] = cls
        return cls


class RecordModel(with_metaclass(RecordModelType, object)):
    pass


class BinStorageId(UINT16):
    pass


class COLORREF(with_metaclass(PrimitiveType, int)):
    binfmt = INT32.binfmt
    never_instantiate = False

    def __getattr__(self, name):
        if name == 'r':
            return self & 0xff
        elif name == 'g':
            return (self & 0xff00) >> 8
        elif name == 'b':
            return (self & 0xff0000) >> 16
        elif name == 'a':
            return int((self & 0xff000000) >> 24)
        elif name == 'rgb':
            return self.r, self.g, self.b

    def __str__(self):
        return '#%02x%02x%02x' % (self.r, self.g, self.b)

    def __repr__(self):
        class_name = self.__class__.__name__
        value = '(0x%02x, 0x%02x, 0x%02x)' % self.rgb
        return class_name + value


class Margin(Struct):
    def attributes():
        yield HWPUNIT16, 'left'
        yield HWPUNIT16, 'right'
        yield HWPUNIT16, 'top'
        yield HWPUNIT16, 'bottom'
    attributes = staticmethod(attributes)


class Coord(Struct):
    def attributes():
        yield SHWPUNIT, 'x'
        yield SHWPUNIT, 'y'
    attributes = staticmethod(attributes)


class Border(Struct):

    # 표 20 테두리선 종류
    StrokeEnum = Enum('none', 'solid',
                      'dashed', 'dotted', 'dash-dot', 'dash-dot-dot',
                      'long-dash', 'large-dot',
                      'double', 'double-2', 'double-3', 'triple',
                      'wave', 'double-wave',
                      'inset', 'outset', 'groove', 'ridge')
    StrokeType = Flags(UINT8,
                       0, 4, StrokeEnum, 'stroke_type')

    # 표 21 테두리선 굵기
    widths = {'0.1mm': 0,
              '0.12mm': 1,
              '0.15mm': 2,
              '0.2mm': 3,
              '0.25mm': 4,
              '0.3mm': 5,
              '0.4mm': 6,
              '0.5mm': 7,
              '0.6mm': 8,
              '0.7mm': 9,
              '1.0mm': 10,
              '1.5mm': 11,
              '2.0mm': 12,
              '3.0mm': 13,
              '4.0mm': 14,
              '5.0mm': 15}
    WidthEnum = Enum(**widths)
    Width = Flags(UINT8,
                  0, 4, WidthEnum, 'width')

    def attributes(cls):
        yield cls.StrokeType, 'stroke_flags',
        yield cls.Width, 'width_flags',
        yield COLORREF, 'color',
    attributes = classmethod(attributes)


class BorderLine(Struct):
    ''' 표 81 테두리 선 정보 '''

    LineEnd = Enum('round', 'flat')
    ArrowShape = Enum('none', 'arrow', 'arrow2', 'diamond', 'circle', 'rect',
                      'diamondfilled', 'disc', 'rectfilled')
    ArrowSize = Enum('smallest', 'smaller', 'small', 'abitsmall', 'normal',
                     'abitlarge', 'large', 'larger', 'largest')

    ''' 표 82 테두리 선 정보 속성 '''
    Flags = Flags(UINT32,
                  0, 5, Border.StrokeEnum, 'stroke',
                  6, 9, LineEnd, 'line_end',
                  10, 15, ArrowShape, 'arrow_start',
                  16, 21, ArrowShape, 'arrow_end',
                  22, 25, ArrowSize, 'arrow_start_size',
                  26, 29, ArrowSize, 'arrow_end_size',
                  30, 'arrow_start_fill',
                  31, 'arrow_end_fill')

    def attributes(cls):
        yield COLORREF, 'color'
        yield INT32, 'width'
        yield cls.Flags, 'flags'
    attributes = classmethod(attributes)


class Fill(Struct):
    pass


class FillNone(Fill):
    def attributes():
        yield UINT32, 'size',  # SPEC is confusing
    attributes = staticmethod(attributes)


class FillColorPattern(Fill):
    ''' 표 23 채우기 정보 '''
    PatternTypeEnum = Enum(NONE=255, HORIZONTAL=0, VERTICAL=1, BACKSLASH=2,
                           SLASH=3, GRID=4, CROSS=5)
    PatternTypeFlags = Flags(UINT32,
                             0, 7, PatternTypeEnum, 'pattern_type')

    def attributes(cls):
        yield COLORREF, 'background_color',
        yield COLORREF, 'pattern_color',
        yield cls.PatternTypeFlags, 'pattern_type_flags',
    attributes = classmethod(attributes)


class FillImage(Fill):
    FillImageEnum = Enum(TILE_ALL=0,
                         TILE_HORIZONTAL_TOP=1,
                         TILE_HORIZONTAL_BOTTOM=2,
                         TILE_VERTICAL_LEFT=3,
                         TILE_VERTICAL_RIGHT=4,
                         RESIZE=5,
                         CENTER=6,
                         CENTER_TOP=7,
                         CENTER_BOTTOM=8,
                         LEFT_MIDDLE=9,
                         LEFT_TOP=10,
                         LEFT_BOTTOM=11,
                         RIGHT_MIDDLE=12,
                         RIGHT_TOP=13,
                         RIGHT_BOTTOM=14,
                         NONE=15)
    FillImageFlags = Flags(BYTE,
                           0, 16, FillImageEnum, 'fillimage_type')

    EffectEnum = Enum(REAL_PIC=0,
                      GRAY_SCALE=1,
                      BLACK_WHITE=2,
                      PATTERN8x8=3)
    EffectFlags = Flags(UINT8,
                        0, 8, EffectEnum, 'effect_type')

    def attributes(cls):
        yield cls.FillImageFlags, 'flags'
        yield INT8, 'brightness'
        yield INT8, 'contrast'
        yield cls.EffectFlags, 'effect'
        yield UINT16, 'bindata_id'
    attributes = classmethod(attributes)


class Coord32(Struct):
    def attributes():
        yield UINT32, 'x'
        yield UINT32, 'y'
    attributes = staticmethod(attributes)


GradationTypeEnum = Enum(LINEAR=1, CIRCULAR=2, CONICAL=3, RECTANGULAR=4)
GradationTypeFlags = Flags(BYTE,
                           0, 8, GradationTypeEnum, 'gradation_type')


class FillGradation(Fill):
    def attributes():
        yield GradationTypeFlags, 'type',
        yield UINT32, 'shear',  # 기울임 각 (도)
        yield Coord32, 'center',
        yield UINT32, 'blur',  # 번짐 정도: 0-100
        # TODO: 스펙 1.2에 따르면 색상 수 > 2인 경우
        # 색상이 바뀌는 위치 배열이 온다고 함
        yield N_ARRAY(UINT32, COLORREF), 'colors',
    attributes = staticmethod(attributes)


def ref_parent_member(member_name):
    def f(context, values):
        context, model = context['parent']
        return model['content'][member_name]
    f.__doc__ = 'PARENTREC.' + member_name
    return f
