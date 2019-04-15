# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from unittest import TestCase
import json
import os.path
import shutil
import zlib

from hwp5 import filestructure as FS
from hwp5.errors import InvalidHwp5FileError
from hwp5.filestructure import Hwp5DistDoc
from hwp5.filestructure import Hwp5DistDocStream
from hwp5.filestructure import Hwp5DistDocStorage
from hwp5.filestructure import Hwp5File
from hwp5.filestructure import Hwp5FileBase
from hwp5.filestructure import Hwp5FileOpener
from hwp5.filestructure import HwpFileHeader
from hwp5.filestructure import PreviewText
from hwp5.filestructure import Sections
from hwp5.recordstream import read_record
from hwp5.storage import ExtraItemStorage
from hwp5.storage import is_directory
from hwp5.storage import is_stream
from hwp5.storage import unpack
from hwp5.storage.fs import FileSystemStorage
from hwp5.tagids import HWPTAG_DISTRIBUTE_DOC_DATA
from hwp5.tagids import HWPTAG_DOCUMENT_PROPERTIES
from hwp5.tagids import HWPTAG_PARA_HEADER
from hwp5.utils import cached_property
from hwp5.utils import GeneratorReader
from . import test_ole


class TestBase(test_ole.TestBase):

    @cached_property
    def hwp5file_base(self):
        return FS.Hwp5FileBase(self.olestg)

    @cached_property
    def hwp5file_fs(self):
        return FS.Hwp5File(self.olestg)

    hwp5file = hwp5file_fs

    @cached_property
    def docinfo(self):
        return self.hwp5file.docinfo

    @cached_property
    def bodytext(self):
        return self.hwp5file.bodytext

    @cached_property
    def viewtext(self):
        return self.hwp5file.viewtext


class TestModuleFunctions(TestBase):

    def test_is_hwp5file(self):
        assert FS.is_hwp5file(self.hwp5file_path)
        nonole_filename = self.get_fixture_file('nonole.txt')
        assert not FS.is_hwp5file(nonole_filename)


class TestHwp5FileOpener(TestBase):

    def test_open(self):
        hwp5file_opener = Hwp5FileOpener(self.olestorage_opener, Hwp5FileBase)
        hwp5file = hwp5file_opener.open_hwp5file(self.hwp5file_path)
        self.assertTrue('FileHeader' in hwp5file)

    def test_open_with_nonole(self):
        nonole = self.get_fixture_file('nonole.txt')
        hwp5file_opener = Hwp5FileOpener(self.olestorage_opener, Hwp5FileBase)
        self.assertRaises(
            InvalidHwp5FileError,
            hwp5file_opener.open_hwp5file,
            nonole,
        )


class TestHwp5FileBase(TestBase):

    @cached_property
    def hwp5file_base(self):
        return Hwp5FileBase(self.olestg)

    def test_create_with_nonhwp5_storage(self):
        stg = FileSystemStorage(self.get_fixture_file('nonhwp5stg'))
        self.assertRaises(InvalidHwp5FileError, Hwp5FileBase, stg)

    def test_item_is_hwpfileheader(self):
        fileheader = self.hwp5file_base['FileHeader']
        self.assertTrue(isinstance(fileheader, HwpFileHeader))

    def test_header(self):
        header = self.hwp5file_base.header
        self.assertTrue(isinstance(header, HwpFileHeader))


class TestHwp5DistDocStream(TestBase):

    hwp5file_name = 'viewtext.hwp'

    @cached_property
    def jscriptversion(self):
        return Hwp5DistDocStream(
            self.hwp5file_base['Scripts']['JScriptVersion'],
            self.hwp5file_base.header.version
        )

    def test_head_record(self):
        record = self.jscriptversion.head_record()
        self.assertEqual(HWPTAG_DISTRIBUTE_DOC_DATA, record['tagid'])

    def test_head_record_stream(self):
        stream = self.jscriptversion.head_record_stream()
        record = json.load(stream)
        self.assertEqual(HWPTAG_DISTRIBUTE_DOC_DATA, record['tagid'])

        # stream should have been exausted
        self.assertEqual('', stream.read(1))

    def test_head(self):
        head = self.jscriptversion.head()
        self.assertEqual(256, len(head))

    def test_head_stream(self):
        head_stream = self.jscriptversion.head_stream()
        self.assertEqual(256, len(head_stream.read()))

    def test_tail(self):
        tail = self.jscriptversion.tail()
        self.assertEqual(16, len(tail))

    def test_tail_stream(self):
        tail_stream = self.jscriptversion.tail_stream()
        self.assertEqual(16, len(tail_stream.read()))


class TestHwp5DistDicStorage(TestBase):

    hwp5file_name = 'viewtext.hwp'

    @cached_property
    def scripts(self):
        return Hwp5DistDocStorage(self.olestg['Scripts'])

    def test_scripts_other_formats(self):
        jscriptversion = self.scripts['JScriptVersion']
        self.assertTrue(isinstance(jscriptversion, Hwp5DistDocStream))


class TestHwp5DistDoc(TestBase):

    hwp5file_name = 'viewtext.hwp'

    @cached_property
    def hwp5distdoc(self):
        return Hwp5DistDoc(self.olestg)

    def test_conversion_for(self):
        conversion = self.hwp5distdoc.resolve_conversion_for('Scripts')
        self.assertTrue(conversion is Hwp5DistDocStorage)

    def test_getitem(self):
        self.assertTrue(isinstance(self.hwp5distdoc['Scripts'],
                                   Hwp5DistDocStorage))
        self.assertTrue(isinstance(self.hwp5distdoc['ViewText'],
                                   Hwp5DistDocStorage))


class TestCompressedStorage(TestBase):
    def test_getitem(self):
        stg = FS.CompressedStorage(self.olestg['BinData'])
        self.assertTrue(is_directory(stg))

        item = stg['BIN0002.jpg']
        self.assertTrue(is_stream(item))

        f = item.open()
        try:
            data = f.read()
            self.assertEqual(b'\xff\xd8\xff\xe0', data[0:4])
            self.assertEqual(15895, len(data))
        finally:
            f.close()


class TestHwp5Compression(TestBase):

    @cached_property
    def hwp5file_compressed(self):
        return FS.Hwp5Compression(self.hwp5file_base)

    @cached_property
    def docinfo(self):
        return self.hwp5file_compressed['DocInfo'].open()

    @cached_property
    def bodytext(self):
        return self.hwp5file_compressed['BodyText']

    @cached_property
    def scripts(self):
        return self.hwp5file_compressed['Scripts']

    def test_docinfo_decompressed(self):
        record = read_record(self.docinfo, 0)
        self.assertEqual(HWPTAG_DOCUMENT_PROPERTIES, record['tagid'])

    def test_bodytext_decompressed(self):
        record = read_record(self.bodytext['Section0'].open(), 0)
        self.assertEqual(HWPTAG_PARA_HEADER, record['tagid'])

    def test_scripts_version(self):
        hwp5file = self.hwp5file_compressed
        self.assertFalse(hwp5file.header.flags.distributable)

        JScriptVersion = self.scripts['JScriptVersion'].open().read()
        self.assertEqual(8, len(JScriptVersion))


class TestHwp5File(TestBase):

    def test_init_should_accept_string_path(self):
        olestorage = self.olestorage_opener.open_storage(self.hwp5file_path)
        hwp5file = Hwp5File(olestorage)
        self.assertTrue(hwp5file['FileHeader'] is not None)

    def test_init_should_accept_olestorage(self):
        hwp5file = Hwp5File(self.olestg)
        self.assertTrue(hwp5file['FileHeader'] is not None)

    def test_init_should_accept_fs(self):
        outpath = 'test_init_should_accept_fs'
        if os.path.exists(outpath):
            shutil.rmtree(outpath)
        os.mkdir(outpath)
        unpack(self.olestg, outpath)
        fs = FileSystemStorage(outpath)
        hwp5file = Hwp5File(fs)
        fileheader = hwp5file['FileHeader']
        self.assertTrue(fileheader is not None)
        self.assertEqual((5, 0, 1, 7), fileheader.version)

    def test_fileheader(self):
        fileheader = self.hwp5file.header
        self.assertEqual((5, 0, 1, 7), fileheader.version)
        self.assertTrue(fileheader.flags.compressed)

    def test_getitem_storage_classes(self):
        hwp5file = self.hwp5file
        self.assertTrue(isinstance(hwp5file['BinData'], FS.StorageWrapper))
        self.assertTrue(isinstance(hwp5file['BodyText'], FS.Sections))
        self.assertTrue(isinstance(hwp5file['Scripts'], FS.StorageWrapper))

    def test_prv_text(self):
        prvtext = self.hwp5file['PrvText']
        self.assertTrue(isinstance(prvtext, PreviewText))
        expected = '한글 2005 예제 파일입니다.'
        self.assertEqual(expected, prvtext.text[0:len(expected)])

    def test_distdoc_layer_inserted(self):
        # self.hwp5file_name = 'viewtext.hwp'
        # self.assertTrue('Section0.tail' in ExtraItemStorage(self.viewtext))
        pass

    def test_unpack(self):
        outpath = 'test_unpack'
        if os.path.exists(outpath):
            shutil.rmtree(outpath)
        os.mkdir(outpath)
        unpack(ExtraItemStorage(self.hwp5file), outpath)

        self.assertTrue(os.path.exists('test_unpack/_05HwpSummaryInformation'))
        self.assertTrue(os.path.exists('test_unpack/BinData/BIN0002.jpg'))
        self.assertTrue(os.path.exists('test_unpack/BinData/BIN0002.png'))
        self.assertTrue(os.path.exists('test_unpack/BinData/BIN0003.png'))
        self.assertTrue(os.path.exists('test_unpack/BodyText/Section0'))
        self.assertTrue(os.path.exists('test_unpack/DocInfo'))
        self.assertTrue(os.path.exists('test_unpack/DocOptions/_LinkDoc'))
        self.assertTrue(os.path.exists('test_unpack/FileHeader'))
        self.assertTrue(os.path.exists('test_unpack/PrvImage'))
        self.assertTrue(os.path.exists('test_unpack/PrvText'))
        self.assertTrue(os.path.exists('test_unpack/PrvText.utf8'))
        self.assertTrue(os.path.exists('test_unpack/Scripts/DefaultJScript'))
        self.assertTrue(os.path.exists('test_unpack/Scripts/JScriptVersion'))

    def test_if_hwp5file_contains_other_formats(self):
        stg = ExtraItemStorage(self.hwp5file)
        self.assertTrue('PrvText.utf8' in list(stg))

    def test_resolve_conversion_for_bodytext(self):
        self.assertTrue(self.hwp5file.resolve_conversion_for('BodyText'))

    def test_docinfo(self):
        hwp5file = self.hwp5file
        self.assertTrue(isinstance(hwp5file.docinfo, FS.VersionSensitiveItem))
        docinfo = hwp5file.docinfo.open()
        try:
            data = docinfo.read()
        finally:
            docinfo.close()

        docinfo = self.olestg['DocInfo']
        self.assertEqual(zlib.decompress(docinfo.open().read(), -15), data)

    def test_bodytext(self):
        bodytext = self.hwp5file.bodytext
        self.assertTrue(isinstance(bodytext, FS.Sections))
        self.assertEqual(['Section0'], list(bodytext))


class TestSections(TestBase):

    @property
    def sections(self):
        return Sections(
            self.hwp5file.stg['BodyText'],
            self.hwp5file.header.version,
        )


class TestGeneratorReader(TestCase):
    def test_generator_reader(self):
        def data():
            yield b'Hello world'
            yield b'my name is'
            yield b'gen'
            yield b'reader'

        f = GeneratorReader(data())
        self.assertEqual(b'Hel', f.read(3))
        self.assertEqual(b'lo wor', f.read(6))
        self.assertEqual(b'ldmy ', f.read(5))
        self.assertEqual(b'name isgenre', f.read(12))
        self.assertEqual(b'ader', f.read())

        f = GeneratorReader(data())
        self.assertEqual(b'Hel', f.read(3))
        self.assertEqual(b'lo wor', f.read(6))
        self.assertEqual(b'ldmy ', f.read(5))
        self.assertEqual(b'name isgenreader', f.read())

        f = GeneratorReader(data())
        self.assertEqual(b'Hel', f.read(3))
        self.assertEqual(b'lo wor', f.read(6))
        self.assertEqual(b'ldmy ', f.read(5))
        self.assertEqual(b'name isgenreader', f.read(1000))
