# -*- coding: utf-8 -*-
import os
import os.path
import shutil
from hwp5.tests import test_xmlmodel


class TestBase(test_xmlmodel.TestBase):

    def make_base_dir(self):
        base_dir = self.id()
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)
        os.mkdir(base_dir)
        return base_dir


class HtmlConvTest(TestBase):

    def test_generate_css_file(self):
        base_dir = self.make_base_dir()
        hwp5file = self.hwp5file
        css_path = os.path.join(base_dir, 'styles.css')

        from tempfile import TemporaryFile
        hwp5_xml = TemporaryFile()
        try:
            hwp5file.xmlevents(embedbin=False).dump(hwp5_xml)
            hwp5_xml.seek(0)

            from hwp5.hwp5html import generate_css_file
            generate_css_file(hwp5_xml, css_path)
        finally:
            hwp5_xml.close()

        self.assertTrue(os.path.exists(css_path))
        #with file(css_path) as f:
        #    print f.read()

    def test_generate_html_file(self):
        base_dir = self.make_base_dir()
        hwp5file = self.hwp5file
        html_path = os.path.join(base_dir, 'index.html')

        from tempfile import TemporaryFile
        hwp5_xml = TemporaryFile()
        try:
            hwp5file.xmlevents(embedbin=False).dump(hwp5_xml)
            hwp5_xml.seek(0)

            from hwp5.hwp5html import generate_html_file
            generate_html_file(hwp5_xml, html_path)
        finally:
            hwp5_xml.close()

        self.assertTrue(os.path.exists(html_path))
        #with file(html_path) as f:
        #    print f.read()

    def test_extract_bindata_dir(self):
        base_dir = self.make_base_dir()
        hwp5file = self.hwp5file

        bindata_dir = os.path.join(base_dir, 'bindata')

        from hwp5.hwp5html import extract_bindata_dir
        extract_bindata_dir(hwp5file, bindata_dir)

        bindata_stg = hwp5file['BinData']

        from hwp5.storage.fs import FileSystemStorage
        self.assertEquals(set(bindata_stg),
                          set(FileSystemStorage(bindata_dir)))
