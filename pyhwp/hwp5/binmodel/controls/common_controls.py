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

from hwp5.binmodel.controls._shared import Control
from hwp5.dataio import Enum
from hwp5.dataio import Flags
from hwp5.dataio import UINT32
from hwp5.dataio import SHWPUNIT
from hwp5.dataio import HWPUNIT
from hwp5.dataio import INT16
from hwp5.dataio import BSTR
from hwp5.binmodel._shared import Margin


class CommonControl(Control):

    # 표 65 개체 공통 속성의 속성
    Flow = Enum(FLOAT=0, BLOCK=1, BACK=2, FRONT=3)
    TextSide = Enum(BOTH=0, LEFT=1, RIGHT=2, LARGER=3)
    VRelTo = Enum(PAPER=0, PAGE=1, PARAGRAPH=2)
    HRelTo = Enum(PAPER=0, PAGE=1, COLUMN=2, PARAGRAPH=3)
    VAlign = Enum(TOP=0, MIDDLE=1, BOTTOM=2)
    HAlign = Enum(LEFT=0, CENTER=1, RIGHT=2, INSIDE=3, OUTSIDE=4)
    WidthRelTo = Enum(PAPER=0, PAGE=1, COLUMN=2, PARAGRAPH=3, ABSOLUTE=4)
    HeightRelTo = Enum(PAPER=0, PAGE=1, ABSOLUTE=2)
    NumberCategory = Enum(NONE=0, FIGURE=1, TABLE=2, EQUATION=3)

    CommonControlFlags = Flags(UINT32,
                               0, 'inline',
                               2, 'affect_line_spacing',
                               3, 4, VRelTo, 'vrelto',
                               5, 7, VAlign, 'valign',
                               8, 9, HRelTo, 'hrelto',
                               10, 12, HAlign, 'halign',
                               13, 'restrict_in_page',
                               14, 'overlap_others',
                               15, 17, WidthRelTo, 'width_relto',
                               18, 19, HeightRelTo, 'height_relto',
                               20, 'protect_size_when_vrelto_paragraph',
                               21, 23, Flow, 'flow',
                               24, 25, TextSide, 'text_side',
                               26, 27, NumberCategory, 'number_category')

    MARGIN_LEFT = 0
    MARGIN_RIGHT = 1
    MARGIN_TOP = 2
    MARGIN_BOTTOM = 3

    def attributes(cls):
        ''' 표 64 개체 공통 속성 '''
        yield cls.CommonControlFlags, 'flags',
        yield SHWPUNIT, 'y',    # DIFFSPEC
        yield SHWPUNIT, 'x',    # DIFFSPEC
        yield HWPUNIT, 'width',
        yield HWPUNIT, 'height',
        yield INT16, 'z_order',
        yield INT16, 'unknown1',
        yield Margin, 'margin',
        yield UINT32, 'instance_id',
        yield dict(type=INT16, name='unknown2', version=(5, 0, 0, 5))
        yield dict(type=BSTR, name='description', version=(5, 0, 0, 5))
    attributes = classmethod(attributes)
