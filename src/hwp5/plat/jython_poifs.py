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
import os.path
import sys

from zope.interface import implementer

from ..errors import ImplementationNotAvailable
from ..errors import InvalidOleStorageError
from ..interfaces import IStorage
from ..interfaces import IStorageOpener
from ..interfaces import IStorageStreamNode
from ..interfaces import IStorageDirectoryNode


PY3 = sys.version_info.major == 3
if PY3:
    basestring = str


def is_enabled():
    try:
        from org.apache.poi.poifs.filesystem import POIFSFileSystem
        POIFSFileSystem  # silencing
        return True
    except ImportError:
        return False


def createStorageOpener(registry, **settings):
    try:
        from java.io import FileInputStream
        from java.io import IOException
        from org.apache.poi.poifs.filesystem import POIFSFileSystem
    except ImportError:
        raise ImplementationNotAvailable('storage/jython_poifs')
    return OleStorageOpener(
        FileInputStream,
        IOException,
        POIFSFileSystem,
    )


@implementer(IStorageOpener)
class OleStorageOpener:

    def __init__(self, FileInputStream, IOException, POIFSFileSystem):
        self.FileInputStream = FileInputStream
        self.IOException = IOException
        self.POIFSFileSystem = POIFSFileSystem

    def is_storage(self, path):
        pass

    def open_storage(self, path):
        path = os.path.abspath(path)
        fis = self.FileInputStream(path)
        try:
            fs = self.POIFSFileSystem(fis)
        except self.IOException as e:
            raise InvalidOleStorageError(e.getMessage())
        entry = fs.getRoot()
        return OleStorage(entry)


@implementer(IStorageDirectoryNode)
class OleStorageDirectory:

    def __init__(self, entry):
        from org.apache.poi.poifs.filesystem import DirectoryEntry

        if isinstance(entry, DirectoryEntry):
            raise TypeError()
        self.entry = entry

    def __iter__(self):
        return (entry.getName() for entry in self.entry.getEntries())

    def __getitem__(self, name):
        from java.io import FileNotFoundException
        try:
            entry = self.entry.getEntry(name)
        except FileNotFoundException:
            raise KeyError('%s not found' % name)

        if entry.directoryEntry:
            child = OleStorageDirectory(entry)
            child.__name__ = name
            child.__parent__ = self
            return child
        elif entry.documentEntry:
            child = OleStream(entry)
            child.__name__ = name
            child.__parent__ = self
            return child
        else:
            raise KeyError('%s is invalid' % name)


@implementer(IStorage)
class OleStorage(OleStorageDirectory):
    ''' Create an OleStorage instance.

    :param olefile: an OLE2 Compound Binary File.
    :raises: `InvalidOleStorageError` when `olefile` is not valid OLE2 format.
    '''

    __parent__ = None
    __name__ = ''

    def close(self):
        return


@implementer(IStorageStreamNode)
class OleStream(object):

    def __init__(self, entry):
        self.entry = entry

    def open(self):
        from org.apache.poi.poifs.filesystem import DocumentInputStream
        dis = DocumentInputStream(self.entry)
        return FileFromDocumentInputStream(dis)


class FileFromDocumentInputStream(object):

    def __init__(self, dis):
        self.dis = dis
        self.size = dis.available()
        dis.mark(0)

    def read(self, size=None):
        import jarray
        dis = self.dis
        available = dis.available()
        if size is None:
            size = available
        elif size > available:
            size = available
        bytes = jarray.zeros(size, 'b')
        n_read = dis.read(bytes)
        data = bytes.tostring()
        if n_read < size:
            return data[:n_read]
        return data

    def seek(self, offset, whence=0):
        dis = self.dis
        if whence == 0:
            dis.reset()
            dis.skip(offset)
        elif whence == 1:
            dis.skip(offset)
        elif whence == 2:
            dis.reset()
            dis.skip(self.size - offset)
        else:
            raise ValueError('invalid whence: %s', whence)

    def tell(self):
        return self.size - self.dis.available()

    def close(self):
        return self.dis.close()
