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
from hwp5.tagids import HWPTAG_SHAPE_COMPONENT_OLE
from hwp5.dataio import Flags
from hwp5.dataio import UINT32
from hwp5.dataio import INT32
from hwp5.binmodel._shared import BinStorageId
from hwp5.binmodel._shared import BorderLine


class ShapeOLE(RecordModel):
    ''' 4.2.9.5 OLE 개체 '''

    tagid = HWPTAG_SHAPE_COMPONENT_OLE

    Flags = Flags(UINT32,
                  0, 7, 'dvaspect',
                  8, 'moniker',
                  # baseline:
                  #  0 means defaut (85%)
                  #  1 means 0%
                  #  101 means 100%
                  9, 15, 'baseline')

    @classmethod
    def attributes(cls):
        yield cls.Flags, 'flags'
        yield INT32, 'extent_x'
        yield INT32, 'extent_y'
        yield BinStorageId, 'storage_id'
        yield BorderLine, 'border'
