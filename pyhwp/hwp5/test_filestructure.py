# -*- coding: utf-8 -*-
from unittest import TestCase
from hwp5 import filestructure as FS
from OleFileIO_PL import OleFileIO
from .utils import cached_property

class TestBase(TestCase):

    fixtures_dir = 'fixtures'
    hwp5file_name = 'sample-5017.hwp'

    @cached_property
    def hwp5file_path(self):
        import os.path
        return os.path.join(self.fixtures_dir,
                            self.hwp5file_name)

    @property
    def olefile(self):
        return OleFileIO(self.hwp5file_path)

    @property
    def olestg(self):
        return FS.OleStorage(self.olefile)

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
        import os.path
        nonole_filename = os.path.join(self.fixtures_dir, 'nonole.txt')
        assert not FS.is_hwp5file(nonole_filename)

    def test_open_pseudostreams(self):
        olefile = OleFileIO(self.hwp5file_path)
        assert FS.open_fileheader(olefile)
        assert FS.open_summaryinfo(olefile)
        assert FS.open_previewtext(olefile)
        assert FS.open_previewimage(olefile)
        assert FS.open_docinfo(olefile)
        assert FS.open_bodytext(olefile, 0)
        self.assertRaises(IndexError, FS.open_bodytext, olefile, 1)
        assert FS.open_bindata(olefile, 'BIN0002.jpg')
        self.assertRaises(KeyError, FS.open_bindata, olefile, 'BIN0000.xxx')
        assert FS.open_script(olefile, 'DefaultJScript')
        self.assertRaises(KeyError, FS.open_script, olefile, 'NOTEXISTS')

        import os.path
        olefile = OleFileIO(os.path.join(self.fixtures_dir, 'viewtext.hwp'))
        self.assertRaises(IndexError, FS.open_viewtext, olefile, 1)
        assert FS.open_viewtext(olefile, 0)
        head = FS.open_viewtext_head(olefile, 0)
        assert head
        assert len(head.read()) == 4+256
        assert FS.open_viewtext_tail(olefile, 0)

    def test_list_streams(self):
        olefile = OleFileIO(self.hwp5file_path)
        assert 'DocInfo' in list(FS.list_streams(olefile))

    def test_list_sections(self):
        olefile = OleFileIO(self.hwp5file_path)
        assert [0] == FS.list_sections(olefile)

    def test_list_bindata(self):
        olefile = OleFileIO(self.hwp5file_path)
        assert set(['BIN0002.jpg', 'BIN0002.png', 'BIN0003.png']) == set(FS.list_bindata(olefile))

    def test_get_fileheader(self):
        olefile = OleFileIO(self.hwp5file_path)
        fileheader = FS.get_fileheader(olefile)
        assert isinstance(fileheader, FS.FileHeader)


class TestOleStorage(TestBase):

    def test_getitem0(self):
        olestg = self.olestg
        self.assertEquals(None, olestg.name)
        self.assertEquals(None, olestg.parent)
        self.assertTrue(olestg.is_storage())
        self.assertEquals('', olestg.path)

        docinfo = olestg['DocInfo']
        self.assertEquals('DocInfo', docinfo.name)
        self.assertTrue(docinfo.is_stream())
        self.assertTrue(docinfo.parent is olestg)
        self.assertEquals('DocInfo', docinfo.path)

        bodytext = olestg['BodyText']
        self.assertEquals('BodyText', bodytext.name)
        self.assertTrue(bodytext.parent is olestg)
        self.assertTrue(bodytext.is_storage())
        self.assertEquals('BodyText', bodytext.path)

        section = bodytext['Section0']
        self.assertEquals('Section0', section.name)
        self.assertTrue(section.is_stream())
        self.assertTrue(section.parent is bodytext)
        self.assertEquals('BodyText/Section0', section.path)

        f = section.open()
        try:
            data = f.read()
            self.assertEquals(1529, len(data))
        finally:
            f.close()

        try:
            bodytext['nonexists']
            self.fail('KeyError expected')
        except KeyError:
            pass

    def test_init_should_receive_string_olefile(self):
        from .filestructure import OleStorage
        import os.path
        olestg = OleStorage(os.path.join(self.fixtures_dir,
                                         self.hwp5file_name))
        self.assertTrue(olestg['FileHeader'] is not None)

    def test_iter(self):
        olestg = self.olestg
        gen = iter(olestg)
        import types
        self.assertTrue(isinstance(gen, types.GeneratorType))
        expected = ['FileHeader', 'BodyText', 'BinData', 'Scripts', 'DocOptions', 'DocInfo',
                    'PrvText', 'PrvImage', '\x05HwpSummaryInformation']
        self.assertEquals(sorted(expected), sorted(gen))

    def test_getitem(self):
        olestg = self.olestg

        try:
            olestg['non-exists']
            self.fail('KeyError expected')
        except KeyError:
            pass

        fileheader = olestg['FileHeader']
        self.assertTrue(hasattr(fileheader, 'open'))
        
        bindata = olestg['BinData']
        self.assertTrue(isinstance(bindata, FS.OleStorage))
        self.assertEquals('BinData', bindata.path)

        self.assertEquals(sorted(['BIN0002.jpg', 'BIN0002.png', 'BIN0003.png']),
                          sorted(iter(bindata)))

        bin0002 = bindata['BIN0002.jpg']
        self.assertTrue(hasattr(bin0002, 'open'))


    def test_iter_storage_leafs(self):
        from hwp5.storage import iter_storage_leafs
        result = iter_storage_leafs(self.olestg)
        expected = ['\x05HwpSummaryInformation', 'BinData/BIN0002.jpg', 'BinData/BIN0002.png', 'BinData/BIN0003.png',
                    'BodyText/Section0', 'DocInfo', 'DocOptions/_LinkDoc', 'FileHeader', 'PrvImage', 'PrvText',
                    'Scripts/DefaultJScript', 'Scripts/JScriptVersion']
        self.assertEquals(sorted(expected), sorted(result))

    def test_unpack(self):
        from hwp5.filestructure import unpack
        import shutil
        import os, os.path

        if os.path.exists('5017'):
            shutil.rmtree('5017')
        os.mkdir('5017')
        unpack(self.olestg, '5017')

        self.assertTrue(os.path.exists('5017/\x05HwpSummaryInformation'))
        self.assertTrue(os.path.exists('5017/BinData/BIN0002.jpg'))
        self.assertTrue(os.path.exists('5017/BinData/BIN0002.png'))
        self.assertTrue(os.path.exists('5017/BinData/BIN0003.png'))
        self.assertTrue(os.path.exists('5017/BodyText/Section0'))
        self.assertTrue(os.path.exists('5017/DocInfo'))
        self.assertTrue(os.path.exists('5017/DocOptions/_LinkDoc'))
        self.assertTrue(os.path.exists('5017/FileHeader'))
        self.assertTrue(os.path.exists('5017/PrvImage'))
        self.assertTrue(os.path.exists('5017/PrvText'))
        self.assertTrue(os.path.exists('5017/Scripts/DefaultJScript'))
        self.assertTrue(os.path.exists('5017/Scripts/JScriptVersion'))


class TestHwp5FileBase(TestBase):

    @cached_property
    def hwp5file_base(self):
        from .filestructure import Hwp5FileBase
        return Hwp5FileBase(self.olestg)

    def test_header(self):
        from .filestructure import FileHeader
        header = self.hwp5file_base.header
        self.assertTrue(isinstance(header, FileHeader))


class TestHwp5DistDocStream(TestBase):

    hwp5file_name = 'viewtext.hwp'

    @cached_property
    def jscriptversion(self):
        from .filestructure import Hwp5DistDocStream
        return Hwp5DistDocStream(self.olestg['Scripts']['JScriptVersion'],
                                 self.hwp5file.header.version)

    def test_head_record(self):
        from .tagids import HWPTAG_DISTRIBUTE_DOC_DATA
        record = self.jscriptversion.head_record()
        self.assertEquals(HWPTAG_DISTRIBUTE_DOC_DATA, record['tagid'])

    def test_head_record_stream(self):
        from .tagids import HWPTAG_DISTRIBUTE_DOC_DATA
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
        from .filestructure import Hwp5DistDocStorage
        return Hwp5DistDocStorage(self.olestg['Scripts'])

    def test_resolve_baseitemobject(self):
        version = self.scripts.resolve_baseitemobject('JScriptVersion')
        self.assertTrue(version is not None)
        self.assertEquals(4+256+16, len(version.open().read()))
        self.assertTrue(version.other_formats() is not None)

    def test_resolve_other_formats_for_version(self):
        other_formats = self.scripts.resolve_other_formats_for('JScriptVersion')
        self.assertTrue(other_formats is not None)
        self.assertEquals(set(['.head.record', '.head', '.tail']),
                          set(other_formats.keys()))


class TestHwp5DistDoc(TestBase):

    hwp5file_name = 'viewtext.hwp'

    @cached_property
    def hwp5distdoc(self):
        from .filestructure import Hwp5DistDoc
        return Hwp5DistDoc(self.olestg)

    def test_conversion_for(self):
        from .filestructure import Hwp5DistDocStorage
        conversion = self.hwp5distdoc.resolve_conversion_for('Scripts')
        self.assertTrue(conversion is Hwp5DistDocStorage)

    def test_getitem(self):
        from .filestructure import Hwp5DistDocStorage
        self.assertTrue(isinstance(self.hwp5distdoc['Scripts'],
                                   Hwp5DistDocStorage))
        self.assertTrue(isinstance(self.hwp5distdoc['ViewText'],
                                   Hwp5DistDocStorage))


class TestCompressedStorage(TestBase):
    def test_getitem(self):
        stg = FS.CompressedStorage(self.olestg['BinData'])
        self.assertTrue(stg.is_storage())
        self.assertTrue(stg.name is None)
        self.assertTrue(stg.parent is None)

        item = stg['BIN0002.jpg']
        self.assertTrue(item.is_stream())
        self.assertEquals('BIN0002.jpg', item.name)
        #self.assertTrue(item.parent is stg)

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
        from .recordstream import read_record
        from .tagids import HWPTAG_DOCUMENT_PROPERTIES
        record = read_record(self.docinfo, 0)
        self.assertEquals(HWPTAG_DOCUMENT_PROPERTIES, record['tagid'])

    def test_bodytext_uncompressed(self):
        from .recordstream import read_record
        from .tagids import HWPTAG_PARA_HEADER
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

        from .tagids import HWPTAG_DISTRIBUTE_DOC_DATA
        from .recordstream import read_record
        distdoc = read_record(JScriptVersion, 0)
        encrypted = JScriptVersion.read()
        self.assertEquals(HWPTAG_DISTRIBUTE_DOC_DATA, distdoc['tagid'])
        self.assertEquals(16, len(encrypted))

        #from .recordstream import record_to_json
        #print record_to_json(distdoc, sort_keys=True, indent=2)
        #from .dataio import dumpbytes
        #print 'Encrypted:', '\n'.join(dumpbytes(encrypted))


class TestHwp5File(TestBase):

    def test_init_should_accept_string_path(self):
        from .filestructure import Hwp5File
        hwp5file = Hwp5File(self.hwp5file_path)
        self.assertTrue(hwp5file['FileHeader'] is not None)

    def test_init_should_accept_olefile(self):
        from .filestructure import Hwp5File
        hwp5file = Hwp5File(self.olefile)
        self.assertTrue(hwp5file['FileHeader'] is not None)

    def test_init_should_accept_olestorage(self):
        from .filestructure import Hwp5File
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
        prvtext = self.hwp5file['PrvText.utf8']
        expected = '한글 2005 예제 파일입니다.'
        self.assertEquals(expected, prvtext.open().read()[0:len(expected)])

    def test_distdoc_layer_inserted(self):
        self.hwp5file_name = 'viewtext.hwp'
        self.assertTrue('Section0.tail' in self.viewtext)

    def test_unpack(self):
        outpath = 'test_unpack'
        import os, os.path, shutil
        if os.path.exists(outpath):
            shutil.rmtree(outpath)
        os.mkdir(outpath)
        FS.unpack(self.hwp5file, outpath)

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
        self.assertTrue('PrvText.utf8' in list(self.hwp5file))

    def test_resolve_conversion_for_bodytext(self):
        self.assertTrue(self.hwp5file.resolve_conversion_for('BodyText'))

    def test_resolve_other_formats_for_preview_text(self):
        self.assertTrue(self.hwp5file.resolve_other_formats_for('PrvText') is not None)

    def test_resolve_other_formats_for_docinfo(self):
        self.assertTrue(self.hwp5file.resolve_other_formats_for('DocInfo') is not None)

    def test_docinfo(self):
        hwp5file = self.hwp5file
        self.assertTrue(isinstance(hwp5file.docinfo, FS.Hwp5Object))
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
        from .filestructure import Sections
        return Sections(self.hwp5file.stg['BodyText'], self.hwp5file.header.version)

    def test_resolve_other_formats_for_section(self):
        self.assertTrue(self.sections.resolve_other_formats_for('Section0') is not None)

    def test_resolve_other_formats_for_nonsection(self):
        self.assertTrue(self.sections.resolve_other_formats_for('NoneSection') is None)


class TestGeneratorReader(object):
    def test_generator_reader(self):
        def data(self):
            yield 'Hello world'
            yield 'my name is'
            yield 'gen'
            yield 'reader'

        from .filestructure import GeneratorReader

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


from .utils import cached_property
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

        from .filestructure import ZLibIncrementalDecoder
        dec = ZLibIncrementalDecoder(wbits=-15)
        data = dec.decode(compressed_data[2:2048])
        data += dec.decode(compressed_data[2048:2048+1024])
        data += dec.decode(compressed_data[2048+1024:2048+1024+4096])
        data += dec.decode(compressed_data[2048+1024+4096:], True)

        self.assertEquals(self.original_data, data)

    def test_uncompress(self):
        from StringIO import StringIO

        from .filestructure import uncompress_gen
        gen = uncompress_gen(StringIO(self.compressed_data[2:]))
        self.assertEquals(self.original_data, ''.join(gen))

        #print '-----'

        from .filestructure import uncompress

        f = uncompress(StringIO(self.compressed_data[2:]))
        g = StringIO(self.original_data)

        self.assertEquals(f.read(2048), g.read(2048))
        self.assertEquals(f.read(1024), g.read(1024))
        self.assertEquals(f.read(4096), g.read(4096))
        self.assertEquals(f.read(), g.read())
