# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010 mete0r@sarangbang.or.kr
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
import unohelper


class Base(unohelper.Base):

    def __init__(self, context):
        self.context = context


def component_context(f):
    import unokit.contexts
    def wrapper(self, *args, **kwargs):
        unokit.contexts.push(self.context)
        try:
            return f(self, *args, **kwargs)
        finally:
            unokit.contexts.pop()
    return wrapper
