# -*- coding: utf-8 -*-

from hwp5.tests import test_filestructure
from hwp5 import recordstream as RS
from hwp5.utils import cached_property

class TestBase(test_filestructure.TestBase):

    @property
    def hwp5file_rec(self):
        return RS.Hwp5File(self.olestg)

    hwp5file = hwp5file_rec


class TestRecord(TestBase):

    def test_read_record(self):
        from hwp5.recordstream import read_record
        from hwp5.tagids import HWPTAG_DOCUMENT_PROPERTIES
        docinfo_stream = self.hwp5file['DocInfo']

        record = read_record(docinfo_stream.open(), 0)
        self.assertEquals(HWPTAG_DOCUMENT_PROPERTIES, record['tagid'])

    def test_dump_record(self):
        from hwp5.recordstream import dump_record
        from hwp5.recordstream import read_record
        docinfo_stream = self.hwp5file['DocInfo']
        record = read_record(docinfo_stream.open(), 0)
        from StringIO import StringIO
        stream = StringIO()
        dump_record(stream, record)
        stream.seek(0)
        record2 = read_record(stream, 0)
        self.assertEquals(record2, record)


class TestRecordStream(TestBase):

    @cached_property
    def docinfo(self):
        from hwp5.recordstream import RecordStream
        return RecordStream(self.hwp5file_fs['DocInfo'],
                            self.hwp5file_fs.header.version)

    def test_records(self):
        self.assertEquals(67, len(list(self.docinfo.records())))

    def test_records_kwargs_treegroup(self):
        from hwp5.tagids import HWPTAG_ID_MAPPINGS
        records = self.docinfo.records(treegroup=1)
        self.assertEquals(66, len(records))
        self.assertEquals(HWPTAG_ID_MAPPINGS, records[0]['tagid'])

        from hwp5.tagids import HWPTAG_DOCUMENT_PROPERTIES
        records = self.docinfo.records(treegroup=0)
        self.assertEquals(1, len(records))
        self.assertEquals(HWPTAG_DOCUMENT_PROPERTIES, records[0]['tagid'])

        records = self.bodytext.section(0).records(treegroup=5)
        self.assertEquals(26, records[0]['seqno'])
        self.assertEquals(37, len(records))

    def test_record(self):
        record = self.docinfo.record(0)
        self.assertEquals(0, record['seqno'])

        record = self.docinfo.record(10)
        self.assertEquals(10, record['seqno'])

    def test_records_treegrouped(self):
        groups = self.docinfo.records_treegrouped()
        document_properties_treerecords = groups.next()
        self.assertEquals(1, len(document_properties_treerecords))
        idmappings_treerecords = groups.next()
        self.assertEquals(66, len(idmappings_treerecords))

        from hwp5.tagids import HWPTAG_PARA_HEADER
        section = self.bodytext.section(0)
        for group_idx, records in enumerate(section.records_treegrouped()):
            #print group_idx, records[0]['seqno'], len(records)
            self.assertEquals(HWPTAG_PARA_HEADER, records[0]['tagid'])

    def test_records_treegrouped_as_iterable(self):
        groups = self.docinfo.records_treegrouped(group_as_list=False)
        group = groups.next()
        self.assertFalse(isinstance(group, list))

    def test_records_treegroped_as_list(self):
        groups = self.docinfo.records_treegrouped()
        group = groups.next()
        self.assertTrue(isinstance(group, list))

    def test_records_treegroup(self):
        from hwp5.tagids import HWPTAG_ID_MAPPINGS
        records = self.docinfo.records_treegroup(1)
        self.assertEquals(66, len(records))
        self.assertEquals(HWPTAG_ID_MAPPINGS, records[0]['tagid'])

        from hwp5.tagids import HWPTAG_DOCUMENT_PROPERTIES
        records = self.docinfo.records_treegroup(0)
        self.assertEquals(1, len(records))
        self.assertEquals(HWPTAG_DOCUMENT_PROPERTIES, records[0]['tagid'])

        records = self.bodytext.section(0).records_treegroup(5)
        self.assertEquals(26, records[0]['seqno'])
        self.assertEquals(37, len(records))


class TestHwp5File(TestBase):

    def test_if_hwp5file_contains_other_formats(self):
        from hwp5.storage import ExtraItemStorage
        stg = ExtraItemStorage(self.hwp5file)
        self.assertTrue('DocInfo.records' in list(stg))

    def test_docinfo(self):
        docinfo = self.hwp5file.docinfo
        self.assertTrue(isinstance(docinfo, RS.RecordStream))
        records = list(docinfo.records())
        self.assertEquals(67, len(records))

    def test_bodytext(self):
        from hwp5.storage import ExtraItemStorage
        bodytext = self.hwp5file.bodytext
        self.assertTrue(isinstance(bodytext, RS.Sections))
        stg = ExtraItemStorage(bodytext)
        self.assertEquals(['Section0', 'Section0.records'], list(stg))


class TestJson(TestBase):
    def test_record_to_json(self):
        from hwp5.recordstream import record_to_json
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
        import simplejson
        records_json = self.hwp5file.docinfo.records_json()
        json = ''.join(records_json.generate())

        jsonobject = simplejson.loads(json)
        self.assertEquals(67, len(jsonobject))
