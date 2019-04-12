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
from hwp5.dataio import Flags
from hwp5.dataio import UINT32
from hwp5.dataio import UINT16
from hwp5.dataio import HWPUNIT
from hwp5.dataio import HWPUNIT16
from hwp5.dataio import HexBytes
from hwp5.binmodel.tagid71_ctrl_data import ControlData
from hwp5.binmodel.controls._shared import Control


class SectionDef(Control):
    ''' 4.2.10.1. 구역 정의 '''
    chid = CHID.SECD

    Flags = Flags(UINT32,
                  0, 'hide_header',
                  1, 'hide_footer',
                  2, 'hide_page',
                  3, 'hide_border',
                  4, 'hide_background',
                  5, 'hide_pagenumber',
                  8, 'show_border_on_first_page_only',
                  9, 'show_background_on_first_page_only',
                  16, 18, 'text_direction',
                  19, 'hide_blank_line',
                  20, 21, 'pagenum_on_split_section',
                  22, 'squared_manuscript_paper')

    def attributes(cls):
        yield cls.Flags, 'flags',
        yield HWPUNIT16, 'columnspacing',
        yield HWPUNIT16, 'grid_vertical',
        yield HWPUNIT16, 'grid_horizontal',
        yield HWPUNIT, 'defaultTabStops',
        yield UINT16, 'numbering_shape_id',
        yield UINT16, 'starting_pagenum',
        yield UINT16, 'starting_picturenum',
        yield UINT16, 'starting_tablenum',
        yield UINT16, 'starting_equationnum',
        yield dict(type=UINT32, name='unknown1', version=(5, 0, 1, 7))
        yield dict(type=UINT32, name='unknown2', version=(5, 0, 1, 7))
    attributes = classmethod(attributes)


class SectionDefData(ControlData):
    parent_model_type = SectionDef

    def attributes():
        yield HexBytes(280), 'unknown'
    attributes = staticmethod(attributes)
