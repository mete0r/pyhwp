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
from hwp5.tagids import HWPTAG_BORDER_FILL
from hwp5.dataio import UINT32
from hwp5.dataio import UINT16
from hwp5.dataio import BYTE
from hwp5.dataio import Flags
from hwp5.binmodel._shared import Border
from hwp5.binmodel._shared import FillColorPattern
from hwp5.binmodel._shared import FillGradation
from hwp5.binmodel._shared import FillImage


class BorderFill(RecordModel):
    ''' 4.1.5. 테두리/배경 '''

    tagid = HWPTAG_BORDER_FILL

    # 표 19 테두리/배경 속성
    BorderFlags = Flags(UINT16,
                        0, 'effect_3d',
                        1, 'effect_shadow',
                        2, 4, 'slash',
                        5, 6, 'backslash')

    # 표 23 채우기 정보
    FillFlags = Flags(UINT32,
                      0, 'colorpattern',
                      1, 'image',
                      2, 'gradation')

    def attributes(cls):
        ''' 표 18 테두리/배경 속성 '''
        yield cls.BorderFlags, 'borderflags'
        yield Border, 'left',
        yield Border, 'right',
        yield Border, 'top',
        yield Border, 'bottom',
        yield Border, 'diagonal'
        yield cls.FillFlags, 'fillflags'

        def fill_colorpattern(context, values):
            ''' fillflags.fill_colorpattern '''
            return values['fillflags'].colorpattern

        def fill_image(context, values):
            ''' fillflags.fill_image '''
            return values['fillflags'].image

        def fill_gradation(context, values):
            ''' fillflags.fill_gradation '''
            return values['fillflags'].gradation

        yield dict(type=FillColorPattern, name='fill_colorpattern',
                   condition=fill_colorpattern)
        yield dict(type=FillGradation, name='fill_gradation',
                   condition=fill_gradation)
        yield dict(type=FillImage, name='fill_image',
                   condition=fill_image)
        yield UINT32, 'shape'
        yield dict(type=BYTE, name='blur_center',
                   condition=fill_gradation)
    attributes = classmethod(attributes)
