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
from hwp5.tagids import HWPTAG_TABLE
from hwp5.dataio import Enum
from hwp5.dataio import Flags
from hwp5.dataio import UINT32
from hwp5.dataio import UINT16
from hwp5.dataio import HWPUNIT16
from hwp5.dataio import N_ARRAY
from hwp5.dataio import Struct
from hwp5.binmodel._shared import Margin


class ZoneInfo(Struct):
    def attributes():
        yield UINT16, 'starting_column'
        yield UINT16, 'starting_row'
        yield UINT16, 'end_column'
        yield UINT16, 'end_row'
        yield UINT16, 'borderfill_id'
    attributes = staticmethod(attributes)


class TableBody(RecordModel):
    tagid = HWPTAG_TABLE
    Split = Enum(NONE=0, BY_CELL=1, SPLIT=2)
    Flags = Flags(UINT32,
                  0, 1, Split, 'split_page',
                  2, 'repeat_header')

    def attributes(cls):
        from hwp5.dataio import X_ARRAY
        from hwp5.dataio import ref_member
        yield cls.Flags, 'flags'
        yield UINT16, 'rows'
        yield UINT16, 'cols'
        yield HWPUNIT16, 'cellspacing'
        yield Margin, 'padding'
        yield dict(type=X_ARRAY(UINT16, ref_member('rows')),
                   name='rowcols')
        yield UINT16, 'borderfill_id'
        yield dict(type=N_ARRAY(UINT16, ZoneInfo),
                   name='validZones',
                   version=(5, 0, 0, 7))
    attributes = classmethod(attributes)
