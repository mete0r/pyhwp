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
from hwp5.tagids import HWPTAG_PARA_SHAPE
from hwp5.dataio import Enum
from hwp5.dataio import Flags
from hwp5.dataio import INT32
from hwp5.dataio import UINT32
from hwp5.dataio import UINT16
from hwp5.dataio import SHWPUNIT
from hwp5.dataio import HWPUNIT16


class ParaShape(RecordModel):
    ''' 4.1.10. 문단 모양 '''
    tagid = HWPTAG_PARA_SHAPE

    # 표 39 문단 모양 속성1
    LineSpacingType = Enum(RATIO=0, FIXED=1, SPACEONLY=2, MINIMUM=3)
    Align = Enum(BOTH=0, LEFT=1, RIGHT=2, CENTER=3, DISTRIBUTE=4,
                 DISTRIBUTE_SPACE=5)
    VAlign = Enum(FONT=0, TOP=1, CENTER=2, BOTTOM=3)
    LineBreakAlphabet = Enum(WORD=0, HYPHEN=1, CHAR=2)
    LineBreakHangul = Enum(WORD=0, CHAR=1)
    HeadShape = Enum(NONE=0, OUTLINE=1, NUMBER=2, BULLET=3)
    Flags1 = Flags(UINT32,
                   0, 1, LineSpacingType, 'linespacing_type',
                   2, 4, Align, 'align',
                   5, 6, LineBreakAlphabet, 'linebreak_alphabet',
                   7, LineBreakHangul, 'linebreak_hangul',
                   8, 'use_paper_grid',
                   9, 15, 'minimum_space',  # 공백 최소값
                   16, 'protect_single_line',  # 외톨이줄 보호
                   17, 'with_next_paragraph',  # 다음 문단과 함께
                   18, 'protect',  # 문단 보호
                   19, 'start_new_page',  # 문단 앞에서 항상 쪽 나눔
                   20, 21, VAlign, 'valign',
                   22, 'lineheight_along_fontsize',  # 글꼴에 어울리는 줄 높이
                   23, 24, HeadShape, 'head_shape',  # 문단 머리 모양
                   25, 27, 'level',  # 문단 수준
                   28, 'linked_border',  # 문단 테두리 연결 여부
                   29, 'ignore_margin',  # 문단 여백 무시
                   30, 'tail_shape')  # 문단 꼬리 모양

    # 표 40 문단 모양 속성2
    Flags2 = Flags(UINT32,
                   0, 1, 'in_single_line',
                   2, 3, 'reserved',
                   4, 'autospace_alphabet',
                   5, 'autospace_number')

    # 표 41 줄 간격 종류
    Flags3 = Flags(UINT32,
                   0, 4, LineSpacingType, 'linespacing_type3')

    Flags = Flags1

    def attributes(cls):
        ''' 표 38 문단 모양 '''
        yield cls.Flags, 'parashapeflags',
        yield INT32,  'doubled_margin_left',   # 1/7200 * 2 # DIFFSPEC
        yield INT32,  'doubled_margin_right',  # 1/7200 * 2
        yield SHWPUNIT,  'indent',
        yield INT32,  'doubled_margin_top',    # 1/7200 * 2
        yield INT32,  'doubled_margin_bottom',  # 1/7200 * 2
        yield SHWPUNIT,  'linespacing',
        yield UINT16, 'tabdef_id',
        yield UINT16, 'numbering_bullet_id',
        yield UINT16, 'borderfill_id',
        yield HWPUNIT16,  'border_left',
        yield HWPUNIT16,  'border_right',
        yield HWPUNIT16,  'border_top',
        yield HWPUNIT16,  'border_bottom',
        yield dict(type=cls.Flags2, name='flags2', version=(5, 0, 1, 7))
        # yield cls.Flags3, 'flags3',   # DIFFSPEC
        # yield UINT32, 'lineSpacing',  # DIFFSPEC
    attributes = classmethod(attributes)
