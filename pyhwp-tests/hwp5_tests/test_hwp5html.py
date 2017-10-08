# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from contextlib import closing
import os.path
import shutil

from hwp5.hwp5html import HTMLTransform
from hwp5.plat import get_xslt
from hwp5.storage.fs import FileSystemStorage

from . import test_xmlmodel


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
        return get_xslt()

    @property
    def xhwp5_path(self):
        return self.id() + '.xhwp5'

    @property
    def transform(self):
        return HTMLTransform()

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

        with closing(self.hwp5file) as hwp5file:
            with file(css_path, 'w+') as f:
                self.transform.transform_hwp5_to_css(hwp5file, f)

    def test_generate_html_file(self):
        base_dir = self.make_base_dir()
        html_path = os.path.join(base_dir, 'index.xhtml')

        with closing(self.hwp5file) as hwp5file:
            with file(html_path, 'w+') as f:
                self.transform.transform_hwp5_to_xhtml(hwp5file, f)

    def test_extract_bindata_dir(self):
        base_dir = self.make_base_dir()
        hwp5file = self.hwp5file

        bindata_dir = os.path.join(base_dir, 'bindata')

        self.transform.extract_bindata_dir(hwp5file, bindata_dir)

        bindata_stg = hwp5file['BinData']

        self.assertEquals(set(bindata_stg),
                          set(FileSystemStorage(bindata_dir)))

    def test_extract_bindata_dir_without_bindata(self):
        self.hwp5file_name = 'charshape.hwp'
        base_dir = self.make_base_dir()
        hwp5file = self.hwp5file

        bindata_dir = os.path.join(base_dir, 'bindata')

        self.transform.extract_bindata_dir(hwp5file, bindata_dir)
        self.assertFalse(os.path.exists(bindata_dir))
