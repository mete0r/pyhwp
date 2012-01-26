# -*- coding: utf-8 -*-
from unittest import TestCase
from hwp5 import filestructure as FS
from OleFileIO_PL import OleFileIO
import OleFileIO_PL

sample_filename = '../../../samples/sample-5017.hwp'
nonole_filename = '../../../README.markdown'

class TestModuleFunctions(TestCase):

    def test_is_hwp5file(self):
        assert FS.is_hwp5file(sample_filename)
        assert not FS.is_hwp5file(nonole_filename)

    def test_open_pseudostreams(self):
        olefile = OleFileIO(sample_filename)
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

        olefile = OleFileIO('../../../samples/viewtext.hwp')
        self.assertRaises(IndexError, FS.open_viewtext, olefile, 1)
        assert FS.open_viewtext(olefile, 0)
        head = FS.open_viewtext_head(olefile, 0)
        assert head
        assert len(head.read()) == 4+256
        assert FS.open_viewtext_tail(olefile, 0)

    def test_list_streams(self):
        olefile = OleFileIO(sample_filename)
        assert 'DocInfo' in list(FS.list_streams(olefile))

    def test_list_sections(self):
        olefile = OleFileIO(sample_filename)
        assert [0] == FS.list_sections(olefile)

    def test_list_bindata(self):
        olefile = OleFileIO(sample_filename)
        assert set(['BIN0002.jpg', 'BIN0002.png', 'BIN0003.png']) == set(FS.list_bindata(olefile))

    def test_get_fileheader(self):
        olefile = OleFileIO(sample_filename)
        fileheader = FS.get_fileheader(olefile)
        assert isinstance(fileheader, FS.FileHeader)

    def test_open(self):
        f = FS.open(sample_filename)
        assert isinstance(f, FS.File)

        self.assertRaises(FS.BadFormatError, FS.open, nonole_filename)

    def test_listdir(self):
        olefile = OleFileIO(sample_filename)
        hwpfile = FS.File(olefile)
        self.assertEquals(sorted(['Section0']),
                          sorted(hwpfile.listdir('BodyText')))
        self.assertEquals(sorted(['BIN0002.jpg', 'BIN0002.png', 'BIN0003.png']),
                          sorted(hwpfile.listdir('BinData')))
        self.assertEquals(sorted(['DefaultJScript', 'JScriptVersion']),
                          sorted(hwpfile.listdir('Scripts')))

        expected = ['FileHeader', 'BodyText', 'BinData', 'Scripts', 'DocOptions', 'DocInfo',
                    'PrvText', 'PrvImage', '\x05HwpSummaryInformation']
        self.assertEquals(sorted(expected), sorted(hwpfile.listdir('/')))
        self.assertEquals(sorted(expected), sorted(hwpfile.listdir('')))

    def test_is_storage(self):
        olefile = OleFileIO(sample_filename)
        hwpfile = FS.File(olefile)
        self.assertTrue(hwpfile.is_storage('BodyText'))
        self.assertTrue(hwpfile.is_storage('BinData'))
        self.assertTrue(hwpfile.is_storage('Scripts'))

    def test_is_stream(self):
        olefile = OleFileIO(sample_filename)
        hwpfile = FS.File(olefile)
        self.assertTrue(hwpfile.is_stream('BodyText/Section0'))
        self.assertTrue(hwpfile.is_stream('BinData/BIN0002.jpg'))
        self.assertTrue(hwpfile.is_stream('BinData/BIN0002.png'))
        self.assertTrue(hwpfile.is_stream('BinData/BIN0003.png'))
        self.assertTrue(hwpfile.is_stream('Scripts/DefaultJScript'))
        self.assertTrue(hwpfile.is_stream('Scripts/JScriptVersion'))

    def test_walk(self):
        olefile = OleFileIO(sample_filename)
        hwpfile = FS.File(olefile)
        from hwp5.filestructure import walk

        result = list(walk(hwpfile))
        self.assertEquals('', result[0][0])
        self.assertEquals(sorted(['BinData', 'BodyText', 'DocOptions', 'Scripts']),
                          sorted(result[0][1]))
        self.assertEquals(sorted(['\x05HwpSummaryInformation', 'DocInfo', 'FileHeader', 'PrvImage', 'PrvText']),
                          sorted(result[0][2]))

        for dirpath, dirs, files in walk(hwpfile):
            print dirpath, dirs, files


class TestBase(TestCase):

    @property
    def olefile(self):
        return OleFileIO(sample_filename)

    @property
    def olestg(self):
        return FS.OleStorage(self.olefile)


class TestOleStorage(TestBase):

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
            a = olestg['non-exists']
            self.fail('KeyError expected')
        except KeyError:
            pass

        fileheader = olestg['FileHeader']
        self.assertTrue(hasattr(fileheader, 'read'))
        
        bindata = olestg['BinData']
        self.assertTrue(isinstance(bindata, FS.OleStorage))
        self.assertEquals('BinData', bindata.path)

        self.assertEquals(sorted(['BIN0002.jpg', 'BIN0002.png', 'BIN0003.png']),
                          sorted(iter(bindata)))

        bin0002 = bindata['BIN0002.jpg']
        self.assertTrue(hasattr(bin0002, 'read'))


    def test_iter_storage_leafs(self):
        from hwp5.filestructure import iter_storage_leafs
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


class TestCompressedStorage(TestBase):
    def test_getitem(self):
        stg = FS.CompressedStorage(self.olestg['BinData'])
        data = stg['BIN0002.jpg'].read()
        self.assertEquals('\xff\xd8\xff\xe0', data[0:4])
        self.assertEquals(15895, len(data))


class TestHwp5File(TestBase):

    @property
    def hwp5file(self):
        return FS.Hwp5File(self.olestg)

    def test_fileheader(self):
        fileheader = self.hwp5file.header
        self.assertEquals((5,0,1,7), fileheader.version)
        self.assertTrue(fileheader.flags.compressed)

    def test_getitem_storage_classes(self):
        hwp5file = self.hwp5file
        self.assertTrue(isinstance(hwp5file['BinData'], FS.Hwp5File.BinDataStorage))
        self.assertTrue(isinstance(hwp5file['BodyText'], FS.Hwp5File.BodyTextStorage))
        self.assertTrue(isinstance(hwp5file['Scripts'], FS.Hwp5File.ScriptsStorage))

    def test_prv_text(self):
        prvtext = self.hwp5file['PrvText.utf8']
        expected = '한글 2005 예제 파일입니다.'
        self.assertEquals(expected, prvtext.read()[0:len(expected)])

    def test_unpack(self):
        outpath = 'sample-5017'
        import os, os.path, shutil
        if os.path.exists(outpath):
            shutil.rmtree(outpath)
        os.mkdir(outpath)
        FS.unpack(self.hwp5file, outpath)

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

    def test_docinfo(self):
        hwp5file = self.hwp5file
        docinfo = hwp5file.docinfo.open()
        try:
            data = docinfo.read()
        finally:
            docinfo.close()

        import zlib
        self.assertEquals(zlib.decompress(self.olestg['DocInfo'].read(), -15), data)

    def test_bodytext(self):
        bodytext = self.hwp5file.bodytext
        self.assertTrue(isinstance(bodytext, FS.SectionStorage))
        self.assertEquals(['Section0'], list(bodytext))
        section0 = bodytext.section(0)
        self.assertEquals([0], bodytext.section_indexes())
        self.assertEquals(1, len(bodytext.sections))


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

        print '-----'

        from .filestructure import uncompress

        f = uncompress(StringIO(self.compressed_data[2:]))
        g = StringIO(self.original_data)

        self.assertEquals(f.read(2048), g.read(2048))
        self.assertEquals(f.read(1024), g.read(1024))
        self.assertEquals(f.read(4096), g.read(4096))
        self.assertEquals(f.read(), g.read())
