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

from six import with_metaclass

from hwp5.binmodel._shared import RecordModel
from hwp5.tagids import HWPTAG_PARA_CHAR_SHAPE
from hwp5.dataio import ArrayType
from hwp5.dataio import X_ARRAY
from hwp5.dataio import ARRAY
from hwp5.dataio import UINT32
from hwp5.dataio import UINT16
from hwp5.binmodel._shared import ref_parent_member


class ParaCharShape(RecordModel):
    ''' 4.2.3. 문단의 글자 모양 '''
    tagid = HWPTAG_PARA_CHAR_SHAPE

    def attributes():
        ''' 표 56 문단의 글자 모양 '''
        yield dict(name='charshapes',
                   type=X_ARRAY(ARRAY(UINT32, 2),
                                ref_parent_member('charshapes')))
    attributes = staticmethod(attributes)


class ParaCharShapeList(with_metaclass(ArrayType, list)):

    itemtype = ARRAY(UINT16, 2)

    def read(cls, f, context):
        bytes = f.read()
        return cls.decode(bytes, context)
    read = classmethod(read)

    def decode(payload, context=None):
        import struct
        fmt = 'II'
        unitsize = struct.calcsize('<' + fmt)
        unitcount = len(payload) / unitsize
        values = struct.unpack('<' + (fmt * unitcount), payload)
        return list(tuple(values[i * 2:i * 2 + 2])
                    for i in range(0, unitcount))
    decode = staticmethod(decode)
