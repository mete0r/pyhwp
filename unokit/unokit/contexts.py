# -*- coding: utf-8 -*-
#
#                   GNU AFFERO GENERAL PUBLIC LICENSE
#                      Version 3, 19 November 2007
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
import uno
import threading


tls = threading.local()
localcontext = uno.getComponentContext()


def get_stack():
    try:
        return tls.context_stack
    except AttributeError:
        tls.context_stack = []
        return tls.context_stack


def push(context):
    return get_stack().append(context)


def pop():
    return get_stack().pop()


def get_current():
    stack = get_stack()
    if len(stack) == 0:
        return localcontext
    return stack[-1]
