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
from contextlib import closing
import io
import os.path
import shutil
import sys

from zope.interface import implementer

from ..interfaces import IStorage
from ..interfaces import IStorageDirectoryNode
from ..interfaces import IStorageStreamNode
from ..interfaces import IStorageTreeEventGenerator
from ..interfaces import IStorageTreeEventUnpacker
from ..treeop import STARTEVENT
from ..treeop import ENDEVENT


PY3 = sys.version_info.major == 3
if PY3:
    basestring = str


def is_storage(item):
    return IStorage.providedBy(item)


def is_directory(item):
    return IStorageDirectoryNode.providedBy(item)


def is_stream(item):
    return IStorageStreamNode.providedBy(item)


class ItemWrapper(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getattr__(self, name):
        return getattr(self.wrapped, name)


class StorageWrapper(ItemWrapper):
    def __iter__(self):
        return iter(self.wrapped)

    def __getitem__(self, name):
        node = self.wrapped[name]
        node.__name__ = name
        node.__parent__ = self
        return node


class ItemConversionStorage(StorageWrapper):

    def __getitem__(self, name):
        item = self.wrapped[name]
        # 기반 스토리지에서 찾은 아이템에 대해, conversion()한다.
        conversion = self.resolve_conversion_for(name)
        if conversion:
            node = conversion(item)
            node.__name__ = name
            node.__parent__ = self
            return node
        item.__name__ = name
        item.__parent__ = self
        return item

    def resolve_conversion_for(self, name):
        ''' return a conversion function for the specified storage item '''
        pass


@implementer(IStorageDirectoryNode)
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
            if is_directory(item):
                item = ExtraItemStorage(item)
            item.__name__ = name
            item.__parent__ = self
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
                                node = Open2Stream(func)
                                node.__name__ = name
                                node.__parent__ = self
                                return node
            raise


@implementer(IStorageStreamNode)
class Open2Stream(object):

    def __init__(self, open):
        self.open = open


@implementer(IStorageTreeEventGenerator)
class StorageTreeEventGenerator:

    def generate(self, node, name=''):
        if is_directory(node):
            yield STARTEVENT, name, node
            for child_name in iter(node):
                child_node = node[child_name]
                for x in self.generate(child_node, child_name):
                    yield x
            yield ENDEVENT, name, node
        else:
            yield None, name, node


@implementer(IStorageTreeEventUnpacker)
class StorageTreeEventUnpacker:

    def __init__(self, rename):
        self.rename = rename

    def unpack_from_tree_events(self, tree_events, out_directory):
        path_segments = []
        for ev, name, node in tree_events:
            if ev is STARTEVENT:
                path_segments.append(name)
                path = os.path.join(*([out_directory] + path_segments[1:]))
                if not os.path.exists(path):
                    os.makedirs(path)
            elif ev is ENDEVENT:
                path_segments = path_segments[:-1]
            else:
                modified_name = self.rename(name)
                path = os.path.join(*([out_directory] + path_segments[1:] +
                                      [modified_name]))
                with closing(node.open()) as input_fp:
                    with io.open(path, 'wb') as output_fp:
                        shutil.copyfileobj(input_fp, output_fp)


def rename_safe(name):
    return name.replace('\x05', '_05')


def unpack(stg, outbase):
    storage_event_generator = StorageTreeEventGenerator()
    storage_event_unpacker = StorageTreeEventUnpacker(rename_safe)
    tree_events = storage_event_generator.generate(stg)
    storage_event_unpacker.unpack_from_tree_events(
        tree_events, outbase,
    )


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
        if is_directory(item):
            printstorage(item, path + '/')
        elif is_stream(item):
            print(path.encode('unicode_escape').decode('utf-8'))
