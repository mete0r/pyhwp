# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from unittest import TestCase

from hwp5.errors import ImplementationNotAvailable
from hwp5.plat import jython_poifs

from .mixin_olestg import OleStorageTestMixin


class TestOleStorageJythonPoiFS(TestCase, OleStorageTestMixin):

    def setUp(self):
        try:
            self.olestorage_opener = jython_poifs.createStorageOpener(None)
        except ImplementationNotAvailable:
            self.olestorage_opener = None
