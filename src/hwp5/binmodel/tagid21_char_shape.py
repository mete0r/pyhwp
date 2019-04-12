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
from hwp5.tagids import HWPTAG_CHAR_SHAPE
from hwp5.dataio import StructType
from hwp5.dataio import Struct
from hwp5.dataio import Enum
from hwp5.dataio import Flags
from hwp5.dataio import UINT32
from hwp5.dataio import INT32
from hwp5.dataio import INT8
from hwp5.dataio import UINT8
from hwp5.dataio import WORD
from hwp5.binmodel._shared import COLORREF


def LanguageStruct(name, basetype):
    ''' 표 29 글꼴에 대한 언어 '''
    def attributes():
        for lang in ('ko', 'en', 'cn', 'jp', 'other', 'symbol', 'user'):
            yield basetype, lang
    attributes = staticmethod(attributes)
    return StructType(name, (Struct,), dict(basetype=basetype,
                                            attributes=attributes))


class ShadowSpace(Struct):
    def attributes():
        yield INT8, 'x'
        yield INT8, 'y'
    attributes = staticmethod(attributes)


class CharShape(RecordModel):
    ''' 4.1.6. 글자 모양 '''

    tagid = HWPTAG_CHAR_SHAPE

    # 표 30 글자 모양 속성
    Underline = Enum(NONE=0, UNDERLINE=1, LINE_THROUGH=2, OVERLINE=3)
    UnderlineStyle = Enum(SOLID=0, DASHED=1, DOTTED=2, DASH_DOT=3,
                          DASH_DOT_DOT=4, LONG_DASHED=5, LARGE_DOTTED=6,
                          DOUBLE=7, LOWER_WEIGHTED=8, UPPER_WEIGHTED=9,
                          MIDDLE_WEIGHTED=10)
    Flags = Flags(UINT32,
                  0, 'italic',
                  1, 'bold',
                  2, 3, Underline, 'underline',
                  4, 7, UnderlineStyle, 'underline_style',
                  8, 10, 'outline',
                  11, 13, 'shadow')

    def attributes(cls):
        ''' 표 28 글자 모양 '''
        yield LanguageStruct('FontFace', WORD), 'font_face',
        yield (LanguageStruct('LetterWidthExpansion', UINT8),
               'letter_width_expansion')
        yield LanguageStruct('LetterSpacing', INT8), 'letter_spacing'
        yield LanguageStruct('RelativeSize', INT8), 'relative_size'
        yield LanguageStruct('Position', INT8), 'position'
        yield INT32, 'basesize',
        yield cls.Flags, 'charshapeflags',
        yield ShadowSpace, 'shadow_space'
        yield COLORREF, 'text_color',
        yield COLORREF, 'underline_color',
        yield COLORREF, 'shade_color',
        yield COLORREF, 'shadow_color',
        # yield UINT16, 'borderfill_id',        # DIFFSPEC
        # yield COLORREF, 'strikeoutColor',    # DIFFSPEC
    attributes = classmethod(attributes)
