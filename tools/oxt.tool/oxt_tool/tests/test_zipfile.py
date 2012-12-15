# -*- coding: utf-8 -*-
from __future__ import with_statement
import unittest
from oxt_tool.storage import _zipfile
from mixin_storage import StorageTestMixin
import contextlib


class TestZipFile(unittest.TestCase, StorageTestMixin):

    @property
    def zipfile_path(self):
        return self.id() + '.zip'

    def zipfile_create(self):
        import zipfile
        return zipfile.ZipFile(self.zipfile_path, 'w')

    def zipfile_get(self):
        import zipfile
        return zipfile.ZipFile(self.zipfile_path, 'r')

    def test_zipfile_folder(self):
        import os
        zf = self.zipfile_create()
        try:
            zf.writestr(os.sep.join(['foo', 'bar.txt']), 'Hello')
            _zipfile.ZipFileFolder(zf, 'foo')
        finally:
            zf.close()

    def test_zipfile_file(self):
        import os
        zf = self.zipfile_create()
        try:
            path = os.sep.join(['foo', 'bar.txt'])
            zf.writestr(path, 'Hello')
            _zipfile.ZipFileFile(zf, path)
        finally:
            zf.close()

    def test_zipfile_file_put(self):
        path = self.id() + '.txt'
        with file(path, 'w') as f:
            f.write('new-file-content')
        with self.create_fixture_folder() as folder:
            folder.file('new-file').put(path)
        with self.get_fixture_folder() as folder:
            with folder['new-file'].open() as f:
                self.assertEquals('new-file-content', f.read())

    def create_fixture_storage(self):
        return _zipfile.ZipFileStorage(self.zipfile_path, 'w')

    @contextlib.contextmanager
    def create_fixture_zipfile(self):
        import os
        zf = self.zipfile_create()
        try:
            zf.writestr(os.sep.join(['foo', 'bar.txt']), 'Hello')
            zf.writestr(os.sep.join(['foo', 'baz.txt']), 'World')
            zf.writestr(os.sep.join(['foo', 'bar', 'baz']), 'Hello World')
            yield zf
        finally:
            zf.close()

    @contextlib.contextmanager
    def create_fixture_folder(self):
        with self.create_fixture_zipfile() as zf:
            yield _zipfile.ZipFileFolder(zf, 'foo')

    @contextlib.contextmanager
    def get_fixture_folder(self):
        zf = self.zipfile_get()
        try:
            yield _zipfile.ZipFileFolder(zf, 'foo')
        finally:
            zf.close()

    def test_zipfile_nodes(self):
        import os.path
        from oxt_tool.storage._zipfile import zipfile_nodes
        with self.create_fixture_zipfile() as zipfile:
            nodes = dict(zipfile_nodes(zipfile))
            self.assertEquals(set(['foo',
                                   os.path.join('foo', 'bar'),
                                   os.path.join('foo', 'bar.txt'),
                                   os.path.join('foo', 'baz.txt'),
                                   os.path.join('foo', 'bar', 'baz')]),
                              set(nodes.keys()))
            self.assertTrue(hasattr(nodes['foo'], '__getitem__'))
            self.assertTrue(hasattr(nodes[os.path.join('foo', 'bar')],
                                    '__getitem__'))
            self.assertTrue(hasattr(nodes[os.path.join('foo', 'bar.txt')],
                                    'open'))
            self.assertTrue(hasattr(nodes[os.path.join('foo', 'baz.txt')],
                                    'open'))
            self.assertTrue(hasattr(nodes[os.path.join('foo', 'bar', 'baz')],
                                    'open'))
