# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import logging
import os.path
import shutil

from hwp5.errors import InvalidOleStorageError
from hwp5.storage import is_storage
from hwp5.storage import is_directory
from hwp5.storage import is_stream
from hwp5.storage import unpack

from .fixtures import get_fixture_path


logger = logging.getLogger(__name__)


class OleStorageTestMixin(object):

    hwp5file_name = 'sample-5017.hwp'

    def get_fixture_file(self, filename):
        return get_fixture_path(filename)

    @property
    def hwp5file_path(self):
        return self.get_fixture_file(self.hwp5file_name)

    @property
    def olestg(self):
        return self.olestorage_opener.open_storage(self.hwp5file_path)

    def test_open_storage(self):
        if self.olestorage_opener is None:
            logger.warning('%s: skipped', self.id())
            return

        nonolefile = self.get_fixture_file('nonole.txt')
        self.assertRaises(
            InvalidOleStorageError,
            self.olestorage_opener.open_storage,
            nonolefile
        )

        olestg = self.olestorage_opener.open_storage(self.hwp5file_path)
        self.assertTrue(is_storage(olestg))

    def test_getitem0(self):
        if self.olestorage_opener is None:
            logger.warning('%s: skipped', self.id())
            return
        olestg = self.olestg
        self.assertTrue(is_storage(olestg))
        # self.assertEqual('', olestg.path)

        docinfo = olestg['DocInfo']
        self.assertTrue(is_stream(docinfo))
        # self.assertEqual('DocInfo', docinfo.path)

        bodytext = olestg['BodyText']
        self.assertTrue(is_directory(bodytext))
        # self.assertEqual('BodyText', bodytext.path)

        section = bodytext['Section0']
        self.assertTrue(is_stream(section))
        # self.assertEqual('BodyText/Section0', section.path)

        f = section.open()
        try:
            data = f.read()
            self.assertEqual(1529, len(data))
        finally:
            f.close()

        try:
            bodytext['nonexists']
            self.fail('KeyError expected')
        except KeyError:
            pass

    def test_iter(self):
        if self.olestorage_opener is None:
            logger.warning('%s: skipped', self.id())
            return
        olestg = self.olestg
        gen = iter(olestg)
        # import types
        # self.assertTrue(isinstance(gen, types.GeneratorType))
        expected = ['FileHeader', 'BodyText', 'BinData', 'Scripts',
                    'DocOptions', 'DocInfo', 'PrvText', 'PrvImage',
                    '\x05HwpSummaryInformation']
        self.assertEqual(sorted(expected), sorted(gen))

    def test_getitem(self):
        if self.olestorage_opener is None:
            logger.warning('%s: skipped', self.id())
            return

        olestg = self.olestg

        try:
            olestg['non-exists']
            self.fail('KeyError expected')
        except KeyError:
            pass

        fileheader = olestg['FileHeader']
        self.assertTrue(hasattr(fileheader, 'open'))

        bindata = olestg['BinData']
        self.assertTrue(is_directory(bindata))
        # self.assertEqual('BinData', bindata.path)

        self.assertEqual(sorted(['BIN0002.jpg', 'BIN0002.png',
                                 'BIN0003.png']),
                         sorted(iter(bindata)))

        bin0002 = bindata['BIN0002.jpg']
        self.assertTrue(hasattr(bin0002, 'open'))

    def test_stream_open(self):
        if self.olestorage_opener is None:
            logger.warning('%s: skipped', self.id())
            return
        olestg = self.olestg

        fileheader = olestg['FileHeader']
        self.assertTrue(hasattr(fileheader, 'open'))

        stream1 = fileheader.open()
        stream2 = fileheader.open()

        x = stream1.read(4)
        self.assertEqual(4, len(x))
        self.assertEqual(4, stream1.tell())

        self.assertEqual(0, stream2.tell())

        stream1.seek(0)
        self.assertEqual(0, stream1.tell())

    def test_unpack(self):
        if self.olestorage_opener is None:
            logger.warning('%s: skipped', self.id())
            return

        if os.path.exists('5017'):
            shutil.rmtree('5017')
        os.mkdir('5017')
        unpack(self.olestg, '5017')

        self.assertTrue(os.path.exists('5017/_05HwpSummaryInformation'))
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
