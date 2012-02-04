# -*- coding: utf-8 -*-
from unittest import TestCase, makeSuite
from StringIO import StringIO

from .recordstream import Record, read_records
from .binmodel import tag_models, prefix_event, prefix_ancestors
from .binmodel import BinData, TableControl, ListHeader, TableCaption, TableCell, TableBody
from .binmodel import STARTEVENT, ENDEVENT
from . import binmodel
from .utils import cached_property

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

    def test_parse_model_attributes(self):
        # TODO
        pass


class BinEmbeddedTest(TestCase):
    ctx = TestContext()
    stream = StringIO('\x12\x04\xc0\x00\x01\x00\x02\x00\x03\x00\x6a\x00\x70\x00\x67\x00')
    def testParsePass1(self):
        from .binmodel import BinData
        from .binmodel import init_record_parsing_context
        record = read_records(self.stream, 'docinfo').next()
        context = init_record_parsing_context(testcontext, record)
        model_type, attributes = BinData.parse_pass1(context)

        self.assertTrue(BinData, model_type)
        self.assertEquals(BinData.StorageType.EMBEDDING, BinData.Flags(attributes['flags']).storage)
        self.assertEquals(2, attributes['storage_id'])
        self.assertEquals('jpg', attributes['ext'])


def nth(iterable, n, default=None):
    from itertools import islice
    return next(islice(iterable, n, None), default)

class TestBase(TestCase):
    ctx = TestContext()

    @cached_property
    def samples_dir(self):
        return '../../../samples'

    @cached_property
    def sample_hwp(self):
        return 'sample-5017.hwp'

    @cached_property
    def olefile(self):
        from OleFileIO_PL import OleFileIO
        return OleFileIO('/'.join([self.samples_dir, self.sample_hwp]))

    @cached_property
    def olestg(self):
        from .filestructure import OleStorage
        return OleStorage(self.olefile)

    @cached_property
    def hwp5file_rec(self):
        from .recordstream import Hwp5File
        return Hwp5File(self.olestg)

    @cached_property
    def bodytext(self):
        hwp5file = self.hwp5file_rec
        return hwp5file.bodytext


class TableTest(TestBase):

    @property
    def stream(self):
        return StringIO('G\x04\xc0\x02 lbt\x11#*\x08\x00\x00\x00\x00\x00\x00\x00\x00\x06\x9e\x00\x00D\x10\x00\x00\x00\x00\x00\x00\x1b\x01\x1b\x01\x1b\x01\x1b\x01\xed\xad\xa2V\x00\x00\x00\x00')

    @cached_property
    def tablecontrol_record(self):
        return nth(self.bodytext.section(0).records(), 30)

    @cached_property
    def tablecaption_record(self):
        return nth(self.bodytext.section(0).records(), 68)

    @cached_property
    def tablebody_record(self):
        return nth(self.bodytext.section(0).records(), 31)

    @cached_property
    def tablecell_record(self):
        return nth(self.bodytext.section(0).records(), 32)

    def testParsePass1(self):
        from .binmodel import Control, TableControl
        from .binmodel import init_record_parsing_context
        record = read_records(self.stream, 'bodytext/0').next()
        context = init_record_parsing_context(testcontext, record)
        model_type, attributes = Control.parse_pass1(context)

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

    def test_parse_child_table_body(self):
        from .binmodel import init_record_parsing_context
        record = self.tablecontrol_record
        context = init_record_parsing_context(testcontext, record)

        tablebody_record = self.tablebody_record
        tablebody_context = init_record_parsing_context(testcontext, tablebody_record)
        child = (tablebody_context, TableBody, dict())

        self.assertFalse(context.get('table_body'))
        child_model, child_attributes = TableControl.parse_child(dict(),
                                                                 context, child)
        # 'table_body' in table record context should have been changed to True
        self.assertTrue(context['table_body'])
        # model and attributes should not have been changed
        self.assertEquals(TableBody, child_model)
        self.assertEquals(dict(), child_attributes)

    def test_parse_child_table_cell(self):
        from .binmodel import init_record_parsing_context
        from .binmodel import ListHeader, TableCell
        record = self.tablecontrol_record
        context = init_record_parsing_context(testcontext, record)

        context['table_body'] = True

        child_record = self.tablecell_record
        child_context = init_record_parsing_context(testcontext, child_record)
        child_model, child_attributes = ListHeader.parse_pass1(child_context)
        self.assertEquals(ListHeader, child_model)
        child = (child_context, child_model, child_attributes)

        child_model, child_attributes = TableControl.parse_child(dict(),
                                                                 context, child)
        self.assertEquals(TableCell, child_model)
        self.assertEquals(dict(padding=dict(top=141, right=141, bottom=141,
                                            left=141),
                               rowspan=1,
                               colspan=1,
                               borderfill_id=1,
                               height=282,
                               listflags=32L,
                               width=20227,
                               unknown1=0,
                               unknown_width=20227,
                               paragraphs=1,
                               col=0,
                               row=0), child_attributes)
        self.assertEquals('', child_context['stream'].read())

    def test_parse_child_table_caption(self):
        from .binmodel import init_record_parsing_context
        from .binmodel import ListHeader, TableCaption
        record = self.tablecontrol_record
        context = init_record_parsing_context(testcontext, record)

        context['table_body'] = False

        child_record = self.tablecaption_record
        child_context = init_record_parsing_context(testcontext, child_record)
        child_model, child_attributes = ListHeader.parse_pass1(child_context)
        child = (child_context, child_model, child_attributes)

        child_model, child_attributes = TableControl.parse_child(dict(),
                                                                 context, child)
        self.assertEquals(TableCaption, child_model)
        self.assertEquals(dict(listflags=0,
                               width=8504,
                               maxsize=40454,
                               unknown1=0,
                               flags=3L,
                               separation=850,
                               paragraphs=2), child_attributes)
        self.assertEquals('', child_context['stream'].read())


class ShapeComponentTest(TestBase):

    @cached_property
    def sample_hwp(self):
        return 'textbox.hwp'

    @cached_property
    def control_gso_record(self):
        return nth(self.bodytext.section(0).records(), 12)

    @cached_property
    def shapecomponent_record(self):
        return nth(self.bodytext.section(0).records(), 19)

    @cached_property
    def textbox_paragraph_list_record(self):
        return nth(self.bodytext.section(0).records(), 20)

    def test_parse_shapecomponent_textbox_paragraph_list(self):
        from .binmodel import init_record_parsing_context
        from .binmodel import ListHeader, ShapeComponent, TextboxParagraphList
        record = self.shapecomponent_record
        context = init_record_parsing_context(testcontext, record)

        child_record = self.textbox_paragraph_list_record
        child_context = init_record_parsing_context(testcontext,
                                                    child_record)
        child_model, child_attributes = ListHeader.parse_pass1(child_context)
        self.assertEquals(ListHeader, child_model)
        child = (child_context, child_model, child_attributes)

        child_model, child_attributes = ShapeComponent.parse_child(dict(),
                                                                   context,
                                                                   child)
        self.assertEquals(TextboxParagraphList, child_model)
        self.assertEquals(dict(listflags=32L,
                               padding=dict(top=283, right=283, bottom=283,
                                            left=283),
                               unknown1=0,
                               maxwidth=11763,
                               paragraphs=1), child_attributes)
        self.assertEquals('', child_context['stream'].read())

    def test_parse_with_parent(self):
        from .binmodel import init_record_parsing_context
        from .binmodel import GShapeObjectControl, ShapeComponent

        parent_record = self.control_gso_record
        parent_context = init_record_parsing_context(testcontext, parent_record)

        # if parent model is GShapeObjectControl
        parent_model = dict(type=GShapeObjectControl)
        parent = (parent_context, parent_model)

        record = self.shapecomponent_record
        context = init_record_parsing_context(testcontext, record)
        model_type, model_content = ShapeComponent, dict()
        model_type, model_content = model_type.parse_with_parent(model_content, context, parent)

        self.assertEquals(model_type, ShapeComponent)
        self.assertTrue('chid0' in model_content)

        # if parent model is not GShapeObjectControl
        # TODO


class HeaderFooterTest(TestBase):

    @cached_property
    def sample_hwp(self):
        return 'headerfooter.hwp'

    @cached_property
    def header_record(self):
        return nth(self.bodytext.section(0).records(), 16)

    @cached_property
    def header_paragraph_list_record(self):
        return nth(self.bodytext.section(0).records(), 17)

    def test_parse_child(self):
        from .binmodel import init_record_parsing_context
        from .binmodel import ListHeader, Header
        record = self.header_record
        context = init_record_parsing_context(testcontext, record)

        child_record = self.header_paragraph_list_record
        child_context = init_record_parsing_context(testcontext,
                                                    child_record)
        child_model, child_attributes = ListHeader.parse_pass1(child_context)
        child = (child_context, child_model, child_attributes)

        child_model, child_attributes = Header.parse_child(dict(), context,
                                                           child)
        self.assertEquals(Header.ParagraphList, child_model)
        self.assertEquals(dict(textrefsbitmap=0,
                               numberrefsbitmap=0,
                               height=4252,
                               listflags=0,
                               width=42520,
                               unknown1=0,
                               paragraphs=1), child_attributes)
        # TODO
        #self.assertEquals('', child_context['stream'].read())


class ListHeaderTest(TestCase):
    ctx = TestContext()
    record_bytes = 'H\x08`\x02\x01\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x03O\x00\x00\x1a\x01\x00\x00\x8d\x00\x8d\x00\x8d\x00\x8d\x00\x01\x00\x03O\x00\x00'
    stream = StringIO(record_bytes)
    def testParse(self):
        from .binmodel import ListHeader
        from .binmodel import init_record_parsing_context
        record = read_records(self.stream, 'bodytext/0').next()
        context = init_record_parsing_context(testcontext, record)
        model, attributes = ListHeader.parse_pass1(context)

        self.assertEquals(1, attributes['paragraphs'])
        self.assertEquals(0x20L, attributes['listflags'])
        self.assertEquals(0, attributes['unknown1'])
        self.assertEquals(8, context['stream'].tell())

class TableBodyTest(TestCase):
    ctx = TestContext(version=(5, 0, 1, 7))
    stream = StringIO('M\x08\xa0\x01\x06\x00\x00\x04\x02\x00\x02\x00\x00\x00\x8d\x00\x8d\x00\x8d\x00\x8d\x00\x02\x00\x02\x00\x01\x00\x00\x00')
    def testParsePass1(self):
        from .binmodel import parse_pass1_record
        record = read_records(self.stream, 'bodytext/0').next()

        context, model = parse_pass1_record(self.ctx, record)
        model_type = model['type']
        model_content = model['content']

        self.assertEquals(TableBody, model_type)
        self.assertEquals(dict(left=141, right=141, top=141, bottom=141),
                          model_content['padding'])
        self.assertEquals(0x4000006L, model_content['flags'])
        self.assertEquals(2, model_content['cols'])
        self.assertEquals(2, model_content['rows'])
        self.assertEquals(1, model_content['borderfill_id'])
        self.assertEquals((2, 2), model_content['rowcols'])
        self.assertEquals(0, model_content['cellspacing'])
        self.assertEquals([], model_content['validZones'])

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
        from .binmodel import parse_pass1
        stream = StringIO(self.records_bytes)
        records = list(read_records(stream, 'bodytext/0'))

        pass1 = list(parse_pass1(self.ctx, records))
        def expected():
            yield TableControl, set([name for type, name in TableControl.attributes(self.ctx)]+['chid'])
            yield ListHeader, set(name for type, name in ListHeader.attributes(self.ctx))
            yield TableBody, set(name for type, name in TableBody.attributes(self.ctx))
            yield ListHeader, set(name for type, name in ListHeader.attributes(self.ctx))
        expected = list(expected())
        self.assertEquals(expected, [(model['type'],
                                      set(model['content'].keys()))
                                     for context, model in pass1])
        return pass1

    def testParsePass2(self):
        from .binmodel import parse_pass2
        pass1 = self.testParsePass1()
        pass2 = list(parse_pass2(pass1))

        result = pass2
        tablecaption = result[1]
        context, model = tablecaption
        model_type = model['type']
        model_content = model['content']
        stream = context['stream']

        self.assertEquals(TableCaption, model_type)
        self.assertEquals(22, stream.tell())
        # ListHeader attributes
        self.assertEquals(2, model_content['paragraphs'])
        self.assertEquals(0x0L, model_content['listflags'])
        self.assertEquals(0, model_content['unknown1'])
        # TableCaption model_content
        self.assertEquals(3, model_content['flags'])
        self.assertEquals(8504L, model_content['width'])
        self.assertEquals(850, model_content['separation'])
        self.assertEquals(40454L, model_content['maxsize'])

        tablecell = result[3]
        context, model = tablecell
        model_type = model['type']
        model_content = model['content']
        stream = context['stream']
        self.assertEquals(TableCell, model_type)
        self.assertEquals(38, stream.tell())
        # ListHeader model_content
        self.assertEquals(1, model_content['paragraphs'])
        self.assertEquals(0x20L, model_content['listflags'])
        self.assertEquals(0, model_content['unknown1'])
        # TableCell model_content
        self.assertEquals(0, model_content['col'])
        self.assertEquals(0, model_content['row'])
        self.assertEquals(1, model_content['colspan'])
        self.assertEquals(1, model_content['rowspan'])
        self.assertEquals(0x4f03, model_content['width'])
        self.assertEquals(0x11a, model_content['height'])
        self.assertEquals(dict(left=141, right=141, top=141, bottom=141),
                          model_content['padding'])
        self.assertEquals(1, model_content['borderfill_id'],)
        self.assertEquals(0x4f03, model_content['unknown_width'])

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

class TestPrefixOps(TestCase):

    def test_ancestors_from_level(self):

        from .binmodel import prefix_ancestors_from_level

        level_prefixed = [
            (0, 'a0'),
            (0, 'b0'),   # sibling
            (1, 'b0-a1'), # child
            (2, 'b0-a1-a2'), #child
            (1, 'b0-b1'), # jump to parent level
            (2, 'b0-b1-b2'), # child
            (0, 'c0'), # jump to grand-parent level
        ]

        ancestors_prefixed = prefix_ancestors_from_level(level_prefixed)
        result = list((list(ancestors), item)
                      for ancestors, item in ancestors_prefixed)

        self.assertEquals(result.pop(0), ([None], 'a0'))
        self.assertEquals(result.pop(0), ([None], 'b0'))
        self.assertEquals(result.pop(0), ([None, 'b0'], 'b0-a1'))
        self.assertEquals(result.pop(0), ([None, 'b0', 'b0-a1'], 'b0-a1-a2'))
        self.assertEquals(result.pop(0), ([None, 'b0'], 'b0-b1'))
        self.assertEquals(result.pop(0), ([None, 'b0', 'b0-b1'], 'b0-b1-b2'))
        self.assertEquals(result.pop(0), ([None], 'c0'))

    def test_ancestors_from_level_from_nonzero_baselevel(self):
        from .binmodel import prefix_ancestors_from_level
        level_prefixed = [
            (7, 'a0'), # baselevel 7
            (8, 'a0-a1'),
            (9, 'a0-a1-a2'),
            (7, 'b0'),
        ]
        ancestors_prefixed = prefix_ancestors_from_level(level_prefixed)
        result = list((list(ancestors), item)
                      for ancestors, item in ancestors_prefixed)
        self.assertEquals(result.pop(0), ([None], 'a0'))
        self.assertEquals(result.pop(0), ([None, 'a0'], 'a0-a1'))
        self.assertEquals(result.pop(0), ([None, 'a0', 'a0-a1'], 'a0-a1-a2'))
        self.assertEquals(result.pop(0), ([None], 'b0'))

    def test_ancestors_from_level_fails_at_level_below_baselevel(self):
        from .binmodel import prefix_ancestors_from_level
        level_prefixed = [
            (7, 'a7'), # baselevel 7
            (8, 'a7-a8'),
            (9, 'a7-a8-a9'),
            (6, 'b7'), # level below the base level
        ]
        try:
            list(prefix_ancestors_from_level(level_prefixed))
            # TODO: 현재로서는 스택에 기본으로 root_item을 넣어놓는 구현 방식 때문에
            # base level 바로 아래 level은 에러가 나지 않음
            #self.fail('exception expected')
        except:
            pass

        level_prefixed = [
            (7, 'a7'), # baselevel 7
            (8, 'a7-a8'),
            (9, 'a7-a8-a9'),
            (5, 'b7'), # level below the base level
        ]
        try:
            list(prefix_ancestors_from_level(level_prefixed))
            self.fail('exception expected')
        except:
            pass

    def test_ancestors_from_level_assert_fails_at_invalid_level_jump(self):
        from .binmodel import prefix_ancestors_from_level

        level_prefixed = [
            (0, 'a0'),
            (2, 'a0-a1-a2'), # invalid level jump
        ]
        ancestors_prefixed = prefix_ancestors_from_level(level_prefixed)
        try:
            list(ancestors_prefixed)
            self.fail('assert fails expected')
        except:
            pass

class TestControlChar(TestBase):
    def test_decode_bytes(self):
        from .binmodel import ControlChar
        import logging
        context = dict(version=self.hwp5file_rec.header.version,
                       logging=logging)
        section = self.hwp5file_rec.bodytext.section(0)
        import itertools
        paratext_record = nth(section.records(), 1)
        payload = paratext_record['payload']
        controlchar = ControlChar.decode_bytes(payload[0:16])
        self.assertEquals(dict(code=ord(ControlChar.SECTION_COLUMN_DEF),
                               chid='secd',
                               param='\x00'*8), controlchar)

class TestModelJson(TestBase):
    def test_model_to_json(self):
        from .binmodel import parse_models
        from .binmodel import model_to_json
        import logging
        context = dict(version=self.hwp5file_rec.header.version,
                       logging=logging)
        record = self.hwp5file_rec.docinfo.records().next()
        model = parse_models(context, [record]).next()
        json = model_to_json(model, indent=2, sort_keys=True)

        import simplejson
        jsonobject = simplejson.loads(json)
        self.assertEquals('DocumentProperties', jsonobject['type'])

    def test_model_to_json_with_controlchar(self):
        from .binmodel import parse_models
        from .binmodel import model_to_json
        import logging
        context = dict(version=self.hwp5file_rec.header.version,
                       logging=logging)
        section = self.hwp5file_rec.bodytext.section(0)
        import itertools
        records = list(itertools.islice(section.records(), 0, 2))
        model = nth(parse_models(context, records), 1)
        json = model_to_json(model)

        import simplejson
        jsonobject = simplejson.loads(json)
        self.assertEquals('ParaText', jsonobject['type'])
        self.assertEquals([[0, 8], dict(code=2, param='\x00'*8, chid='secd')],
                         jsonobject['content']['chunks'][0])

    def test_model_to_json_with_unparsed(self):
        from .binmodel import model_to_json
        import logging

        record = dict(payload='\x00\x01\x02\x03')
        model = dict(type=RecordModel, content=[], record=record,
                     unparsed='\xff\xfe\xfd\xfc')
        json = model_to_json(model)

        import simplejson
        jsonobject = simplejson.loads(json)
        self.assertEquals(['ff fe fd fc'], jsonobject['unparsed'])

    def test_recoder(self):
        from .binmodel import recoder_to_json
        import logging
        context = dict(version=self.hwp5file_rec.header.version,
                      logging=logging)
        recode = recoder_to_json(context)

        stream = recode(self.hwp5file_rec.docinfo.open())

        import simplejson
        jsonobject = simplejson.load(stream)
        self.assertEquals(67, len(jsonobject))
