# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from io import BytesIO
from unittest import TestCase

from zope.interface import implementer

from hwp5.interfaces import IStorageStreamNode
from hwp5.interfaces import IStorageDirectoryNode
from hwp5.storage import StorageWrapper


@implementer(IStorageDirectoryNode)
class DictBasedDirectory:

    def __init__(self, d):
        self.d = d

    def __iter__(self):
        return iter(self.d)

    def __getitem__(self, name):
        return self.d[name]


@implementer(IStorageStreamNode)
class MemoryStream:

    def __init__(self, data):
        self.data = data

    def open(self):
        return BytesIO(self.data)


class TestStorageWrapper(TestCase):

    @property
    def storage(self):
        return DictBasedDirectory({
            'FileHeader': MemoryStream(b'fileheader'),
            'BinData': DictBasedDirectory({
                'BIN0001.jpg': MemoryStream(b'bin0001.jpg'),
            }),
        })

    def test_iter(self):
        stg = StorageWrapper(self.storage)
        expected = ['FileHeader', 'BinData']
        self.assertEqual(sorted(expected), sorted(iter(stg)))

    def test_getitem(self):
        stg = StorageWrapper(self.storage)
        self.assertEqual(
            b'fileheader',
            stg['FileHeader'].open().read()
        )
        self.assertEqual(
            b'bin0001.jpg',
            stg['BinData']['BIN0001.jpg'].open().read()
        )
