# -*- coding: utf-8 -*-
from unittest import TestCase

def example(filename):
    from hwp5.tests import get_fixture_path
    from hwp5.xmlmodel import Hwp5File
    path = get_fixture_path(filename)
    return Hwp5File(path)


class TestPrecondition(TestCase):
    def test_example(self):
        assert example('linespacing.hwp') is not None


class TestConverter(TestCase):

    @property
    def odt_path(self):
        return self.id() + '.odt'

    @property
    def convert(self):
        from hwp5 import plat
        from hwp5.hwp5odt import Converter

        xslt = plat.get_xslt()
        assert xslt is not None, 'no XSLT implementation is available'
        relaxng = plat.get_relaxng()
        return Converter(xslt, relaxng)

    def test_convert_bindata(self):
        from hwp5.hwp5odt import ODTPackage

        hwp5file = example('sample-5017.hwp')
        try:
            f = hwp5file['BinData']['BIN0002.jpg'].open()
            try:
                data1 = f.read()
            finally:
                f.close()

            odtpkg = ODTPackage(self.odt_path)
            try:
                self.convert(hwp5file, odtpkg)
            finally:
                odtpkg.close()
        finally:
            hwp5file.close()

        from zipfile import ZipFile
        zf = ZipFile(self.odt_path)
        data2 = zf.read('bindata/BIN0002.jpg')

        self.assertEquals(data1, data2)
