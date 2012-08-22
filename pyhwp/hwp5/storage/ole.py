# -*- coding: utf-8 -*-
#
#                    GNU AFFERO GENERAL PUBLIC LICENSE
#                       Version 3, 19 November 2007
#
#    pyhwp : hwp file format parser in python
#    Copyright (C) 2010 mete0r@sarangbang.or.kr
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from hwp5.utils import cached_property

class OleStorageItem(object):

    def __init__(self, olefile, path, parent=None):
        self.olefile = olefile
        self.path = path  # path DOES NOT end with '/'

    def get_name(self):
        if self.path == '':
            return None
        segments = self.path.split('/')
        return segments[-1]

    name = cached_property(get_name)


class OleStream(OleStorageItem):

    def open(self):
        return self.olefile.openstream(self.path)


class OleStorage(OleStorageItem):
    ''' Create an OleStorage instance.

    :param olefile: an OLE2 Compound Binary File.
    :type olefile: an OleFileIO instance or an argument to OleFileIO()
    :param path: internal path in the olefile. Should not end with '/'.
    :raises: `InvalidOleStorageError` when `olefile` is not valid OLE2 format.
    '''

    def __init__(self, olefile, path='', parent=None):
        if not hasattr(olefile, 'openstream'):
            from OleFileIO_PL import isOleFile
            if not isOleFile(olefile):
                from hwp5.errors import InvalidOleStorageError
                raise InvalidOleStorageError('Not an OLE2 Compound Binary File.')
            from OleFileIO_PL import OleFileIO
            olefile = OleFileIO(olefile)
        OleStorageItem.__init__(self, olefile, path, parent)

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
            return OleStorage(self.olefile, path, self)
        elif t == 2:  # Stream
            return OleStream(self.olefile, path, self)
        else:
            raise KeyError('%s is invalid' % path)

    def close(self):
        # if this is root, close underlying olefile
        if self.path == '':
            # old version of OleFileIO has no close()
            if hasattr(self.olefile, 'close'):
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
