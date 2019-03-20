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
from hwp5.tagids import HWPTAG_CTRL_EQEDIT
from hwp5.dataio import UINT32
from hwp5.dataio import Enum
from hwp5.dataio import Flags


class EqEdit(RecordModel):
    ''' 4.2.9.3. 한글 스크립트 수식 (한글 97 방식 수식) '''
    tagid = HWPTAG_CTRL_EQEDIT

    ScriptScope = Enum(CHAR=0, LINE=1)
    Flags = Flags(UINT32,
                  0, ScriptScope, 'script_scope')

    @classmethod
    def attributes(cls):
        ''' 표 100 수식 개체 속성 '''

        # TODO: followings are not tested against real files
        if False:
            yield
        # yield cls.Flags, 'flags'
        # yield BSTR, 'script'
        # yield HWPUNIT, 'font_size'
        # yield COLORREF, 'color'
        # yield INT16, 'baseline'
