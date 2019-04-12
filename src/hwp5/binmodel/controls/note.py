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
from hwp5.dataio import UINT32
from hwp5.dataio import UINT16
from hwp5.binmodel.controls._shared import Control


class Note(Control):
    ''' 4.2.10.4 미주/각주 '''
    def attributes():
        yield UINT32, 'number'
        yield UINT32, 'unknown0'
        yield UINT32, 'unknown1'
        yield dict(type=UINT16, name='unknown2', version=(5, 0, 3, 0))
        yield dict(type=UINT16, name='unknown3', version=(5, 0, 3, 0))
    attributes = staticmethod(attributes)


class FootNote(Note):
    ''' 각주 '''
    chid = CHID.FN


class EndNote(Note):
    ''' 미주 '''
    chid = CHID.EN
