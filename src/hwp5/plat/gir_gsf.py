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

from zope.interface import implementer

from ..errors import ImplementationNotAvailable
from ..errors import InvalidOleStorageError
from ..interfaces import IStorage
from ..interfaces import IStorageOpener
from ..interfaces import IStorageStreamNode
from ..interfaces import IStorageDirectoryNode


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


def createStorageOpener(registry, **settings):
    try:
        from gi.repository.Gsf import InputGio
        from gi.repository.Gsf import InfileMSOle
        from gi.repository.GLib import Error as GLibError
    except ImportError:
        raise ImplementationNotAvailable('storage/gir_gsf')

    return OleStorageOpener(InputGio, InfileMSOle, GLibError)


@implementer(IStorageOpener)
class OleStorageOpener:

    def __init__(self, InputGio, InfileMSOle, GLibError):
        self.InputGio = InputGio
        self.InfileMSOle = InfileMSOle
        self.GLibError = GLibError

    def is_storage(self, path):
        try:
            self.open_storage(path)
        except Exception:
            return False
        else:
            return True

    def open_storage(self, path):
        inp = self.InputGio.new_for_path(path)
        try:
            return self.InfileMSOle.new(inp)
        except self.GLibError as e:
            if e.message == 'No OLE2 signature':
                raise InvalidOleStorageError()
            raise


@implementer(IStorageDirectoryNode)
class OleStorageDirectory:

    def __init__(self, gsfole):
        self.gsfole = gsfole

    def __iter__(self):
        return listdir(self.gsfole)

    def __getitem__(self, name):
        child = self.gsfole.child_by_name(name)
        if child is not None:
            if child.num_children() == -1:
                node = OleStreamItem(self.gsfole, name)
            else:
                node = OleStorageDirectory(child)
            node.__name__ = name
            node.__parent__ = self
            return node
        else:
            raise KeyError(name)


@implementer(IStorage)
class OleStorage(OleStorageDirectory):

    __parent__ = None
    __name__ = ''

    def __init__(self, gsfole):
        from gi.repository.Gsf import InfileMSOle

        if not isinstance(gsfole, InfileMSOle):
            raise TypeError()

    def close(self):
        del self.gsfole


@implementer(IStorageStreamNode)
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
