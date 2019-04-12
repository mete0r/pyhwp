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
import sys


PY3 = sys.version_info.major == 3
if PY3:
    basestring = str


def is_storage(item):
    return hasattr(item, '__iter__') and hasattr(item, '__getitem__')


def is_stream(item):
    return hasattr(item, 'open') and callable(item.open)


class ItemWrapper(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getattr__(self, name):
        return getattr(self.wrapped, name)


class StorageWrapper(ItemWrapper):
    def __iter__(self):
        return iter(self.wrapped)

    def __getitem__(self, name):
        return self.wrapped[name]


class ItemConversionStorage(StorageWrapper):

    def __getitem__(self, name):
        item = self.wrapped[name]
        # 기반 스토리지에서 찾은 아이템에 대해, conversion()한다.
        conversion = self.resolve_conversion_for(name)
        if conversion:
            return conversion(item)
        return item

    def resolve_conversion_for(self, name):
        ''' return a conversion function for the specified storage item '''
        pass


class ExtraItemStorage(StorageWrapper):

    def __iter__(self):
        for name in self.wrapped:
            yield name

            item = self.wrapped[name]
            if hasattr(item, 'other_formats'):
                other_formats = item.other_formats()
                if other_formats:
                    for ext in other_formats:
                        yield name + ext

    def __getitem__(self, name):
        try:
            item = self.wrapped[name]
            if is_storage(item):
                item = ExtraItemStorage(item)
            return item
        except KeyError:
            # 기반 스토리지에는 없으므로, other_formats() 중에서 찾아본다.
            for root in self.wrapped:
                item = self.wrapped[root]
                if hasattr(item, 'other_formats'):
                    other_formats = item.other_formats()
                    if other_formats:
                        for ext, func in other_formats.items():
                            if root + ext == name:
                                return Open2Stream(func)
            raise


class Open2Stream(object):

    def __init__(self, open):
        self.open = open


def iter_storage_leafs(stg, basepath=''):
    ''' iterate every leaf nodes in the storage

        stg: an instance of Storage
    '''
    for name in stg:
        path = basepath + name
        item = stg[name]
        if is_storage(item):
            for x in iter_storage_leafs(item, path + '/'):
                yield x
        else:
            yield path


def unpack(stg, outbase):
    ''' unpack a storage into outbase directory

        stg: an instance of Storage
        outbase: path to a directory in filesystem (should not end with '/')
    '''
    for name in stg:
        outpath = os.path.join(outbase, name)
        item = stg[name]
        if is_storage(item):
            if not os.path.exists(outpath):
                os.mkdir(outpath)
            unpack(item, outpath)
        else:
            f = item.open()
            try:
                outpath = outpath.replace('\x05', '_05')
                with io.open(outpath, 'wb') as outfile:
                    outfile.write(f.read())
            finally:
                f.close()


def open_storage_item(stg, path):
    if isinstance(path, basestring):
        path_segments = path.split('/')
    else:
        path_segments = path

    item = stg
    for name in path_segments:
        item = item[name]
    return item


def printstorage(stg, basepath=''):
    names = list(stg)
    names.sort()
    for name in names:
        path = basepath + name
        item = stg[name]
        if is_storage(item):
            printstorage(item, path + '/')
        elif is_stream(item):
            print(path.encode('unicode_escape').decode('utf-8'))
