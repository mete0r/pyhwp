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

from hwp5.binmodel.controls.common_controls import CommonControl
from hwp5.binmodel.controlchar import CHID
from hwp5.binmodel.tagid61_table import TableBody


class TableControl(CommonControl):
    chid = CHID.TBL

    def on_child(cls, attributes, context, child):
        child_context, child_model = child
        if child_model['type'] is TableBody:
            # referenced in ListHeader parsing
            context['seen_table_body'] = True
    on_child = classmethod(on_child)
