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
from hwp5.tagids import HWPTAG_PAGE_DEF
from hwp5.dataio import Enum
from hwp5.dataio import Flags
from hwp5.dataio import UINT32
from hwp5.dataio import HWPUNIT


class PageDef(RecordModel):
    tagid = HWPTAG_PAGE_DEF
    Orientation = Enum(PORTRAIT=0, LANDSCAPE=1)
    BookBinding = Enum(LEFT=0, RIGHT=1, TOP=2, BOTTOM=3)
    Flags = Flags(UINT32,
                  0, Orientation, 'orientation',
                  1, 2, BookBinding, 'bookbinding')

    def attributes(cls):
        yield HWPUNIT, 'width',
        yield HWPUNIT, 'height',
        yield HWPUNIT, 'left_offset',
        yield HWPUNIT, 'right_offset',
        yield HWPUNIT, 'top_offset',
        yield HWPUNIT, 'bottom_offset',
        yield HWPUNIT, 'header_offset',
        yield HWPUNIT, 'footer_offset',
        yield HWPUNIT, 'bookbinding_offset',
        yield cls.Flags, 'attr',
        # yield UINT32, 'attr',
    attributes = classmethod(attributes)

    def getDimension(self):
        width = HWPUNIT(self.paper_width - self.offsetLeft - self.offsetRight)
        height = HWPUNIT(self.paper_height
                         - (self.offsetTop + self.offsetHeader)
                         - (self.offsetBottom + self.offsetFooter))
        if self.attr.landscape:
            return (height, width)
        else:
            return (width, height)
    dimension = property(getDimension)

    def getHeight(self):
        if self.attr.landscape:
            width = HWPUNIT(self.paper_width - self.offsetLeft -
                            self.offsetRight)
            return width
        else:
            height = HWPUNIT(self.paper_height
                             - (self.offsetTop + self.offsetHeader)
                             - (self.offsetBottom + self.offsetFooter))
            return height
    height = property(getHeight)

    def getWidth(self):
        if self.attr.landscape:
            height = HWPUNIT(self.paper_height
                             - (self.offsetTop + self.offsetHeader)
                             - (self.offsetBottom + self.offsetFooter))
            return height
        else:
            width = HWPUNIT(self.paper_width - self.offsetLeft -
                            self.offsetRight)
            return width
    width = property(getWidth)
