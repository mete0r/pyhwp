# -*- coding: utf-8 -*-
from __future__ import with_statement
from unittest import TestCase
from contextlib import closing


def example_path(filename):
    from fixtures import get_fixture_path
    return get_fixture_path(filename)


def open_example(filename):
    from hwp5.xmlmodel import Hwp5File
    path = example_path(filename)
    return closing(Hwp5File(path))


class TestPrecondition(TestCase):
    def test_example(self):
        with open_example('linespacing.hwp') as hwp5file:
            assert hwp5file is not None


class TestODTTransform(TestCase):

    @property
    def odt_path(self):
        return self.id() + '.odt'

    @property
    def transform(self):
        from hwp5 import plat
        from hwp5.hwp5odt import ODTTransform

        xslt = plat.get_xslt_compile()
        assert xslt is not None, 'no XSLT implementation is available'
        relaxng = plat.get_relaxng_compile()
        return ODTTransform(xslt, relaxng)

    def test_convert_bindata(self):
        from hwp5.hwp5odt import open_odtpkg

        with open_example('sample-5017.hwp') as hwp5file:
            f = hwp5file['BinData']['BIN0002.jpg'].open()
            try:
                data1 = f.read()
            finally:
                f.close()
            with open_odtpkg(self.odt_path) as odtpkg:
                self.transform.transform_hwp5_to_package(hwp5file, odtpkg)

        from zipfile import ZipFile
        zf = ZipFile(self.odt_path)
        data2 = zf.read('bindata/BIN0002.jpg')

        self.assertEquals(data1, data2)
