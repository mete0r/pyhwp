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
from hwp5.tagids import HWPTAG_ID_MAPPINGS
from hwp5.dataio import UINT32


class IdMappings(RecordModel):
    tagid = HWPTAG_ID_MAPPINGS

    def attributes():
        yield UINT32, 'bindata',
        yield UINT32, 'ko_fonts',
        yield UINT32, 'en_fonts',
        yield UINT32, 'cn_fonts',
        yield UINT32, 'jp_fonts',
        yield UINT32, 'other_fonts',
        yield UINT32, 'symbol_fonts',
        yield UINT32, 'user_fonts',
        yield UINT32, 'borderfills',
        yield UINT32, 'charshapes',
        yield UINT32, 'tabdefs',
        yield UINT32, 'numberings',
        yield UINT32, 'bullets',
        yield UINT32, 'parashapes',
        yield UINT32, 'styles',
        # TODO: memoshapes does not exist at least 5.0.1.6
        yield dict(type=UINT32, name='memoshapes', version=(5, 0, 1, 7))
    attributes = staticmethod(attributes)
