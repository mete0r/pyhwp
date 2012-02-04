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

class TestJson(TestBase):
    def test_record_to_json(self):
        from .recordstream import record_to_json
        import simplejson
        record = self.hwp5file_rec.docinfo.records().next()
        json = record_to_json(record)
        jsonobject = simplejson.loads(json)
        self.assertEquals(16, jsonobject['tagid'])
        self.assertEquals(0, jsonobject['level'])
        self.assertEquals(26, jsonobject['size'])
        self.assertEquals(['01 00 01 00 01 00 01 00 01 00 01 00 01 00 00 00',
                           '00 00 07 00 00 00 05 00 00 00'],
                          jsonobject['payload'])
        self.assertEquals(0, jsonobject['seqno'])
        self.assertEquals('HWPTAG_DOCUMENT_PROPERTIES', jsonobject['tagname'])

    def test_generate_simplejson_dumps(self):
        from .recordstream import generate_simplejson_dumps
        import simplejson
        records = self.hwp5file_rec.docinfo.records()
        json = ''.join(generate_simplejson_dumps(records))

        jsonobject = simplejson.loads(json)
        self.assertEquals(67, len(jsonobject))
