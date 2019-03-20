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
from hwp5.tagids import HWPTAG_STYLE
from hwp5.dataio import Enum
from hwp5.dataio import Flags
from hwp5.dataio import BYTE
from hwp5.dataio import BSTR
from hwp5.dataio import INT16
from hwp5.dataio import UINT16


class Style(RecordModel):
    ''' 4.1.11. 스타일 '''
    tagid = HWPTAG_STYLE

    # 표 43 스타일 종류
    Kind = Enum(PARAGRAPH=0, CHAR=1)
    Flags = Flags(BYTE,
                  0, 1, Kind, 'kind')

    def attributes(cls):
        ''' 표 42 스타일 '''
        yield BSTR, 'local_name',
        yield BSTR, 'name',
        yield cls.Flags, 'flags',
        yield BYTE, 'next_style_id',
        yield INT16, 'lang_id',
        yield UINT16, 'parashape_id',
        yield UINT16, 'charshape_id',

        # unknown fields
        # following fields are found from 5.0.0.0
        yield UINT16, 'unknown'
    attributes = classmethod(attributes)
