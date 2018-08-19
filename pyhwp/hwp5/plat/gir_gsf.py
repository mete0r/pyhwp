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

from ..errors import InvalidOleStorageError


try:
    bytes
except NameError:
    bytes = str


logger = logging.getLogger(__name__)


def is_enabled():
    try:
        from gi.repository import Gsf
    except Exception:
        return False
    else:
        Gsf
        return True


def open(path):
    from gi.repository.Gsf import InputGio
    from gi.repository.Gsf import InfileMSOle

    inp = InputGio.new_for_path(path)
    return InfileMSOle.new(inp)


def listdir(gsfole):
    for i in xrange(gsfole.num_children()):
        yield gsfole.name_by_index(i)


class OleStorage:

    def __init__(self, gsfole):
        from gi.repository.Gsf import Input
        from gi.repository.Gsf import InfileMSOle

        if isinstance(gsfole, InfileMSOle):
            self.gsfole = gsfole
        elif isinstance(gsfole, Input):
            try:
                self.gsfole = InfileMSOle.new(gsfole)
            except Exception:
                raise InvalidOleStorageError()
        else:
            try:
                self.gsfole = open(gsfole)
            except Exception:
                raise InvalidOleStorageError()

    def __iter__(self):
        return listdir(self.gsfole)

    def __getitem__(self, name):
        child = self.gsfole.child_by_name(name)
        if child:
            if child.num_children() == -1:
                return OleStreamItem(self.gsfole, name)
            else:
                return OleStorage(child)
        else:
            raise KeyError(name)

    def close(self):
        del self.gsfole


class OleStreamItem:

    def __init__(self, parent, name):
        self.__parent = parent
        self.__name = name

    def open(self):
        gsfole = self.__parent.child_by_name(self.__name)
        if gsfole:
            return OleStream(gsfole)
        else:
            raise IOError(self.__name)


class OleStream:

    def __init__(self, gsfole):
        self.gsfole = gsfole

    def close(self):
        pass

    def read(self, size=None):
        pos = self.gsfole.tell()
        totalsize = self.gsfole.size
        if size is not None:
            if pos + size > totalsize:
                size = totalsize - pos
        else:
            size = totalsize - pos

        if size > 0:
            return self.gsfole.read(size)
        return bytes()

    def seek(self, offset, whence=0):
        from gi.repository.GLib import SeekType
        if whence == 0:
            whence = SeekType.SET
        elif whence == 1:
            whence = SeekType.CUR
        elif whence == 2:
            whence = SeekType.END
        else:
            raise ValueError(whence)

        self.gsfole.seek(offset, whence)

    def tell(self):
        return self.gsfole.tell()
