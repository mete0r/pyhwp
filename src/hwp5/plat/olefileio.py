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

from zope.interface import implementer

from ..errors import ImplementationNotAvailable
from ..errors import InvalidOleStorageError
from ..interfaces import IStorage
from ..interfaces import IStorageNode
from ..interfaces import IStorageOpener
from ..interfaces import IStorageStreamNode
from ..interfaces import IStorageDirectoryNode
from ..utils import cached_property


def is_enabled():
    try:
        import olefile  # noqa
    except Exception:
        pass
    else:
        return True

    try:
        import OleFileIO_PL  # noqa
    except ImportError:
        pass
    else:
        return True

    return False


def import_isOleFile():
    try:
        from olefile import isOleFile
    except ImportError:
        pass
    else:
        return isOleFile

    try:
        from OleFileIO_PL import isOleFile
    except ImportError:
        pass
    else:
        return isOleFile


def import_OleFileIO():
    try:
        from olefile import OleFileIO
    except ImportError:
        pass
    else:
        return OleFileIO

    try:
        from OleFileIO_PL import OleFileIO
    except ImportError:
        pass
    else:
        return OleFileIO


@implementer(IStorageNode)
class OleStorageItem(object):

    def __init__(self, olefile, path, parent=None):
        OleFileIO = import_OleFileIO()
        if not isinstance(olefile, OleFileIO):
            raise TypeError()
        self.olefile = olefile
        self.path = path  # path DOES NOT end with '/'

    def get_name(self):
        if self.path == '':
            return None
        segments = self.path.split('/')
        return segments[-1]

    name = cached_property(get_name)


def createStorageOpener(registry, **settings):
    isOleFile = import_isOleFile()
    if isOleFile is None:
        raise ImplementationNotAvailable('storage/olefileio')
    OleFileIO = import_OleFileIO()
    if OleFileIO is None:
        raise ImplementationNotAvailable('storage/olefileio')
    return OleStorageOpener(isOleFile, OleFileIO)


@implementer(IStorageOpener)
class OleStorageOpener:

    def __init__(self, isOleFile, OleFileIO):
        self.isOleFile = isOleFile
        self.OleFileIO = OleFileIO

    def is_storage(self, path):
        return self.isOleFile(path)

    def open_storage(self, path):
        if not self.isOleFile(path):
            errormsg = 'Not an OLE2 Compound Binary File.'
            raise InvalidOleStorageError(errormsg)
        olefile = self.OleFileIO(path)
        return OleStorage(olefile)


@implementer(IStorageStreamNode)
class OleStream(OleStorageItem):

    def open(self):
        return self.olefile.openstream(self.path)


@implementer(IStorageDirectoryNode)
class OleStorageDirectory(OleStorageItem):

    def __iter__(self):
        return olefile_listdir(self.olefile, self.path)

    def __getitem__(self, name):
        if self.path == '' or self.path == '/':
            path = name
        else:
            path = self.path + '/' + name
        if not self.olefile.exists(path):
            raise KeyError('%s not found' % path)
        t = self.olefile.get_type(path)
        if t == 1:  # Storage
            child = OleStorageDirectory(self.olefile, path, self)
            child.__name__ = name
            child.__parent__ = self
            return child
        elif t == 2:  # Stream
            child = OleStream(self.olefile, path, self)
            child.__name__ = name
            child.__parent__ = self
            return child
        else:
            raise KeyError('%s is invalid' % path)


@implementer(IStorage)
class OleStorage(OleStorageDirectory):
    ''' Create an OleStorage instance.

    :param olefile: an OLE2 Compound Binary File.
    :type olefile: an OleFileIO instance or an argument to OleFileIO()
    :param path: internal path in the olefile. Should not end with '/'.
    :raises: `InvalidOleStorageError` when `olefile` is not valid OLE2 format.
    '''

    __parent__ = None
    __name__ = ''

    def __init__(self, olefile, path='', parent=None):
        OleStorageItem.__init__(self, olefile, path, parent)

    def close(self):
        self.olefile.close()


def olefile_listdir(olefile, path):
    if path == '' or path == '/':
        # we use a list instead of a set
        # for python 2.3 compatibility
        yielded = []

        for stream in olefile.listdir():
            top_item = stream[0]
            if top_item in yielded:
                continue
            yielded.append(top_item)
            yield top_item
        return

    if not olefile.exists(path):
        raise IOError('%s not exists' % path)
    if olefile.get_type(path) != 1:
        raise IOError('%s not a storage' % path)
    path_segments = path.split('/')
    for stream in olefile.listdir():
        if len(stream) == len(path_segments) + 1:
            if stream[:-1] == path_segments:
                yield stream[-1]
