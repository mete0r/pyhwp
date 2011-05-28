from unittest import TestCase, makeSuite
from StringIO import StringIO

from .recordstream import Record, read_records
from .models import tag_models, parse_models_pass1, parse_models_pass2, pass2_events, pass2_parented, pass2_morph
from .models import DocumentContext as DC, BinData, BinEmbedded, TableControl, ListHeader, TableCaption, TableCell, TableBody
from . import models

class BinEmbeddedTest(TestCase):
    ctx = DC()
    stream = StringIO('\x12\x04\xc0\x00\x01\x00\x02\x00\x03\x00\x6a\x00\x70\x00\x67\x00')
    def testParsePass1(self):
        record = read_records(self.stream, 'docinfo').next()

        tag_model = BinData
        model_type, attributes, stream = tag_model.parse_pass1(self.ctx, record)
        self.assertTrue(BinEmbedded, model_type)
        self.assertEquals(2, attributes['storageId'])
        self.assertEquals('jpg', attributes['ext'])

class TableTest(TestCase):
    ctx = DC()
    stream = StringIO('G\x04\xc0\x02 lbt\x11#*\x08\x00\x00\x00\x00\x00\x00\x00\x00\x06\x9e\x00\x00D\x10\x00\x00\x00\x00\x00\x00\x1b\x01\x1b\x01\x1b\x01\x1b\x01\xed\xad\xa2V\x00\x00\x00\x00')
    def testParsePass1(self):
        record = read_records(self.stream, 'bodytext/0').next()

        tag_model = tag_models[record.tagid]
        model_type, attributes, stream = tag_model.parse_pass1(self.ctx, record)
        self.assertTrue(TableControl, model_type)

        self.assertEquals(1453501933, attributes['instanceId'])
        self.assertEquals(0x0, attributes['offsetX'])
        self.assertEquals(0x0, attributes['offsetY'])
        self.assertEquals(0x1044, attributes['height'])
        self.assertEquals(0x9e06, attributes['width'])
        self.assertEquals(0, attributes['unknown1'])
        self.assertEquals(0x82a2311L, attributes['flags'])
        self.assertEquals(0, attributes['zOrder'])
        self.assertEquals([283, 283, 283, 283], attributes['margin'])
        self.assertEquals('tbl ' , attributes['chid'])

class ListHeaderTest(TestCase):
    ctx = DC()
    record_bytes = 'H\x08`\x02\x01\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x03O\x00\x00\x1a\x01\x00\x00\x8d\x00\x8d\x00\x8d\x00\x8d\x00\x01\x00\x03O\x00\x00'
    stream = StringIO(record_bytes)
    def testParse(self):
        record = read_records(self.stream, 'bodytext/0').next()

        tag_model = tag_models[record.tagid]
        self.assertEquals(ListHeader, tag_model)
        payload_stream = record.bytestream()
        attributes = tag_model.parse_attributes(self.ctx, payload_stream)
        self.assertEquals(1, attributes['nParagraphs'])
        self.assertEquals(0x20L, attributes['listflags'])
        self.assertEquals(0, attributes['unknown1'])

        model_type, attributes, payload_stream = tag_model.parse_pass1(self.ctx, record)
        self.assertEquals(8, payload_stream.tell())

class TableBodyTest(TestCase):
    ctx = DC(version=(5, 0, 1, 7))
    stream = StringIO('M\x08\xa0\x01\x06\x00\x00\x04\x02\x00\x02\x00\x00\x00\x8d\x00\x8d\x00\x8d\x00\x8d\x00\x02\x00\x02\x00\x01\x00\x00\x00')
    def testParsePass1(self):
        record = read_records(self.stream, 'bodytext/0').next()

        record, model, attributes, stream = parse_models_pass1(self.ctx, [record]).next()
        self.assertEquals(TableBody, model)
        self.assertEquals([141, 141, 141, 141], attributes['padding'])
        self.assertEquals(0x4000006L, attributes['attr'])
        self.assertEquals(2, attributes['nCols'])
        self.assertEquals(2, attributes['nRows'])
        self.assertEquals(1, attributes['borderFillId'])
        self.assertEquals([2, 2], attributes['rowSizes'])
        self.assertEquals(0, attributes['cellspacing'])
        self.assertEquals([], attributes['validZones'])

class Pass2Test(TestCase):
    ctx = DC()
    def test_pass2_events(self):
        from .tagids import HWPTAG_BEGIN
        from .models import STARTREC, ENDREC
        def items():
            yield Record(HWPTAG_BEGIN+4, 0, ''),
            yield Record(HWPTAG_BEGIN+3, 1, ''),
            yield Record(HWPTAG_BEGIN+2, 0, ''),
            yield Record(HWPTAG_BEGIN+1, 0, ''),
        items = list(item for item in items())

        events = list(pass2_events(items))

        def expected():
            yield STARTREC, items[0]
            yield STARTREC, items[1]
            yield ENDREC, items[1]
            yield ENDREC, items[0]
            yield STARTREC, items[2]
            yield ENDREC, items[2]
            yield STARTREC, items[3]
            yield ENDREC, items[3]
        expected = list(expected())
        self.assertEquals(expected, events)

    def test_pass2_parented(self):
        from .models import STARTREC, ENDREC
        def events():
            yield STARTREC, (None, TableControl, None)
            yield STARTREC, (None, ListHeader, None)
            yield ENDREC, (None, ListHeader, None)
            yield STARTREC, (None, TableBody, None)
            yield ENDREC, (None, TableBody, None)
            yield STARTREC, (None, ListHeader, None)
            yield ENDREC, (None, ListHeader, None)
            yield ENDREC, (None, TableControl, None)
            yield STARTREC, (None, ListHeader, None)
            yield ENDREC, (None, ListHeader, None)
        events = list(events())

        parented = list(pass2_parented(events))

        def expected():
            yield dict(attributes=None, model=None), (None, TableControl, None)
            yield dict(attributes=None, model=TableControl), (None, ListHeader, None)
            yield dict(attributes=None, model=TableControl), (None, TableBody, None)
            yield dict(attributes=None, model=TableControl), (None, ListHeader, None)
            yield dict(attributes=None, model=None), (None, ListHeader, None)
        expected = list(expected())
        self.assertEquals(expected, parented)

class TableCaptionCellTest(TestCase):
    ctx = DC(version=(5, 0, 1, 7))
    records_bytes = 'G\x04\xc0\x02 lbt\x10#*(\x00\x00\x00\x00\x00\x00\x00\x00\x06\x9e\x00\x00\x04\n\x00\x00\x03\x00\x00\x00\x1b\x01R\x037\x02n\x04\n^\xc0V\x00\x00\x00\x00H\x08`\x01\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x008!\x00\x00R\x03\x06\x9e\x00\x00M\x08\xa0\x01\x06\x00\x00\x04\x02\x00\x02\x00\x00\x00\x8d\x00\x8d\x00\x8d\x00\x8d\x00\x02\x00\x02\x00\x01\x00\x00\x00H\x08`\x02\x01\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x03O\x00\x00\x1a\x01\x00\x00\x8d\x00\x8d\x00\x8d\x00\x8d\x00\x01\x00\x03O\x00\x00'
    def testParsePass1(self):
        stream = StringIO(self.records_bytes)
        records = list(read_records(stream, 'bodytext/0'))

        pass1 = list(parse_models_pass1(self.ctx, records))
        def expected():
            yield records[0], TableControl, 44, set(['chid', 'flags', 'offsetX', 'offsetY', 'width', 'height', 'zOrder', 'unknown1', 'margin', 'instanceId', 'unknown2', 'description'])
            yield records[1], ListHeader, 8, set(['nParagraphs', 'unknown1', 'listflags'])
            yield records[2], TableBody, 26, set(['attr', 'nRows', 'nCols', 'cellspacing', 'padding', 'rowSizes', 'borderFillId', 'validZones'])
            yield records[3], ListHeader, 8, set(['nParagraphs', 'unknown1', 'listflags'])
        expected = list(expected())
        self.assertEquals(expected, [(record, model, stream.tell(), set(attributes.keys())) for record, model, attributes, stream in pass1])
        return pass1

    def testParsePass2(self):
        pass1 = self.testParsePass1()
        pass2 = list(parse_models_pass2(self.ctx, pass1))

        tablecaption = pass2[1]
        record, model, attributes, stream = tablecaption
        self.assertEquals(TableCaption, model)
        self.assertEquals(22, stream.tell())
        # ListHeader attributes
        self.assertEquals(2, attributes['nParagraphs'])
        self.assertEquals(0x0L, attributes['listflags'])
        self.assertEquals(0, attributes['unknown1'])
        # TableCaption attributes
        self.assertEquals(3, attributes['captflags'])
        self.assertEquals(8504L, attributes['width'])
        self.assertEquals(850, attributes['offset'])
        self.assertEquals(40454L, attributes['maxsize'])

        tablecell = pass2[3]
        record, model, attributes, stream = tablecell
        self.assertEquals(TableCell, model)
        self.assertEquals(38, stream.tell())
        # ListHeader attributes
        self.assertEquals(1, attributes['nParagraphs'])
        self.assertEquals(0x20L, attributes['listflags'])
        self.assertEquals(0, attributes['unknown1'])
        # TableCell attributes
        self.assertEquals(0, attributes['col'])
        self.assertEquals(0, attributes['row'])
        self.assertEquals(1, attributes['colspan'])
        self.assertEquals(1, attributes['rowspan'])
        self.assertEquals(0x4f03, attributes['width'])
        self.assertEquals(0x11a, attributes['height'])
        self.assertEquals([141, 141, 141, 141], attributes['padding'])
        self.assertEquals(1, attributes['borderFillId'],)
        self.assertEquals(0x4f03, attributes['unknown_width'])


def test_suite():
    import sys, unittest
    return unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
