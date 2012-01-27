from unittest import TestCase, makeSuite
from StringIO import StringIO

from .recordstream import Record, read_records
from .binmodel import tag_models, parse_models_pass1, parse_models_pass2, prefix_event, prefix_ancestors
from .binmodel import BinData, TableControl, ListHeader, TableCaption, TableCell, TableBody
from .binmodel import STARTEVENT, ENDEVENT
from . import binmodel

def TestContext(**ctx):
    ''' test context '''
    if not 'logging' in ctx:
        import logging
        logger = logging.getLogger('null')
        logger.addHandler(logging.Handler())
        ctx['logging'] = logger
    if not 'version' in ctx:
        ctx['version'] = (5, 0, 0, 0)
    return ctx

testcontext = TestContext()

class TestRecordParsing(TestCase):
    def test_init_record_parsing_context(self):
        from .tagids import HWPTAG_BEGIN
        from .binmodel import init_record_parsing_context, DocumentProperties
        record = dict(tagid=HWPTAG_BEGIN, payload='abcd')
        context = init_record_parsing_context(testcontext, record)

        self.assertEquals(record, context['record'])
        self.assertEquals('abcd', context['stream'].read())


class BinEmbeddedTest(TestCase):
    ctx = TestContext()
    stream = StringIO('\x12\x04\xc0\x00\x01\x00\x02\x00\x03\x00\x6a\x00\x70\x00\x67\x00')
    def testParsePass1(self):
        record = read_records(self.stream, 'docinfo').next()
        payload_stream = StringIO(record['payload'])

        tag_model = BinData
        model_type, attributes = tag_model.parse_pass1(dict(), self.ctx,
                                                       payload_stream)
        self.assertTrue(BinData, model_type)
        self.assertEquals(BinData.StorageType.EMBEDDING, BinData.Flags(attributes['flags']).storage)
        self.assertEquals(2, attributes['storage_id'])
        self.assertEquals('jpg', attributes['ext'])

class TableTest(TestCase):
    ctx = TestContext()
    stream = StringIO('G\x04\xc0\x02 lbt\x11#*\x08\x00\x00\x00\x00\x00\x00\x00\x00\x06\x9e\x00\x00D\x10\x00\x00\x00\x00\x00\x00\x1b\x01\x1b\x01\x1b\x01\x1b\x01\xed\xad\xa2V\x00\x00\x00\x00')
    def testParsePass1(self):
        record = read_records(self.stream, 'bodytext/0').next()

        model = tag_models[record['tagid']]
        result = model.parse_pass1(dict(), self.ctx, StringIO(record['payload']))
        model_type, attributes = result
        self.assertTrue(TableControl, model_type)

        self.assertEquals(1453501933, attributes['instance_id'])
        self.assertEquals(0x0, attributes['x'])
        self.assertEquals(0x0, attributes['y'])
        self.assertEquals(0x1044, attributes['height'])
        self.assertEquals(0x9e06, attributes['width'])
        self.assertEquals(0, attributes['unknown1'])
        self.assertEquals(0x82a2311L, attributes['flags'])
        self.assertEquals(0, attributes['z_order'])
        self.assertEquals(dict(left=283, right=283, top=283, bottom=283),
                          attributes['margin'])
        self.assertEquals('tbl ' , attributes['chid'])

class ListHeaderTest(TestCase):
    ctx = TestContext()
    record_bytes = 'H\x08`\x02\x01\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x03O\x00\x00\x1a\x01\x00\x00\x8d\x00\x8d\x00\x8d\x00\x8d\x00\x01\x00\x03O\x00\x00'
    stream = StringIO(record_bytes)
    def testParse(self):
        record = read_records(self.stream, 'bodytext/0').next()
        record_tagid = record['tagid']

        tag_model = tag_models[record_tagid]
        self.assertEquals(ListHeader, tag_model)
        payload_stream = StringIO(record['payload'])
        model, attributes = tag_model.parse_pass1(dict(), self.ctx, payload_stream)
        self.assertEquals(1, attributes['paragraphs'])
        self.assertEquals(0x20L, attributes['listflags'])
        self.assertEquals(0, attributes['unknown1'])
        self.assertEquals(8, payload_stream.tell())

class TableBodyTest(TestCase):
    ctx = TestContext(version=(5, 0, 1, 7))
    stream = StringIO('M\x08\xa0\x01\x06\x00\x00\x04\x02\x00\x02\x00\x00\x00\x8d\x00\x8d\x00\x8d\x00\x8d\x00\x02\x00\x02\x00\x01\x00\x00\x00')
    def testParsePass1(self):
        record = read_records(self.stream, 'bodytext/0').next()

        event, (context, record) = parse_models_pass1(self.ctx, [record]).next()
        model = record['model']
        attributes = record['attributes']

        self.assertEquals(TableBody, model)
        self.assertEquals(dict(left=141, right=141, top=141, bottom=141),
                          attributes['padding'])
        self.assertEquals(0x4000006L, attributes['flags'])
        self.assertEquals(2, attributes['cols'])
        self.assertEquals(2, attributes['rows'])
        self.assertEquals(1, attributes['borderfill_id'])
        self.assertEquals((2, 2), attributes['rowcols'])
        self.assertEquals(0, attributes['cellspacing'])
        self.assertEquals([], attributes['validZones'])

class Pass2Test(TestCase):
    ctx = TestContext()
    def test_pass2_events(self):
        from .tagids import HWPTAG_BEGIN
        def items():
            yield Record(HWPTAG_BEGIN+4, 0, ''),
            yield Record(HWPTAG_BEGIN+3, 1, ''),
            yield Record(HWPTAG_BEGIN+2, 0, ''),
            yield Record(HWPTAG_BEGIN+1, 0, ''),
        items = list(item for item in items())
        leveld_items = zip([0, 1, 0, 0], items)

        events = list(prefix_event(leveld_items))

        def expected():
            yield STARTEVENT, items[0]
            yield STARTEVENT, items[1]
            yield ENDEVENT, items[1]
            yield ENDEVENT, items[0]
            yield STARTEVENT, items[2]
            yield ENDEVENT, items[2]
            yield STARTEVENT, items[3]
            yield ENDEVENT, items[3]
        expected = list(expected())
        self.assertEquals(expected, events)

class LineSegTest(TestCase):
    def testDecode(self):
        data = '00000000481e0000e8030000e80300005203000058020000dc0500003ca00000000006003300000088240000e8030000e80300005203000058020000dc0500003ca000000000060067000000c82a0000e8030000e80300005203000058020000dc0500003ca0000000000600'
        import binascii
        data = binascii.a2b_hex(data)
        from .binmodel import ParaLineSeg
        lines = list(ParaLineSeg.decode(dict(), dict(), data))
        self.assertEquals(0, lines[0]['chpos'])
        self.assertEquals(51, lines[1]['chpos'])
        self.assertEquals(103, lines[2]['chpos'])


class TableCaptionCellTest(TestCase):
    ctx = TestContext(version=(5, 0, 1, 7))
    records_bytes = 'G\x04\xc0\x02 lbt\x10#*(\x00\x00\x00\x00\x00\x00\x00\x00\x06\x9e\x00\x00\x04\n\x00\x00\x03\x00\x00\x00\x1b\x01R\x037\x02n\x04\n^\xc0V\x00\x00\x00\x00H\x08`\x01\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x008!\x00\x00R\x03\x06\x9e\x00\x00M\x08\xa0\x01\x06\x00\x00\x04\x02\x00\x02\x00\x00\x00\x8d\x00\x8d\x00\x8d\x00\x8d\x00\x02\x00\x02\x00\x01\x00\x00\x00H\x08`\x02\x01\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x03O\x00\x00\x1a\x01\x00\x00\x8d\x00\x8d\x00\x8d\x00\x8d\x00\x01\x00\x03O\x00\x00'
    def testParsePass1(self):
        stream = StringIO(self.records_bytes)
        records = list(read_records(stream, 'bodytext/0'))

        pass1 = list(parse_models_pass1(self.ctx, records))
        def expected():
            yield TableControl, set([name for type, name in TableControl.attributes(self.ctx)]+['chid'])
            yield ListHeader, set(name for type, name in ListHeader.attributes(self.ctx))
            yield TableBody, set(name for type, name in TableBody.attributes(self.ctx))
            yield ListHeader, set(name for type, name in ListHeader.attributes(self.ctx))
        expected = list(expected())
        self.assertEquals(expected, [(record['model'],
                                      set(record['attributes'].keys()))
                                     for ancestors, (context, record) in
                                     prefix_ancestors(pass1)])
        return pass1

    def testParsePass2(self):
        pass1 = self.testParsePass1()
        pass2 = list(parse_models_pass2(pass1))

        result = list(b for a, b in prefix_ancestors(pass2))
        tablecaption = result[1]
        context, record = tablecaption
        model = record['model']
        attributes = record['attributes']
        stream = context['stream']

        self.assertEquals(TableCaption, model)
        self.assertEquals(22, stream.tell())
        # ListHeader attributes
        self.assertEquals(2, attributes['paragraphs'])
        self.assertEquals(0x0L, attributes['listflags'])
        self.assertEquals(0, attributes['unknown1'])
        # TableCaption attributes
        self.assertEquals(3, attributes['flags'])
        self.assertEquals(8504L, attributes['width'])
        self.assertEquals(850, attributes['separation'])
        self.assertEquals(40454L, attributes['maxsize'])

        tablecell = result[3]
        context, record = tablecell
        model = record['model']
        attributes = record['attributes']
        stream = context['stream']
        self.assertEquals(TableCell, model)
        self.assertEquals(38, stream.tell())
        # ListHeader attributes
        self.assertEquals(1, attributes['paragraphs'])
        self.assertEquals(0x20L, attributes['listflags'])
        self.assertEquals(0, attributes['unknown1'])
        # TableCell attributes
        self.assertEquals(0, attributes['col'])
        self.assertEquals(0, attributes['row'])
        self.assertEquals(1, attributes['colspan'])
        self.assertEquals(1, attributes['rowspan'])
        self.assertEquals(0x4f03, attributes['width'])
        self.assertEquals(0x11a, attributes['height'])
        self.assertEquals(dict(left=141, right=141, top=141, bottom=141),
                          attributes['padding'])
        self.assertEquals(1, attributes['borderfill_id'],)
        self.assertEquals(0x4f03, attributes['unknown_width'])

from .binmodel import RecordModel, typed_model_attributes
from .dataio import INT32, BSTR
class TestTypedModelAttributes(TestCase):
    def test_typed_model_attributes(self):
        class Hello(RecordModel):
            @staticmethod
            def attributes(context):
                yield INT32, 'a'
        class Hoho(Hello):
            @staticmethod
            def attributes(context):
                yield BSTR, 'b'

        attributes = dict(a=1, b=u'abc', c=(2,2))
        result = typed_model_attributes(Hoho, attributes, dict())
        result = list(result)
        expected = dict(a=(INT32,1), b=(BSTR,u'abc'), c=(tuple,(2,2))).items()
        self.assertEquals(set(expected), set(result))

class TestRecordModel(TestCase):
    def test_assign_enum_flags_name(self):
        from .dataio import Flags, Enum, UINT32
        from .binmodel import RecordModel
        class FooRecord(RecordModel):
            Bar = Flags(UINT32)
            Baz = Enum()
        self.assertEquals('Bar', FooRecord.Bar.__name__)
        self.assertEquals('Baz', FooRecord.Baz.__name__)
            
class TestControlType(TestCase):
    def test_ControlType(self):
        from .binmodel import Control
        class FooControl(Control):
            chid = 'foo!'
        try:
            class Foo2Control(Control):
                chid = 'foo!'
        except Exception, duplicated_chid:
            pass
        else:
            assert False, 'Exception expected'
