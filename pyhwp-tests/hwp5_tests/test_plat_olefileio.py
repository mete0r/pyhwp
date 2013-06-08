# -*- coding: utf-8 -*-
from unittest import TestCase
from mixin_olestg import OleStorageTestMixin


class TestOleStorageOleFileIO(TestCase, OleStorageTestMixin):

    def setUp(self):
        from hwp5.plat import olefileio
        if olefileio.is_enabled():
            self.OleStorage = olefileio.OleStorage
