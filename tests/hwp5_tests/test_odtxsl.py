# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from unittest import TestCase
from contextlib import closing
from zipfile import ZipFile

from zope.interface.registry import Components

from hwp5.hwp5odt import ODTTransform
from hwp5.hwp5odt import open_odtpkg
from hwp5.xmlmodel import Hwp5File
from hwp5.cli import create_xslt_factory
from hwp5.cli import create_relaxng_factory
from hwp5.cli import init_temp_stream_factory
from hwp5.plat import createOleStorageOpener

from .fixtures import get_fixture_path


def example_path(filename):
    return get_fixture_path(filename)


def open_example(filename):
    path = example_path(filename)
    olestorage_opener = createOleStorageOpener(None)
    olestorage = olestorage_opener.open_storage(path)
    return closing(Hwp5File(olestorage))


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
        registry = Components()
        init_temp_stream_factory(registry)
        xslt_factory = create_xslt_factory(registry)
        relaxng_factory = create_relaxng_factory(registry)
        return ODTTransform(xslt_factory, relaxng_factory)

    def test_convert_bindata(self):

        with open_example('sample-5017.hwp') as hwp5file:
            f = hwp5file['BinData']['BIN0002.jpg'].open()
            try:
                data1 = f.read()
            finally:
                f.close()
            with open_odtpkg(self.odt_path) as odtpkg:
                self.transform.transform_hwp5_to_package(hwp5file, odtpkg)

        zf = ZipFile(self.odt_path)
        data2 = zf.read('bindata/BIN0002.jpg')

        self.assertEqual(data1, data2)
