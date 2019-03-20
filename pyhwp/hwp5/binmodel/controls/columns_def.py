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

from hwp5.binmodel.controlchar import CHID
from hwp5.dataio import Enum
from hwp5.dataio import Flags
from hwp5.dataio import Struct
from hwp5.dataio import UINT16
from hwp5.dataio import WORD
from hwp5.dataio import HWPUNIT16
from hwp5.dataio import X_ARRAY
from hwp5.dataio import ref_member_flag
from hwp5.binmodel.controls._shared import Control
from hwp5.binmodel._shared import Border


class Column0(Struct):

    @staticmethod
    def attributes():
        yield WORD, 'width'


class Column(Struct):
    @staticmethod
    def attributes():
        yield WORD, 'spacing'
        yield WORD, 'width'


class ColumnsDef(Control):
    ''' 4.2.10.2. 단 정의 '''
    chid = CHID.COLD

    Kind = Enum('normal', 'distribute', 'parallel')
    Direction = Enum('l2r', 'r2l', 'both')
    Flags = Flags(UINT16,
                  0, 1, Kind, 'kind',
                  2, 9, 'count',
                  10, 11, Direction, 'direction',
                  12, 'same_widths')

    def attributes(cls):
        yield cls.Flags, 'flags'
        yield HWPUNIT16, 'spacing'

        def not_same_widths(context, values):
            ''' flags.same_widths == 0 '''
            return not values['flags'].same_widths

        def n_entries(member_ref):
            def n_entries(context, values):
                n_columns = member_ref(context, values)
                return n_columns - 1
            return n_entries

        yield dict(name='column0', type=Column0,
                   condition=not_same_widths)
        yield dict(name='columns',
                   type=X_ARRAY(Column,
                                n_entries(ref_member_flag('flags', 'count'))),
                   condition=not_same_widths)
        yield UINT16, 'attr2'
        yield Border, 'splitter'
    attributes = classmethod(attributes)
