# -*- coding: utf-8 -*-
from __future__ import with_statement
import unittest
from contextlib import contextmanager
from mixin_storage import StorageTestMixin


class TestFileSystem(unittest.TestCase, StorageTestMixin):

    @property
    def fixture_path(self):
        return self.id()

    def create_fixture_storage(self):
        from oxt_tool.storage.fs import FileSystemStorage
        return FileSystemStorage(self.fixture_path, 'a')
    
    @contextmanager
    def create_fixture_folder(self):
        import os.path
        import shutil
        path = self.fixture_path
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
        os.mkdir(os.path.join(path, 'bar'))
        with file(os.path.join(path, 'bar.txt'), 'w') as f:
            f.write('Hello')
        with file(os.path.join(path, 'baz.txt'), 'w') as f:
            f.write('World')
        from oxt_tool.storage.fs import FileSystemFolder
        yield FileSystemFolder(path)

    @contextmanager
    def get_fixture_folder(self):
        from oxt_tool.storage.fs import FileSystemFolder
        yield FileSystemFolder(self.fixture_path)
