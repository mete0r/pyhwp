# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from io import BytesIO
import json

from hwp5 import recordstream as RS
from hwp5.recordstream import RecordStream
from hwp5.recordstream import dump_record
from hwp5.recordstream import read_record
from hwp5.recordstream import record_to_json
from hwp5.storage import ExtraItemStorage
from hwp5.tagids import HWPTAG_DOCUMENT_PROPERTIES
from hwp5.tagids import HWPTAG_ID_MAPPINGS
from hwp5.tagids import HWPTAG_PARA_HEADER
from hwp5.utils import cached_property

from . import test_filestructure


class TestBase(test_filestructure.TestBase):

    @property
    def hwp5file_rec(self):
        return RS.Hwp5File(self.olestg)

    hwp5file = hwp5file_rec


class TestRecord(TestBase):

    def test_read_record(self):
        docinfo_stream = self.hwp5file['DocInfo']

        record = read_record(docinfo_stream.open(), 0)
        self.assertEqual(HWPTAG_DOCUMENT_PROPERTIES, record['tagid'])

    def test_dump_record(self):
        docinfo_stream = self.hwp5file['DocInfo']
        record = read_record(docinfo_stream.open(), 0)
        stream = BytesIO()
        dump_record(stream, record)
        stream.seek(0)
        record2 = read_record(stream, 0)
        self.assertEqual(record2, record)


class TestRecordStream(TestBase):

    @cached_property
    def docinfo(self):
        return RecordStream(
            self.hwp5file_fs,
            self.hwp5file_fs,
            self.hwp5file_fs['DocInfo'],
        )

    def test_records(self):
        self.assertEqual(67, len(list(self.docinfo.records())))

    def test_records_kwargs_treegroup(self):
        records = self.docinfo.records(treegroup=1)
        self.assertEqual(66, len(records))
        self.assertEqual(HWPTAG_ID_MAPPINGS, records[0]['tagid'])

        records = self.docinfo.records(treegroup=0)
        self.assertEqual(1, len(records))
        self.assertEqual(HWPTAG_DOCUMENT_PROPERTIES, records[0]['tagid'])

        records = self.bodytext.section(0).records(treegroup=5)
        self.assertEqual(26, records[0]['seqno'])
        self.assertEqual(37, len(records))

    def test_record(self):
        record = self.docinfo.record(0)
        self.assertEqual(0, record['seqno'])

        record = self.docinfo.record(10)
        self.assertEqual(10, record['seqno'])

    def test_records_treegrouped(self):
        groups = self.docinfo.records_treegrouped()
        document_properties_treerecords = next(groups)
        self.assertEqual(1, len(document_properties_treerecords))
        idmappings_treerecords = next(groups)
        self.assertEqual(66, len(idmappings_treerecords))

        section = self.bodytext.section(0)
        for group_idx, records in enumerate(section.records_treegrouped()):
            # print group_idx, records[0]['seqno'], len(records)
            self.assertEqual(HWPTAG_PARA_HEADER, records[0]['tagid'])

    def test_records_treegrouped_as_iterable(self):
        groups = self.docinfo.records_treegrouped(group_as_list=False)
        group = next(groups)
        self.assertFalse(isinstance(group, list))

    def test_records_treegroped_as_list(self):
        groups = self.docinfo.records_treegrouped()
        group = next(groups)
        self.assertTrue(isinstance(group, list))

    def test_records_treegroup(self):
        records = self.docinfo.records_treegroup(1)
        self.assertEqual(66, len(records))
        self.assertEqual(HWPTAG_ID_MAPPINGS, records[0]['tagid'])

        records = self.docinfo.records_treegroup(0)
        self.assertEqual(1, len(records))
        self.assertEqual(HWPTAG_DOCUMENT_PROPERTIES, records[0]['tagid'])

        records = self.bodytext.section(0).records_treegroup(5)
        self.assertEqual(26, records[0]['seqno'])
        self.assertEqual(37, len(records))


class TestHwp5File(TestBase):

    def test_if_hwp5file_contains_other_formats(self):
        stg = ExtraItemStorage(self.hwp5file)
        self.assertTrue('DocInfo.records' in list(stg))

    def test_docinfo(self):
        docinfo = self.hwp5file.docinfo
        self.assertTrue(isinstance(docinfo, RS.RecordStream))
        records = list(docinfo.records())
        self.assertEqual(67, len(records))

    def test_bodytext(self):
        bodytext = self.hwp5file.bodytext
        self.assertTrue(isinstance(bodytext, RS.Sections))
        stg = ExtraItemStorage(bodytext)
        self.assertEqual(['Section0', 'Section0.records'], list(stg))


class TestJson(TestBase):
    def test_record_to_json(self):
        record = next(self.hwp5file.docinfo.records())
        json_string = record_to_json(record)
        jsonobject = json.loads(json_string)
        self.assertEqual(16, jsonobject['tagid'])
        self.assertEqual(0, jsonobject['level'])
        self.assertEqual(26, jsonobject['size'])
        self.assertEqual(['01 00 01 00 01 00 01 00 01 00 01 00 01 00 00 00',
                          '00 00 07 00 00 00 05 00 00 00'],
                         jsonobject['payload'])
        self.assertEqual(0, jsonobject['seqno'])
        self.assertEqual('HWPTAG_DOCUMENT_PROPERTIES', jsonobject['tagname'])

    def test_generate_json(self):
        records_json = self.hwp5file.docinfo.records_json()
        json_string = ''.join(records_json.generate())

        jsonobject = json.loads(json_string)
        self.assertEqual(67, len(jsonobject))
