# -*- coding: utf-8 -*-

from . import test_filestructure
from . import recordstream as RS

class TestBase(test_filestructure.TestBase):

    @property
    def hwp5file_rec(self):
        return RS.Hwp5File(self.olestg)

    def test_if_hwp5file_contains_other_formats(self):
        self.assertTrue('DocInfo.rec' in list(self.hwp5file_rec))

    def test_docinfo(self):
        docinfo = self.hwp5file_rec.docinfo
        self.assertTrue(isinstance(docinfo, RS.RecordStream))
        records = list(docinfo.records())
        self.assertEquals(67, len(records))

    def test_bodytext(self):
        bodytext = self.hwp5file_rec.bodytext
        self.assertTrue(isinstance(bodytext, RS.Sections))
        self.assertEquals(['Section0', 'Section0.rec'], list(bodytext.open()))
