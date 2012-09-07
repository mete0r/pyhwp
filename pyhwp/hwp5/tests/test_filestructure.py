# -*- coding: utf-8 -*-
from unittest import TestCase
from hwp5 import filestructure as FS
from hwp5.utils import cached_property
from hwp5.tests import test_ole

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


class TestHwp5FileBase(TestBase):

    @cached_property
    def hwp5file_base(self):
        from hwp5.filestructure import Hwp5FileBase
        return Hwp5FileBase(self.olestg)

    def test_create_with_filename(self):
        from hwp5.filestructure import Hwp5FileBase
        hwp5file = Hwp5FileBase(self.hwp5file_path)
        self.assertTrue('FileHeader' in hwp5file)

    def test_create_with_nonole(self):
        from hwp5.errors import InvalidHwp5FileError
        from hwp5.filestructure import Hwp5FileBase
        nonole = self.get_fixture_file('nonole.txt')
        self.assertRaises(InvalidHwp5FileError, Hwp5FileBase, nonole)

    def test_create_with_nonhwp5_storage(self):
        from hwp5.errors import InvalidHwp5FileError
        from hwp5.storage.fs import FileSystemStorage
        from hwp5.filestructure import Hwp5FileBase
        stg = FileSystemStorage(self.get_fixture_file('nonhwp5stg'))
        self.assertRaises(InvalidHwp5FileError, Hwp5FileBase, stg)

    def test_item_is_hwpfileheader(self):
        from hwp5.filestructure import HwpFileHeader
        fileheader = self.hwp5file_base['FileHeader']
        self.assertTrue(isinstance(fileheader, HwpFileHeader))

    def test_header(self):
        from hwp5.filestructure import HwpFileHeader
        header = self.hwp5file_base.header
        self.assertTrue(isinstance(header, HwpFileHeader))


class TestHwp5DistDocStream(TestBase):

    hwp5file_name = 'viewtext.hwp'

    @cached_property
    def jscriptversion(self):
        from hwp5.filestructure import Hwp5DistDocStream
        return Hwp5DistDocStream(self.hwp5file_base['Scripts']['JScriptVersion'],
                                 self.hwp5file_base.header.version)

    def test_head_record(self):
        from hwp5.tagids import HWPTAG_DISTRIBUTE_DOC_DATA
        record = self.jscriptversion.head_record()
        self.assertEquals(HWPTAG_DISTRIBUTE_DOC_DATA, record['tagid'])

    def test_head_record_stream(self):
        from hwp5.tagids import HWPTAG_DISTRIBUTE_DOC_DATA
        import simplejson
        stream = self.jscriptversion.head_record_stream()
        record = simplejson.load(stream)
        self.assertEquals(HWPTAG_DISTRIBUTE_DOC_DATA, record['tagid'])

        # stream should have been exausted
        self.assertEquals('', stream.read(1))

    def test_head(self):
        head = self.jscriptversion.head()
        self.assertEquals(256, len(head))

    def test_head_stream(self):
        head_stream = self.jscriptversion.head_stream()
        self.assertEquals(256, len(head_stream.read()))

    def test_tail(self):
        tail = self.jscriptversion.tail()
        self.assertEquals(16, len(tail))

    def test_tail_stream(self):
        tail_stream = self.jscriptversion.tail_stream()
        self.assertEquals(16, len(tail_stream.read()))


class TestHwp5DistDicStorage(TestBase):

    hwp5file_name = 'viewtext.hwp'

    @cached_property
    def scripts(self):
        from hwp5.filestructure import Hwp5DistDocStorage
        return Hwp5DistDocStorage(self.olestg['Scripts'])

    def test_scripts_other_formats(self):
        from hwp5.filestructure import Hwp5DistDocStream
        jscriptversion = self.scripts['JScriptVersion']
        self.assertTrue(isinstance(jscriptversion, Hwp5DistDocStream))


class TestHwp5DistDoc(TestBase):

    hwp5file_name = 'viewtext.hwp'

    @cached_property
    def hwp5distdoc(self):
        from hwp5.filestructure import Hwp5DistDoc
        return Hwp5DistDoc(self.olestg)

    def test_conversion_for(self):
        from hwp5.filestructure import Hwp5DistDocStorage
        conversion = self.hwp5distdoc.resolve_conversion_for('Scripts')
        self.assertTrue(conversion is Hwp5DistDocStorage)

    def test_getitem(self):
        from hwp5.filestructure import Hwp5DistDocStorage
        self.assertTrue(isinstance(self.hwp5distdoc['Scripts'],
                                   Hwp5DistDocStorage))
        self.assertTrue(isinstance(self.hwp5distdoc['ViewText'],
                                   Hwp5DistDocStorage))


class TestCompressedStorage(TestBase):
    def test_getitem(self):
        from hwp5.storage import is_storage, is_stream
        stg = FS.CompressedStorage(self.olestg['BinData'])
        self.assertTrue(is_storage(stg))

        item = stg['BIN0002.jpg']
        self.assertTrue(is_stream(item))

        f = item.open()
        try:
            data = f.read()
            self.assertEquals('\xff\xd8\xff\xe0', data[0:4])
            self.assertEquals(15895, len(data))
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

    def test_docinfo_uncompressed(self):
        from hwp5.recordstream import read_record
        from hwp5.tagids import HWPTAG_DOCUMENT_PROPERTIES
        record = read_record(self.docinfo, 0)
        self.assertEquals(HWPTAG_DOCUMENT_PROPERTIES, record['tagid'])

    def test_bodytext_uncompressed(self):
        from hwp5.recordstream import read_record
        from hwp5.tagids import HWPTAG_PARA_HEADER
        record = read_record(self.bodytext['Section0'].open(), 0)
        self.assertEquals(HWPTAG_PARA_HEADER, record['tagid'])

    def test_scripts_version(self):
        hwp5file = self.hwp5file_compressed
        self.assertFalse(hwp5file.header.flags.distributable)

        JScriptVersion = self.scripts['JScriptVersion'].open().read()
        self.assertEquals(8, len(JScriptVersion))

    def test_viewtext_scripts(self):
        self.hwp5file_name = 'viewtext.hwp'
        hwp5file = self.hwp5file_compressed
        self.assertTrue(hwp5file.header.flags.distributable)

        JScriptVersion = self.scripts['JScriptVersion'].open()

        from hwp5.tagids import HWPTAG_DISTRIBUTE_DOC_DATA
        from hwp5.recordstream import read_record
        distdoc = read_record(JScriptVersion, 0)
        encrypted = JScriptVersion.read()
        self.assertEquals(HWPTAG_DISTRIBUTE_DOC_DATA, distdoc['tagid'])
        self.assertEquals(16, len(encrypted))

        #from hwp5.recordstream import record_to_json
        #print record_to_json(distdoc, sort_keys=True, indent=2)
        #from hwp5.dataio import dumpbytes
        #print 'Encrypted:', '\n'.join(dumpbytes(encrypted))


class TestHwp5File(TestBase):

    def test_init_should_accept_string_path(self):
        from hwp5.filestructure import Hwp5File
        hwp5file = Hwp5File(self.hwp5file_path)
        self.assertTrue(hwp5file['FileHeader'] is not None)

    def test_init_should_accept_olefile(self):
        from hwp5.filestructure import Hwp5File
        hwp5file = Hwp5File(self.olefile)
        self.assertTrue(hwp5file['FileHeader'] is not None)

    def test_init_should_accept_olestorage(self):
        from hwp5.filestructure import Hwp5File
        hwp5file = Hwp5File(self.olestg)
        self.assertTrue(hwp5file['FileHeader'] is not None)

    def test_fileheader(self):
        fileheader = self.hwp5file.header
        self.assertEquals((5,0,1,7), fileheader.version)
        self.assertTrue(fileheader.flags.compressed)

    def test_getitem_storage_classes(self):
        hwp5file = self.hwp5file
        self.assertTrue(isinstance(hwp5file['BinData'], FS.StorageWrapper))
        self.assertTrue(isinstance(hwp5file['BodyText'], FS.Sections))
        self.assertTrue(isinstance(hwp5file['Scripts'], FS.StorageWrapper))

    def test_prv_text(self):
        prvtext = self.hwp5file['PrvText']
        from hwp5.filestructure import PreviewText
        self.assertTrue(isinstance(prvtext, PreviewText))
        expected = '한글 2005 예제 파일입니다.'
        self.assertEquals(expected, str(prvtext)[0:len(expected)])

    def test_distdoc_layer_inserted(self):
        from hwp5.storage import ExtraItemStorage
        self.hwp5file_name = 'viewtext.hwp'
        self.assertTrue('Section0.tail' in ExtraItemStorage(self.viewtext))

    def test_unpack(self):
        from hwp5.storage import ExtraItemStorage
        from hwp5.storage import unpack
        outpath = 'test_unpack'
        import os, os.path, shutil
        if os.path.exists(outpath):
            shutil.rmtree(outpath)
        os.mkdir(outpath)
        unpack(ExtraItemStorage(self.hwp5file), outpath)

        self.assertTrue(os.path.exists('test_unpack/\x05HwpSummaryInformation'))
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
        from hwp5.storage import ExtraItemStorage
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

        import zlib
        self.assertEquals(zlib.decompress(self.olestg['DocInfo'].open().read(), -15), data)

    def test_bodytext(self):
        bodytext = self.hwp5file.bodytext
        self.assertTrue(isinstance(bodytext, FS.Sections))
        self.assertEquals(['Section0'], list(bodytext))


class TestSections(TestBase):

    @property
    def sections(self):
        from hwp5.filestructure import Sections
        return Sections(self.hwp5file.stg['BodyText'], self.hwp5file.header.version)


class TestGeneratorReader(object):
    def test_generator_reader(self):
        def data(self):
            yield 'Hello world'
            yield 'my name is'
            yield 'gen'
            yield 'reader'

        from hwp5.filestructure import GeneratorReader

        f = GeneratorReader(data())
        self.assertEquals('Hel', f.read(3))
        self.assertEquals('llo wo', f.read(6))
        self.assertEquals('rldmy', f.read(5))
        self.assertEquals(' name isgenr', f.read(12))
        self.assertEquals('eader', f.read())

        f = GeneratorReader(data())
        self.assertEquals('Hel', f.read(3))
        self.assertEquals('llo wo', f.read(6))
        self.assertEquals('rldmy', f.read(5))
        self.assertEquals(' name isgenreader', f.read())

        f = GeneratorReader(data())
        self.assertEquals('Hel', f.read(3))
        self.assertEquals('llo wo', f.read(6))
        self.assertEquals('rldmy', f.read(5))
        self.assertEquals(' name isgenreader', f.read(1000))


from hwp5.utils import cached_property
class TestUncompress(TestCase):

    @cached_property
    def original_data(self):
        f = file('/dev/urandom', 'r')
        try:
            return f.read(16384)
        finally:
            f.close()

    @cached_property
    def compressed_data(self):
        import zlib
        return zlib.compress(self.original_data)

    def test_incremental_decode(self):
        compressed_data = self.compressed_data

        from hwp5.filestructure import ZLibIncrementalDecoder
        dec = ZLibIncrementalDecoder(wbits=-15)
        data = dec.decode(compressed_data[2:2048])
        data += dec.decode(compressed_data[2048:2048+1024])
        data += dec.decode(compressed_data[2048+1024:2048+1024+4096])
        data += dec.decode(compressed_data[2048+1024+4096:], True)

        self.assertEquals(self.original_data, data)

    def test_uncompress(self):
        from StringIO import StringIO

        from hwp5.filestructure import uncompress_gen
        gen = uncompress_gen(StringIO(self.compressed_data[2:]))
        self.assertEquals(self.original_data, ''.join(gen))

        #print '-----'

        from hwp5.filestructure import uncompress

        f = uncompress(StringIO(self.compressed_data[2:]))
        g = StringIO(self.original_data)

        self.assertEquals(f.read(2048), g.read(2048))
        self.assertEquals(f.read(1024), g.read(1024))
        self.assertEquals(f.read(4096), g.read(4096))
        self.assertEquals(f.read(), g.read())
