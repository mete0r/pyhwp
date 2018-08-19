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
import io
import os.path


class FileSystemStorage(object):
    ''' Directory-based stroage. '''

    def __init__(self, path):
        self.path = path

    def __iter__(self):
        return iter(sorted(os.listdir(self.path)))

    def __getitem__(self, name):
        path = os.path.join(self.path, name)
        if os.path.isdir(path):
            return FileSystemStorage(path)
        elif os.path.exists(path):
            return FileSystemStream(path)
        else:
            raise KeyError(name)


class FileSystemStream(object):
    ''' File-based stream. '''

    def __init__(self, path):
        self.path = path

    def open(self):
        return io.open(self.path, 'rb')
