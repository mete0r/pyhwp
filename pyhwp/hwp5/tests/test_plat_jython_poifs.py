# -*- coding: utf-8 -*-
from unittest import TestCase
from mixin_olestg import OleStorageTestMixin


class TestOleStorageJythonPoiFS(TestCase, OleStorageTestMixin):

    def setUp(self):
        from hwp5.plat import jython_poifs
        if jython_poifs.is_enabled():
            self.OleStorage = jython_poifs.OleStorage
