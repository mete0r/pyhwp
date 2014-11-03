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
from hwp5.tagids import HWPTAG_PARA_LINE_SEG
from hwp5.binmodel._shared import ref_parent_member
from hwp5.dataio import ArrayType
from hwp5.dataio import Struct
from hwp5.dataio import UINT16
from hwp5.dataio import Flags
from hwp5.dataio import SHWPUNIT
from hwp5.dataio import INT32
from hwp5.dataio import X_ARRAY


class LineSeg(Struct):
    Flags = Flags(UINT16,
                  4, 'indented')

    def attributes(cls):
        yield INT32, 'chpos',
        yield SHWPUNIT, 'y',
        yield SHWPUNIT, 'height',
        yield SHWPUNIT, 'height2',
        yield SHWPUNIT, 'height85',
        yield SHWPUNIT, 'space_below',
        yield SHWPUNIT, 'x',
        yield SHWPUNIT, 'width'
        yield UINT16, 'a8'
        yield cls.Flags, 'flags'
    attributes = classmethod(attributes)


class ParaLineSeg(RecordModel):
    ''' 4.2.4. 문단의 레이아웃 '''

    tagid = HWPTAG_PARA_LINE_SEG

    def attributes(cls):
        ''' 표 57 문단의 레이아웃 '''
        yield dict(name='linesegs',
                   type=X_ARRAY(LineSeg, ref_parent_member('linesegs')))
    attributes = classmethod(attributes)


class ParaLineSegList(list):
    __metaclass__ = ArrayType
    itemtype = LineSeg

    def read(cls, f, context):
        payload = context['stream'].read()
        return cls.decode(context, payload)
    read = classmethod(read)

    def decode(cls, context, payload):
        from itertools import izip
        import struct
        unitfmt = 'iiiiiiiiHH'
        unitsize = struct.calcsize('<' + unitfmt)
        unitcount = len(payload) / unitsize
        values = struct.unpack('<' + unitfmt * unitcount, payload)
        names = ['chpos', 'y', 'height', 'height2', 'height85', 'space_below',
                 'x', 'width', 'a8', 'flags']
        x = list(dict(izip(names, tuple(values[i * 10:i * 10 + 10])))
                 for i in range(0, unitcount))
        for d in x:
            d['flags'] = LineSeg.Flags(d['flags'])
        return x
    decode = classmethod(decode)
