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
from hwp5.tagids import HWPTAG_BULLET
from hwp5.dataio import INT32
from hwp5.dataio import UINT32
from hwp5.dataio import UINT16
from hwp5.dataio import HWPUNIT16
from hwp5.dataio import WCHAR
from hwp5.dataio import Enum
from hwp5.dataio import Flags


BulletAlignEnum = Enum(LEFT=0, CENTER=1, RIGHT=2)
BulletFlags = Flags(UINT32,
                    0, 1, BulletAlignEnum, 'align',
                    3, 'auto_indent')


class Bullet(RecordModel):
    ''' 4.1.9. 글머리표 '''

    tagid = HWPTAG_BULLET

    @staticmethod
    def attributes():
        # TODO: Spec 1.2 is insufficient and incorrect
        yield BulletFlags, 'flags',
        yield HWPUNIT16, 'width',  # 너비, 단위: HWPUNIT
        yield UINT16, 'space',  # 본문과의 간격, 단위: %
        yield INT32, 'charshape_id',
        yield WCHAR, 'char'
