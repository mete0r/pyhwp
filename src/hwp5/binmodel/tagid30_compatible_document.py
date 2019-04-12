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
from hwp5.tagids import HWPTAG_COMPATIBLE_DOCUMENT
from hwp5.dataio import Enum
from hwp5.dataio import Flags
from hwp5.dataio import UINT32


class CompatibleDocument(RecordModel):
    ''' 4.1.14. 호환 문서 '''
    tagid = HWPTAG_COMPATIBLE_DOCUMENT

    # 표 50 대상 프로그램
    Target = Enum(DEFAULT=0, HWP2007=1, MSWORD=2)
    Flags = Flags(UINT32,
                  0, 1, 'target')

    def attributes(cls):
        ''' 표 49 호환 문서 '''
        yield cls.Flags, 'flags'
    attributes = classmethod(attributes)
