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

    @property
    def xslt(self):
        from hwp5.plat import get_xslt
        return get_xslt()

    @property
    def xhwp5_path(self):
        return self.id() + '.xhwp5'

    def create_xhwp5(self):
        xhwp5_path = self.xhwp5_path
        xhwp5_file = file(xhwp5_path, 'w')
        try:
            self.hwp5file.xmlevents(embedbin=False).dump(xhwp5_file)
        finally:
            xhwp5_file.close()
        return xhwp5_path

    def test_generate_css_file(self):
        base_dir = self.make_base_dir()
        css_path = os.path.join(base_dir, 'styles.css')

        xhwp5_path = self.create_xhwp5()
        from hwp5.hwp5html import generate_css_file
        generate_css_file(self.xslt, xhwp5_path, css_path)

        self.assertTrue(os.path.exists(css_path))
        #with file(css_path) as f:
        #    print f.read()

    def test_generate_html_file(self):
        base_dir = self.make_base_dir()
        html_path = os.path.join(base_dir, 'index.html')

        xhwp5_path = self.create_xhwp5()
        from hwp5.hwp5html import generate_html_file
        generate_html_file(self.xslt, xhwp5_path, html_path)

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
