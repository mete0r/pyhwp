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


HWPTAG_BEGIN = 0x010
tagnames = {
    # DocInfo Records
    HWPTAG_BEGIN + 0: 'HWPTAG_DOCUMENT_PROPERTIES',
    HWPTAG_BEGIN + 1: 'HWPTAG_ID_MAPPINGS',
    HWPTAG_BEGIN + 2: 'HWPTAG_BIN_DATA',
    HWPTAG_BEGIN + 3: 'HWPTAG_FACE_NAME',
    HWPTAG_BEGIN + 4: 'HWPTAG_BORDER_FILL',
    HWPTAG_BEGIN + 5: 'HWPTAG_CHAR_SHAPE',
    HWPTAG_BEGIN + 6: 'HWPTAG_TAB_DEF',
    HWPTAG_BEGIN + 7: 'HWPTAG_NUMBERING',
    HWPTAG_BEGIN + 8: 'HWPTAG_BULLET',
    HWPTAG_BEGIN + 9: 'HWPTAG_PARA_SHAPE',
    HWPTAG_BEGIN + 10: 'HWPTAG_STYLE',
    HWPTAG_BEGIN + 11: 'HWPTAG_DOC_DATA',
    HWPTAG_BEGIN + 12: 'HWPTAG_DISTRIBUTE_DOC_DATA',
    # HWPTAG_BEGIN + 13: RESERVED,
    HWPTAG_BEGIN + 14: 'HWPTAG_COMPATIBLE_DOCUMENT',
    HWPTAG_BEGIN + 15: 'HWPTAG_LAYOUT_COMPATIBILITY',
    HWPTAG_BEGIN + 16: 'HWPTAG_BEGIN_PLUS_16',

    # Section Records
    HWPTAG_BEGIN + 50: 'HWPTAG_PARA_HEADER',
    HWPTAG_BEGIN + 51: 'HWPTAG_PARA_TEXT',
    HWPTAG_BEGIN + 52: 'HWPTAG_PARA_CHAR_SHAPE',
    HWPTAG_BEGIN + 53: 'HWPTAG_PARA_LINE_SEG',
    HWPTAG_BEGIN + 54: 'HWPTAG_PARA_RANGE_TAG',
    HWPTAG_BEGIN + 55: 'HWPTAG_CTRL_HEADER',
    HWPTAG_BEGIN + 56: 'HWPTAG_LIST_HEADER',
    HWPTAG_BEGIN + 57: 'HWPTAG_PAGE_DEF',
    HWPTAG_BEGIN + 58: 'HWPTAG_FOOTNOTE_SHAPE',
    HWPTAG_BEGIN + 59: 'HWPTAG_PAGE_BORDER_FILL',
    HWPTAG_BEGIN + 60: 'HWPTAG_SHAPE_COMPONENT',
    HWPTAG_BEGIN + 61: 'HWPTAG_TABLE',
    HWPTAG_BEGIN + 62: 'HWPTAG_SHAPE_COMPONENT_LINE',
    HWPTAG_BEGIN + 63: 'HWPTAG_SHAPE_COMPONENT_RECTANGLE',
    HWPTAG_BEGIN + 64: 'HWPTAG_SHAPE_COMPONENT_ELLIPSE',
    HWPTAG_BEGIN + 65: 'HWPTAG_SHAPE_COMPONENT_ARC',
    HWPTAG_BEGIN + 66: 'HWPTAG_SHAPE_COMPONENT_POLYGON',
    HWPTAG_BEGIN + 67: 'HWPTAG_SHAPE_COMPONENT_CURVE',
    HWPTAG_BEGIN + 68: 'HWPTAG_SHAPE_COMPONENT_OLE',
    HWPTAG_BEGIN + 69: 'HWPTAG_SHAPE_COMPONENT_PICTURE',
    HWPTAG_BEGIN + 70: 'HWPTAG_SHAPE_COMPONENT_CONTAINER',
    HWPTAG_BEGIN + 71: 'HWPTAG_CTRL_DATA',
    HWPTAG_BEGIN + 72: 'HWPTAG_CTRL_EQEDIT',
    # HWPTAG_BEGIN + 73: RESERVED
    HWPTAG_BEGIN + 74: 'HWPTAG_SHAPE_COMPONENT_TEXTART',
    HWPTAG_BEGIN + 75: 'HWPTAG_FORM_OBJECT',
    HWPTAG_BEGIN + 76: 'HWPTAG_MEMO_SHAPE',
    HWPTAG_BEGIN + 77: 'HWPTAG_MEMO_LIST',
    HWPTAG_BEGIN + 78: 'HWPTAG_FORBIDDEN_CHAR',
    HWPTAG_BEGIN + 79: 'HWPTAG_CHART_DATA',
    # ...
    HWPTAG_BEGIN + 99: 'HWPTAG_SHAPE_COMPONENT_UNKNOWN',
}
for k, v in tagnames.items():
    globals()[v] = k
del k, v
