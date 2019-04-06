# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from io import BytesIO
from unittest import TestCase

from hwp5.storage import StorageWrapper


class TestStorageWrapper(TestCase):

    @property
    def storage(self):
        return dict(FileHeader=BytesIO(b'fileheader'),
                    BinData={'BIN0001.jpg': BytesIO(b'bin0001.jpg')})

    def test_iter(self):
        stg = StorageWrapper(self.storage)
        expected = ['FileHeader', 'BinData']
        self.assertEqual(sorted(expected), sorted(iter(stg)))

    def test_getitem(self):
        stg = StorageWrapper(self.storage)
        self.assertEqual(b'fileheader', stg['FileHeader'].read())
        self.assertEqual(b'bin0001.jpg', stg['BinData']['BIN0001.jpg'].read())
