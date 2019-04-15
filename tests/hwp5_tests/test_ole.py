# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from unittest import TestCase

from hwp5.plat import createOleStorageOpener

from .fixtures import get_fixture_path
from .fixtures import open_fixture
from .mixin_olestg import OleStorageTestMixin


class TestBase(TestCase):

    hwp5file_name = 'sample-5017.hwp'

    def get_fixture_file(self, filename):
        return get_fixture_path(filename)

    def open_fixture(self, filename, *args, **kwargs):
        return open_fixture(filename, *args, **kwargs)

    @property
    def hwp5file_path(self):
        return self.get_fixture_file(self.hwp5file_name)

    @property
    def olestorage_opener(self):
        return createOleStorageOpener(None)

    @property
    def olestg(self):
        return self.olestorage_opener.open_storage(self.hwp5file_path)


class TestOleStorage(TestCase, OleStorageTestMixin):

    def setUp(self):
        self.olestorage_opener = createOleStorageOpener(None)
