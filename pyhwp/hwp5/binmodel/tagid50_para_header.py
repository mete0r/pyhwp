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
from hwp5.tagids import HWPTAG_PARA_HEADER
from hwp5.dataio import Flags
from hwp5.dataio import BYTE
from hwp5.dataio import UINT32
from hwp5.dataio import UINT16


class Paragraph(RecordModel):
    ''' 4.2.1. 문단 헤더 '''

    tagid = HWPTAG_PARA_HEADER

    # 표 54 단 나누기 종류
    SplitFlags = Flags(BYTE,
                       0, 'new_section',
                       1, 'new_columnsdef',
                       2, 'new_page',
                       3, 'new_column')
    ControlMask = Flags(UINT32,
                        2, 'unknown1',
                        11, 'control',
                        21, 'new_number')
    Flags = Flags(UINT32,
                  31, 'unknown',
                  0, 30, 'chars')

    def attributes(cls):
        ''' 표 53 문단 헤더 '''
        yield cls.Flags, 'text',
        yield cls.ControlMask, 'controlmask',
        yield UINT16, 'parashape_id',
        yield BYTE, 'style_id',
        yield cls.SplitFlags, 'split',
        yield UINT16, 'charshapes',
        yield UINT16, 'rangetags',
        yield UINT16, 'linesegs',
        yield UINT32, 'instance_id',
    attributes = classmethod(attributes)
