# -*- coding: utf-8 -*-
from __future__ import with_statement
import unittest
from oxt_tool.package import is_package
from oxt_tool.storage import open_storage
from oxt_tool.storage import resolve_path
from oxt_tool.storage.fs import FileSystemStorage
from oxt_tool.manifest import Manifest
from oxt_tool.description import Description


class PackageTest(unittest.TestCase):

    def test_package_name_from_desc(self):
        from oxt_tool.package import package_name_from_desc
        desc = Description(identifier='pyhwp.example', version='')
        self.assertEqual('pyhwp.example.oxt', package_name_from_desc(desc))
        desc.version = '0.1'
        self.assertEqual('pyhwp.example-0.1.oxt', package_name_from_desc(desc))

    def test_make_output_path(self):
        from oxt_tool.package import make_output_path

        self.assertEqual('abc.oxt', make_output_path('abc.oxt'))
        self.assertEqual('./abc.oxt', make_output_path('./abc.oxt'))
        self.assertEqual('abc/def.oxt', make_output_path('abc/def.oxt'))

        desc = Description(identifier='example', version='0.1')
        self.assertEqual('example-0.1.oxt', make_output_path('', desc))
        self.assertEqual('./example-0.1.oxt', make_output_path('.', desc))
        self.assertEqual('abc/example-0.1.oxt', make_output_path('abc/', desc))

        dirpath = self.id()
        import shutil
        import os.path
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)
        os.mkdir(dirpath)
        self.assertEqual(os.path.join(dirpath, 'example-0.1.oxt'),
                          make_output_path(dirpath, desc))


class BuildPackageTest(unittest.TestCase):

    def test_build_minimal(self):
        from oxt_tool.package import build

        manifest = Manifest()
        description = Description()
        oxt_path = self.id() + '.oxt'
        build(oxt_path, manifest, description)
        with open_storage(oxt_path) as pkg:
            self.assertTrue(is_package(pkg))

    def test_build_missing(self):
        from oxt_tool.package import build

        oxt_path = self.id() + '.oxt'

        manifest = Manifest()
        description = Description(license=dict(en='COPYING'))
        files = dict()
        try:
            build(oxt_path, manifest, description, files=files)
            assert False, 'exception expected'
        except Exception:
            pass

    def test_build_typical(self):
        from oxt_tool.package import build
        from oxt_tool.storage import makedirs_to_file

        manifest = Manifest()
        description = Description()

        import os.path
        import shutil
        src_folder_path = self.id()
        if os.path.exists(src_folder_path):
            shutil.rmtree(src_folder_path)
        src_folder = FileSystemStorage(src_folder_path, 'w')

        license_path = 'COPYING'
        license_node = makedirs_to_file(src_folder, license_path)
        with license_node.open('w') as f:
            f.write('GNU AGPL')
        description.license['en'] = license_path

        oxt_path = self.id() + '.oxt'

        files = {license_path: license_node}
        build(oxt_path, manifest, description, files=files)

        with open_storage(oxt_path) as pkg:
            with resolve_path(pkg, 'COPYING').open() as f:
                self.assertEqual('GNU AGPL', f.read())
