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
