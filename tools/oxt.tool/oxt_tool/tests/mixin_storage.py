# -*- coding: utf-8 -*-
from __future__ import with_statement
from oxt_tool.storage import resolve_path
from oxt_tool.storage import makedirs
from oxt_tool.storage import makedirs_to_file
from oxt_tool.storage import put_file
from oxt_tool.storage import get_file
from oxt_tool.storage import openable_path_on_filesystem
from oxt_tool.storage import copy_file


class StorageTestMixin(object):

    def test_storage(self):
        stg = self.create_fixture_storage()
        self.assertTrue(hasattr(stg, 'close'))
        try:
            self.assertTrue(hasattr(stg, '__enter__'))
            self.assertTrue(hasattr(stg, '__exit__'))
        finally:
            stg.close()

    def test_folder_in(self):
        with self.create_fixture_folder() as folder:
            self.assertTrue('bar.txt' in folder)
            self.assertTrue('baz.txt' in folder)
            self.assertTrue('bar' in folder)
            self.assertFalse('nonexists' in folder)

    def test_folder_iterate(self):
        with self.create_fixture_folder() as folder:
            self.assertEqual(set(['bar.txt', 'baz.txt', 'bar']),
                              set(folder))

    def test_folder_getitem(self):
        with self.create_fixture_folder() as folder:
            self.assertTrue(hasattr(folder['bar.txt'], 'open'))
            self.assertTrue(hasattr(folder['baz.txt'], 'open'))
            self.assertTrue(hasattr(folder['bar'], '__iter__'))
            try:
                folder['nonexists'] 
                assert False, 'KeyError expected'
            except KeyError:
                pass

    def test_file_open_for_reading(self):
        with self.create_fixture_folder() as folder:
            f = folder['bar.txt'].open()
            try:
                self.assertTrue(hasattr(f, '__enter__'))
                self.assertTrue(hasattr(f, '__exit__'))
                self.assertEqual('Hello', f.read())
            finally:
                f.close()

    def test_file_open_for_writing(self):
        with self.create_fixture_folder() as folder:
            f = folder['bar.txt'].open('w')
            try:
                self.assertTrue(hasattr(f, '__enter__'))
                self.assertTrue(hasattr(f, '__exit__'))
                self.assertTrue(hasattr(f, 'fileno'))
                f.write('Hello World')
            finally:
                f.close()

        with self.get_fixture_folder() as folder:
            f = folder['bar.txt'].open()
            try:
                self.assertEqual('Hello World', f.read())
            finally:
                f.close()

    def test_folder_new_file(self):
        with self.create_fixture_folder() as folder:
            self.assertTrue('new-file.txt' not in folder)
            node = folder.file('new-file.txt')
            f = node.open('w')
            try:
                f.write('new-file-contents')
            finally:
                f.close()

        with self.get_fixture_folder() as folder:
            self.assertTrue('new-file.txt' in folder)
            node = folder['new-file.txt']
            f = node.open()
            try:
                self.assertEqual('new-file-contents',
                                  f.read())
            finally:
                f.close()

    def test_folder_new_folder(self):
        with self.create_fixture_folder() as folder:
            self.assertTrue('new-folder' not in folder)
            new_folder = folder.folder('new-folder')

            # we can assert that the new folder exists
            # only if there are at least one file in the folder.
            # (e.g. zipfile)
            node = new_folder.file('file-in-new-folder')
            f = node.open('w')
            try:
                f.write('hello')
            finally:
                f.close()

        with self.get_fixture_folder() as folder:
            self.assertTrue('new-folder' in folder)

    def test_resolve_path(self):
        with self.create_fixture_folder() as folder:
            res = resolve_path(folder, '')
            self.assertEqual(folder, res)

            res = resolve_path(folder, '/')
            self.assertEqual(folder, res)

    def test_makedirs(self):
        import os.path

        dirname = '1'
        path = os.path.join(dirname, 'marker')
        with self.create_fixture_folder() as folder:
            res = makedirs(folder, '')
            self.assertEqual(folder, res)

            fld = makedirs(folder, dirname)
            with fld.file('marker').open('w') as f:
                f.write(dirname)
        with self.get_fixture_folder() as folder:
            node = resolve_path(folder, path)
            with node.open() as f:
                self.assertEqual(dirname, f.read())

        dirname = os.path.join(dirname, '2')
        path = os.path.join(dirname, 'marker')
        with self.create_fixture_folder() as folder:
            fld = makedirs(folder, dirname)
            with fld.file('marker').open('w') as f:
                f.write(dirname)
        with self.get_fixture_folder() as folder:
            node = resolve_path(folder, path)
            with node.open() as f:
                self.assertEqual(dirname, f.read())

        # on existing non-folder
        dirname = 'bar.txt'
        with self.create_fixture_folder() as folder:
            try:
                makedirs(folder, dirname)
                assert False, 'exception expected'
            except:
                pass

        # under existing non-folder
        dirname = os.path.join(dirname, 'should-fail')
        with self.create_fixture_folder() as folder:
            try:
                makedirs(folder, dirname)
                assert False, 'exception expected'
            except:
                pass
        with self.get_fixture_folder() as folder:
            self.assertEqual(None, resolve_path(folder, dirname))

    def test_makedirs_to_file(self):
        import os.path
        path = os.path.join('hello', 'world', 'makedirs')
        with self.create_fixture_folder() as folder:
            node = makedirs_to_file(folder, path)
            with node.open('w'):
                pass
        with self.get_fixture_folder() as folder:
            node = resolve_path(folder, path)
            self.assertTrue(node is not None)

    def test_file_put(self):
        import os
        data = os.urandom(5000)
        path = self.id() + '.bin'
        with file(path, 'w') as f:
            f.write(data)
        with self.create_fixture_folder() as folder:
            node = folder.file('new-file')
            put_file(node, path)
        with self.get_fixture_folder() as folder:
            node = folder['new-file']
            with node.open() as f:
                self.assertEqual(data, f.read())

    def test_file_get(self):
        path = self.id() + '.got'
        with self.create_fixture_folder() as folder:
            node = folder['bar.txt']
            get_file(node, path)
        with file(path) as f:
            self.assertEqual('Hello', f.read())

    def test_openable_path_on_filesystem(self):
        with self.create_fixture_folder() as folder:
            with folder.file('new-file').open('w') as f:
                f.write('new-content')
            node = folder['new-file']
            with openable_path_on_filesystem(node) as path:
                with file(path) as f:
                    self.assertEqual('new-content', f.read())

            with openable_path_on_filesystem(node, writeback=True) as path:
                with file(path, 'w') as f:
                    f.write('modified-content')
            with node.open() as f:
                self.assertEqual('modified-content', f.read())

    def test_file_copy(self):
        with self.create_fixture_folder() as testee:

            #
            # copy from/to zipfile
            #
            from oxt_tool.storage._zipfile import ZipFileStorage
            zfs = ZipFileStorage(self.id() + '.zipstg.zip', 'a')
            with zfs.file('from-zipfile').open('w') as f:
                f.write('copied-from-zipfile')

            # zipfile to testee
            copy_file(zfs['from-zipfile'], testee.file('from-zipfile'))
            with testee['from-zipfile'].open() as f:
                self.assertEqual('copied-from-zipfile', f.read())

            # testee to zipfile
            copy_file(testee['bar.txt'], zfs.file('from-testee'))
            with zfs['from-testee'].open() as f:
                self.assertEqual('Hello', f.read())

            #
            # copy from/to filesystem
            #
            from oxt_tool.storage.fs import FileSystemStorage
            fss_path = self.id() + '.fsstg'
            import shutil
            import os.path
            if os.path.exists(fss_path):
                shutil.rmtree(fss_path)
            os.mkdir(fss_path)
            fss = FileSystemStorage(fss_path)
            with fss.file('from-fs').open('w') as f:
                f.write('copied-from-fs')

            # fs to testee
            copy_file(fss['from-fs'], testee.file('from-fs'))
            with testee['from-fs'].open() as f:
                self.assertEqual('copied-from-fs', f.read())

            # testee to fs
            copy_file(testee['bar.txt'], fss.file('from-testee'))
            with fss['from-testee'].open() as f:
                self.assertEqual('Hello', f.read())
