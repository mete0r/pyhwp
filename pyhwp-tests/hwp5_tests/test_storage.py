# -*- coding: utf-8 -*-
from unittest import TestCase
from hwp5.storage import StorageWrapper

class TestStorageWrapper(TestCase):

    @property
    def storage(self):
        from StringIO import StringIO
        return dict(FileHeader=StringIO('fileheader'),
                    BinData={'BIN0001.jpg': StringIO('bin0001.jpg')})

    def test_iter(self):
        stg = StorageWrapper(self.storage)
        expected = ['FileHeader', 'BinData']
        self.assertEquals(sorted(expected), sorted(iter(stg)))

    def test_getitem(self):
        stg = StorageWrapper(self.storage)
        self.assertEquals('fileheader', stg['FileHeader'].read())
        self.assertEquals('bin0001.jpg', stg['BinData']['BIN0001.jpg'].read())
