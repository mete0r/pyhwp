# -*- coding: utf-8 -*-

from . import test_filestructure
from . import recordstream as RS
from .utils import cached_property

class TestBase(test_filestructure.TestBase):

    @property
    def hwp5file_rec(self):
        return RS.Hwp5File(self.olestg)

    hwp5file = hwp5file_rec


class TestRecord(TestBase):

    def test_read_record(self):
        from .recordstream import read_record
        from .tagids import HWPTAG_DOCUMENT_PROPERTIES
        docinfo_stream = self.hwp5file['DocInfo']

        record = read_record(docinfo_stream.open(), 0)
        self.assertEquals(HWPTAG_DOCUMENT_PROPERTIES, record['tagid'])


class TestRecordStream(TestBase):

    @cached_property
    def docinfo(self):
        from .recordstream import RecordStream
        return RecordStream(self.hwp5file['DocInfo'],
                            self.hwp5file.header.version)

    def test_records(self):
        self.assertEquals(67, len(list(self.docinfo.records())))

    def test_record(self):
        record = self.docinfo.record(0)
        self.assertEquals(0, record['seqno'])

        record = self.docinfo.record(10)
        self.assertEquals(10, record['seqno'])


class TestHwp5File(TestBase):

    def test_if_hwp5file_contains_other_formats(self):
        from .storage import ExtraItemStorage
        stg = ExtraItemStorage(self.hwp5file)
        self.assertTrue('DocInfo.records' in list(stg))

    def test_docinfo(self):
        docinfo = self.hwp5file.docinfo
        self.assertTrue(isinstance(docinfo, RS.RecordStream))
        records = list(docinfo.records())
        self.assertEquals(67, len(records))

    def test_bodytext(self):
        from .storage import ExtraItemStorage
        bodytext = self.hwp5file.bodytext
        self.assertTrue(isinstance(bodytext, RS.Sections))
        stg = ExtraItemStorage(bodytext)
        self.assertEquals(['Section0', 'Section0.records'], list(stg))


class TestJson(TestBase):
    def test_record_to_json(self):
        from .recordstream import record_to_json
        import simplejson
        record = self.hwp5file.docinfo.records().next()
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
        records = self.hwp5file.docinfo.records()
        json = ''.join(generate_simplejson_dumps(records))

        jsonobject = simplejson.loads(json)
        self.assertEquals(67, len(jsonobject))
