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

from zope.interface import implementer

from ..interfaces import IStorage
from ..interfaces import IStorageOpener
from ..interfaces import IStorageStreamNode
from ..interfaces import IStorageDirectoryNode


def createStorageOpener(registry, **settings):
    return FileSystemStorageOpener()


@implementer(IStorageOpener)
class FileSystemStorageOpener:

    def is_storage(self, path):
        return os.path.isdir(path)

    def open_storage(self, path):
        if not self.is_storage(path):
            raise Exception('Not a directory', path)
        return FileSystemStorage(path)


@implementer(IStorageDirectoryNode)
class FileSystemDirectory(object):

    def __init__(self, path):
        self.path = path

    def __iter__(self):
        return iter(sorted(os.listdir(self.path)))

    def __getitem__(self, name):
        path = os.path.join(self.path, name)
        if os.path.isdir(path):
            node = FileSystemDirectory(path)
            node.__name__ = name
            node.__parent__ = self
            return node
        elif os.path.exists(path):
            node = FileSystemStream(path)
            node.__name__ = name
            node.__parent__ = self
            return node
        else:
            raise KeyError(name)


@implementer(IStorage)
class FileSystemStorage(FileSystemDirectory):
    ''' Directory-based stroage. '''

    __parent__ = None
    __name__ = ''

    def close(self):
        pass


@implementer(IStorageStreamNode)
class FileSystemStream(object):
    ''' File-based stream. '''

    def __init__(self, path):
        self.path = path

    def open(self):
        return io.open(self.path, 'rb')
