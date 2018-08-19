# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from unittest import TestCase

from hwp5.plat import olefileio

from .mixin_olestg import OleStorageTestMixin


class TestOleStorageOleFileIO(TestCase, OleStorageTestMixin):

    def setUp(self):
        if olefileio.is_enabled():
            self.OleStorage = olefileio.OleStorage
