# -*- coding: utf-8 -*-
from unittest import TestCase
from mixin_olestg import OleStorageTestMixin


class TestBase(TestCase):

    hwp5file_name = 'sample-5017.hwp'

    def get_fixture_file(self, filename):
        from hwp5.tests import get_fixture_path
        return get_fixture_path(filename)

    def open_fixture(self, filename, *args, **kwargs):
        from hwp5.tests import open_fixture
        return open_fixture(filename, *args, **kwargs)

    @property
    def hwp5file_path(self):
        return self.get_fixture_file(self.hwp5file_name)

    @property
    def olestg(self):
        from hwp5.storage.ole import OleStorage
        return OleStorage(self.hwp5file_path)


class TestOleStorage(TestCase, OleStorageTestMixin):

    def setUp(self):
        from hwp5.storage.ole import OleStorage
        self.OleStorage = OleStorage
