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
import logging

from ..plat import get_olestorage_class


logger = logging.getLogger(__name__)


class OleStorage(object):

    def __init__(self, *args, **kwargs):
        impl_class = get_olestorage_class()
        assert impl_class is not None, 'no OleStorage implementation available'
        self.impl = impl_class(*args, **kwargs)

    def __iter__(self):
        return self.impl.__iter__()

    def __getitem__(self, name):
        return self.impl.__getitem__(name)

    def __getattr__(self, name):
        return getattr(self.impl, name)
