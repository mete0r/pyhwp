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
from hwp5.dataio import BSTR
from hwp5.binmodel.controls._shared import Control


class TCPSControl(Control):
    ''' 4.2.10.12. 글자 겹침 '''
    chid = CHID.TCPS

    def attributes():
        yield BSTR, 'textlength'
        # yield UINT8, 'frameType'
        # yield INT8, 'internalCharacterSize'
        # yield UINT8, 'internalCharacterFold'
        # yield N_ARRAY(UINT8, UINT32), 'characterShapeIds'
    attributes = staticmethod(attributes)
