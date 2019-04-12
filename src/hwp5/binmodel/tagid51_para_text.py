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
from __future__ import division

from six import with_metaclass

from hwp5.binmodel._shared import RecordModel
from hwp5.tagids import HWPTAG_PARA_TEXT
from hwp5.dataio import ArrayType
from hwp5.binmodel.controlchar import ControlChar


class ParaTextChunks(with_metaclass(ArrayType, list)):

    def read(cls, f):
        bytes = f.read()
        return [x for x in cls.parse_chunks(bytes)]
    read = classmethod(read)

    def parse_chunks(bytes):
        from hwp5.dataio import decode_utf16le_with_hypua
        size = len(bytes)
        idx = 0
        while idx < size:
            ctrlpos, ctrlpos_end = ControlChar.find(bytes, idx)
            if idx < ctrlpos:
                text = decode_utf16le_with_hypua(bytes[idx:ctrlpos])
                yield (idx // 2, ctrlpos // 2), text
            if ctrlpos < ctrlpos_end:
                cch = ControlChar.decode(bytes[ctrlpos:ctrlpos_end])
                yield (ctrlpos // 2, ctrlpos_end // 2), cch
            idx = ctrlpos_end
    parse_chunks = staticmethod(parse_chunks)


class ParaText(RecordModel):
    ''' 4.2.2. 문단의 텍스트 '''
    tagid = HWPTAG_PARA_TEXT

    def attributes():
        yield ParaTextChunks, 'chunks'
    attributes = staticmethod(attributes)
