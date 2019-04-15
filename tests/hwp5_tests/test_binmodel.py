# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from io import BytesIO
from unittest import TestCase
import binascii
import codecs
import json
import sys

from hwp5.binmodel import BinData
from hwp5.binmodel import BorderFill
from hwp5.binmodel import Control
from hwp5.binmodel import ControlChar
from hwp5.binmodel import ControlData
from hwp5.binmodel import FaceName
from hwp5.binmodel import GShapeObjectControl
from hwp5.binmodel import HeaderParagraphList
from hwp5.binmodel import Hwp5File
from hwp5.binmodel import LanguageStruct
from hwp5.binmodel import ListHeader
from hwp5.binmodel import ModelStream
from hwp5.binmodel import ParaLineSegList
from hwp5.binmodel import ParaText
from hwp5.binmodel import Paragraph
from hwp5.binmodel import RecordModel
from hwp5.binmodel import ShapeComponent
from hwp5.binmodel import Style
from hwp5.binmodel import TableBody
from hwp5.binmodel import TableCaption
from hwp5.binmodel import TableCell
from hwp5.binmodel import TableControl
from hwp5.binmodel import TextboxParagraphList
from hwp5.binmodel import init_record_parsing_context
from hwp5.binmodel import model_to_json
from hwp5.binmodel import parse_model
from hwp5.binmodel import parse_models
from hwp5.binmodel import parse_models_intern
from hwp5.dataio import Enum
from hwp5.dataio import Flags
from hwp5.dataio import UINT32
from hwp5.dataio import WORD
from hwp5.filestructure import Hwp5FileOpener
from hwp5.recordstream import Record
from hwp5.recordstream import read_records
from hwp5.tagids import HWPTAG_BEGIN
from hwp5.treeop import STARTEVENT, ENDEVENT
from hwp5.treeop import prefix_event
from hwp5.utils import cached_property

from . import test_recordstream
from .fixtures import get_fixture_path


PY3 = sys.version_info.major == 3
if PY3:
    basestring = str
    unichr = chr


def TestContext(**ctx):
    ''' test context '''
    if 'version' not in ctx:
        ctx['version'] = (5, 0, 0, 0)
    return ctx


testcontext = TestContext()


class TestRecordParsing(TestCase):
    def test_init_record_parsing_context(self):
        record = dict(tagid=HWPTAG_BEGIN, payload=b'abcd')
        context = init_record_parsing_context(testcontext, record)

        self.assertEqual(record, context['record'])
        self.assertEqual(b'abcd', context['stream'].read())


class BinEmbeddedTest(TestCase):
    ctx = TestContext()
    stream = BytesIO(b'\x12\x04\xc0\x00\x01\x00\x02\x00\x03\x00'
                     b'\x6a\x00\x70\x00\x67\x00')

    def testParse(self):
        record = next(read_records(self.stream))
        context = init_record_parsing_context(testcontext, record)
        model = record
        parse_model(context, model)

        self.assertTrue(BinData, model['type'])
        self.assertEqual(BinData.StorageType.EMBEDDING,
                         BinData.Flags(model['content']['flags']).storage)
        self.assertEqual(2, model['content']['bindata']['storage_id'])
        self.assertEqual('jpg', model['content']['bindata']['ext'])


class LanguageStructTest(TestCase):
    def test_cls_dict_has_attributes(self):
        FontFace = LanguageStruct(b'FontFace', WORD)
        self.assertTrue('attributes' in FontFace.__dict__)


class TestBase(test_recordstream.TestBase):

    @cached_property
    def hwp5file_bin(self):
        return Hwp5File(self.olestg)

    hwp5file = hwp5file_bin


class FaceNameTest(TestBase):
    hwp5file_name = 'facename.hwp'

    def test_font_file_type(self):

        docinfo = self.hwp5file.docinfo
        facenames = (model for model in docinfo.models()
                     if model['type'] is FaceName)
        facenames = list(facenames)

        facename = facenames[0]['content']
        self.assertEqual(u'굴림', facename['name'])
        self.assertEqual(FaceName.FontFileType.TTF,
                         facename['flags'].font_file_type)

        facename = facenames[3]['content']
        self.assertEqual(u'휴먼명조', facename['name'])
        self.assertEqual(FaceName.FontFileType.HFT,
                         facename['flags'].font_file_type)

        facename = facenames[4]['content']
        self.assertEqual(u'한양신명조', facename['name'])
        self.assertEqual(FaceName.FontFileType.HFT,
                         facename['flags'].font_file_type)


class DocInfoTest(TestBase):
    hwp5file_name = 'facename2.hwp'

    def test_charshape_lang_facename(self):

        docinfo = self.hwp5file.docinfo
        styles = list(m for m in docinfo.models()
                      if m['type'] is Style)

        def style_lang_facename(style, lang):
            charshape_id = style['content']['charshape_id']
            return docinfo.charshape_lang_facename(charshape_id, lang)

        def style_lang_facename_name(style, lang):
            facename = style_lang_facename(style, lang)
            return facename['content']['name']

        self.assertEqual(u'바탕', style_lang_facename_name(styles[0], 'ko'))
        self.assertEqual(u'한컴돋움', style_lang_facename_name(styles[1], 'ko'))
        self.assertEqual(u'Times New Roman',
                         style_lang_facename_name(styles[2], 'en'))
        self.assertEqual(u'Arial', style_lang_facename_name(styles[3], 'en'))
        self.assertEqual(u'해서 약자', style_lang_facename_name(styles[4], 'cn'))
        self.assertEqual(u'해서 간자', style_lang_facename_name(styles[5], 'cn'))
        self.assertEqual(u'명조', style_lang_facename_name(styles[6], 'jp'))
        self.assertEqual(u'고딕', style_lang_facename_name(styles[7], 'jp'))


class BorderFillTest(TestBase):
    hwp5file_name = 'borderfill.hwp'

    def test_parse_borderfill(self):

        docinfo = self.hwp5file.docinfo
        borderfills = (model for model in docinfo.models()
                       if model['type'] is BorderFill)
        borderfills = list(borderfills)

        section = self.hwp5file.bodytext.section(0)
        tablecells = list(model for model in section.models()
                          if model['type'] is TableCell)
        for tablecell in tablecells:
            borderfill_id = tablecell['content']['borderfill_id']
            borderfill = borderfills[borderfill_id - 1]['content']
            tablecell['borderfill'] = borderfill

        borderfill = tablecells[0]['borderfill']
        self.assertEqual(0, borderfill['fillflags'])
        self.assertEqual(None, borderfill.get('fill_colorpattern'))
        self.assertEqual(None, borderfill.get('fill_gradation'))
        self.assertEqual(None, borderfill.get('fill_image'))

        borderfill = tablecells[1]['borderfill']
        self.assertEqual(1, borderfill['fillflags'])
        self.assertEqual(dict(background_color=0xff7f3f,
                              pattern_color=0,
                              pattern_type_flags=0xffffffff),
                         borderfill['fill_colorpattern'])
        self.assertEqual(None, borderfill.get('fill_gradation'))
        self.assertEqual(None, borderfill.get('fill_image'))

        borderfill = tablecells[2]['borderfill']
        self.assertEqual(4, borderfill['fillflags'])
        self.assertEqual(None, borderfill.get('fill_colorpattern'))
        self.assertEqual(dict(blur=40, center=dict(x=0, y=0),
                              colors=[0xff7f3f, 0],
                              shear=90, type=1),
                         borderfill['fill_gradation'])
        self.assertEqual(None, borderfill.get('fill_image'))

        borderfill = tablecells[3]['borderfill']
        self.assertEqual(2, borderfill['fillflags'])
        self.assertEqual(None, borderfill.get('fill_colorpattern'))
        self.assertEqual(None, borderfill.get('fill_gradation'))
        self.assertEqual(dict(flags=5, bindata_id=1, effect=0, brightness=0,
                              contrast=0),
                         borderfill.get('fill_image'))

        borderfill = tablecells[4]['borderfill']
        self.assertEqual(3, borderfill['fillflags'])
        self.assertEqual(dict(background_color=0xff7f3f,
                              pattern_color=0,
                              pattern_type_flags=0xffffffff),
                         borderfill['fill_colorpattern'])
        self.assertEqual(None, borderfill.get('fill_gradation'))
        self.assertEqual(dict(flags=5, bindata_id=1, effect=0, brightness=0,
                              contrast=0),
                         borderfill.get('fill_image'))

        borderfill = tablecells[5]['borderfill']
        self.assertEqual(6, borderfill['fillflags'])
        self.assertEqual(None, borderfill.get('fill_colorpattern'))
        self.assertEqual(dict(blur=40, center=dict(x=0, y=0),
                              colors=[0xff7f3f, 0],
                              shear=90, type=1),
                         borderfill['fill_gradation'])
        self.assertEqual(dict(flags=5, bindata_id=1, effect=0, brightness=0,
                              contrast=0),
                         borderfill.get('fill_image'))


class StyleTest(TestBase):
    hwp5file_name = 'charstyle.hwp'

    def test_charstyle(self):

        docinfo = self.hwp5file.docinfo
        styles = (model for model in docinfo.models()
                  if model['type'] is Style)
        styles = list(styles)

        style = styles[0]['content']
        self.assertEqual(dict(name='Normal',
                              unknown=0,
                              parashape_id=0,
                              charshape_id=1,
                              next_style_id=0,
                              lang_id=1042,
                              flags=0,
                              local_name=u'바탕글'),
                         style)
        charstyle = styles[13]['content']
        self.assertEqual(dict(name='',
                              unknown=0,
                              parashape_id=0,
                              charshape_id=1,
                              next_style_id=0,
                              lang_id=1042,
                              flags=1,
                              local_name=u'글자스타일'),
                         charstyle)


class ParaCharShapeTest(TestBase):

    @property
    def paracharshape_record(self):
        return self.bodytext.section(0).record(2)

    def test_read_paracharshape(self):
        parent_context = dict()
        parent_model = dict(content=dict(charshapes=5))

        record = self.paracharshape_record
        context = init_record_parsing_context(dict(), record)
        context['parent'] = parent_context, parent_model
        model = record
        parse_model(context, model)
        self.assertEqual(dict(charshapes=[(0, 7), (19, 8), (23, 7), (24, 9),
                                          (26, 7)]),
                         model['content'])


class TableTest(TestBase):

    @property
    def stream(self):
        return BytesIO(b'G\x04\xc0\x02 lbt\x11#*\x08\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x06\x9e\x00\x00D\x10\x00\x00\x00\x00\x00\x00'
                       b'\x1b\x01\x1b\x01\x1b\x01\x1b\x01\xed\xad\xa2V\x00\x00'
                       b'\x00\x00')

    @cached_property
    def tablecontrol_record(self):
        return self.bodytext.section(0).record(30)

    @cached_property
    def tablecaption_record(self):
        return self.bodytext.section(0).record(68)

    @cached_property
    def tablebody_record(self):
        return self.bodytext.section(0).record(31)

    @cached_property
    def tablecell_record(self):
        return self.bodytext.section(0).record(32)

    def testParsePass1(self):
        record = next(read_records(self.stream))
        context = init_record_parsing_context(testcontext, record)
        model = record
        parse_model(context, model)

        self.assertTrue(TableControl, model['type'])
        self.assertEqual(1453501933, model['content']['instance_id'])
        self.assertEqual(0x0, model['content']['x'])
        self.assertEqual(0x0, model['content']['y'])
        self.assertEqual(0x1044, model['content']['height'])
        self.assertEqual(0x9e06, model['content']['width'])
        self.assertEqual(0, model['content']['unknown1'])
        self.assertEqual(0x82a2311, model['content']['flags'])
        self.assertEqual(0, model['content']['z_order'])
        self.assertEqual(dict(left=283, right=283, top=283, bottom=283),
                         model['content']['margin'])
        self.assertEqual('tbl ', model['content']['chid'])

    def test_parse_child_table_body(self):
        record = self.tablecontrol_record
        context = init_record_parsing_context(testcontext, record)

        tablebody_record = self.tablebody_record
        child_context = init_record_parsing_context(testcontext,
                                                    tablebody_record)
        child_model = dict(type=TableBody, content=dict())
        child = (child_context, child_model)

        self.assertFalse(context.get('seen_table_body'))
        TableControl.on_child(dict(), context, child)
        # 'seen_table_body' in table record context should have been changed
        # to True
        self.assertTrue(context['seen_table_body'])
        # model and attributes should not have been changed
        self.assertEqual(dict(), child_model['content'])

    def test_parse_child_table_cell(self):
        record = self.tablecontrol_record
        context = init_record_parsing_context(testcontext, record)
        model = record
        parse_model(context, model)

        context['seen_table_body'] = True

        child_record = self.tablecell_record
        child_context = init_record_parsing_context(testcontext, child_record)
        child_model = child_record
        child_context['parent'] = context, model
        parse_model(child_context, child_model)
        self.assertEqual(TableCell, child_model['type'])
        self.assertEqual(TableCell, child_model['type'])
        self.assertEqual(dict(padding=dict(top=141, right=141, bottom=141,
                                           left=141),
                              rowspan=1,
                              colspan=1,
                              borderfill_id=1,
                              height=282,
                              listflags=32,
                              width=20227,
                              unknown1=0,
                              unknown_width=20227,
                              paragraphs=1,
                              col=0,
                              row=0), child_model['content'])
        self.assertEqual(b'', child_context['stream'].read())

    def test_parse_child_table_caption(self):
        record = self.tablecontrol_record
        context = init_record_parsing_context(testcontext, record)
        model = record
        parse_model(context, model)

        context['seen_table_body'] = False

        child_record = self.tablecaption_record
        child_context = init_record_parsing_context(testcontext, child_record)
        child_context['parent'] = context, model
        child_model = child_record
        parse_model(child_context, child_model)
        self.assertEqual(TableCaption, child_model['type'])
        self.assertEqual(dict(listflags=0,
                              width=8504,
                              max_width=40454,
                              unknown1=0,
                              flags=3,
                              separation=850,
                              paragraphs=2), child_model['content'])
        self.assertEqual(b'', child_context['stream'].read())


class ShapeComponentTest(TestBase):

    hwp5file_name = 'textbox.hwp'

    @cached_property
    def control_gso_record(self):
        return self.bodytext.section(0).record(12)

    @cached_property
    def shapecomponent_record(self):
        return self.bodytext.section(0).record(19)

    @cached_property
    def textbox_paragraph_list_record(self):
        return self.bodytext.section(0).record(20)

    def test_parse_shapecomponent_textbox_paragraph_list(self):
        record = self.shapecomponent_record
        context = init_record_parsing_context(testcontext, record)
        model = record
        model['type'] = ShapeComponent

        child_record = self.textbox_paragraph_list_record
        child_context = init_record_parsing_context(testcontext,
                                                    child_record)
        child_context['parent'] = context, model
        child_model = child_record
        parse_model(child_context, child_model)
        self.assertEqual(TextboxParagraphList, child_model['type'])
        self.assertEqual(dict(listflags=32,
                              padding=dict(top=283, right=283, bottom=283,
                                           left=283),
                              unknown1=0,
                              maxwidth=11763,
                              paragraphs=1), child_model['content'])
        self.assertEqual(b'', child_context['stream'].read())

    def test_parse(self):

        # parent_record = self.control_gso_record

        # if parent model is GShapeObjectControl
        parent_model = dict(type=GShapeObjectControl)

        record = self.shapecomponent_record
        context = init_record_parsing_context(testcontext, record)
        context['parent'] = dict(), parent_model
        model = record
        parse_model(context, model)

        self.assertEqual(model['type'], ShapeComponent)
        self.assertTrue('chid0' in model['content'])

        # if parent model is not GShapeObjectControl
        # TODO

    def test_rect_fill(self):
        self.hwp5file_name = 'shapecomponent-rect-fill.hwp'

        section = self.hwp5file_bin.bodytext.section(0)
        shapecomps = (model for model in section.models()
                      if model['type'] is ShapeComponent)
        shapecomps = list(shapecomps)

        shapecomp = shapecomps.pop(0)['content']
        self.assertFalse(shapecomp['fill_flags'].fill_colorpattern)
        self.assertFalse(shapecomp['fill_flags'].fill_gradation)
        self.assertFalse(shapecomp['fill_flags'].fill_image)

        shapecomp = shapecomps.pop(0)['content']
        self.assertTrue(shapecomp['fill_flags'].fill_colorpattern)
        self.assertFalse(shapecomp['fill_flags'].fill_gradation)
        self.assertFalse(shapecomp['fill_flags'].fill_image)
        self.assertEqual(dict(background_color=0xff7f3f,
                              pattern_color=0,
                              pattern_type_flags=0xffffffff),
                         shapecomp['fill_colorpattern'])
        self.assertEqual(None, shapecomp.get('fill_gradation'))
        self.assertEqual(None, shapecomp.get('fill_image'))

        shapecomp = shapecomps.pop(0)['content']
        self.assertFalse(shapecomp['fill_flags'].fill_colorpattern)
        self.assertTrue(shapecomp['fill_flags'].fill_gradation)
        self.assertFalse(shapecomp['fill_flags'].fill_image)
        self.assertEqual(None, shapecomp.get('fill_colorpattern'))
        self.assertEqual(dict(type=1, shear=90,
                              center=dict(x=0, y=0),
                              colors=[0xff7f3f, 0],
                              blur=50), shapecomp['fill_gradation'])
        self.assertEqual(None, shapecomp.get('fill_image'))

        shapecomp = shapecomps.pop(0)['content']
        self.assertFalse(shapecomp['fill_flags'].fill_colorpattern)
        self.assertFalse(shapecomp['fill_flags'].fill_gradation)
        self.assertTrue(shapecomp['fill_flags'].fill_image)
        self.assertEqual(None, shapecomp.get('fill_colorpattern'))
        self.assertEqual(None, shapecomp.get('fill_gradation'))
        self.assertEqual(dict(flags=5, bindata_id=1, effect=0, brightness=0,
                              contrast=0),
                         shapecomp['fill_image'])

        shapecomp = shapecomps.pop(0)['content']
        self.assertTrue(shapecomp['fill_flags'].fill_colorpattern)
        self.assertFalse(shapecomp['fill_flags'].fill_gradation)
        self.assertTrue(shapecomp['fill_flags'].fill_image)
        self.assertEqual(dict(background_color=0xff7f3f,
                              pattern_color=0,
                              pattern_type_flags=0xffffffff),
                         shapecomp['fill_colorpattern'])
        self.assertEqual(None, shapecomp.get('fill_gradation'))
        self.assertEqual(dict(flags=5, bindata_id=1, effect=0, brightness=0,
                              contrast=0),
                         shapecomp['fill_image'])

        shapecomp = shapecomps.pop(0)['content']
        self.assertFalse(shapecomp['fill_flags'].fill_colorpattern)
        self.assertTrue(shapecomp['fill_flags'].fill_gradation)
        self.assertTrue(shapecomp['fill_flags'].fill_image)
        self.assertEqual(None, shapecomp.get('fill_colorpattern'))
        self.assertEqual(dict(type=1, shear=90,
                              center=dict(x=0, y=0),
                              colors=[0xff7f3f, 0],
                              blur=50), shapecomp['fill_gradation'])
        self.assertEqual(dict(flags=5, bindata_id=1, effect=0, brightness=0,
                              contrast=0),
                         shapecomp['fill_image'])

    def test_colorpattern_gradation(self):
        # 5005-shapecomponent-with-colorpattern-and-gradation.dat
        records = \
            [{'level': 1,
              'payload': b' osg\x10bj\x04\x00\x00\x00\x00\x0c\x00\x00\x004\xbc\x00\x00l\x06\x01\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00G\xechf\x00\x00\x00\x00',  # noqa
              'seqno': 12,
              'size': 44,
              'tagid': 71,
              'tagname': 'HWPTAG_CTRL_HEADER'},
             {'level': 2,
              'payload': b'noc$noc$\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x004\xbc\x00\x00l\x06\x01\x004\xbc\x00\x00l\x06\x01\x00\x00\x00\x03\x00\x00\x00w\x00WPS \xb9\xae\x01\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00lop$noc$',  # noqa
              'seqno': 13,
              'size': 206,
              'tagid': 76,
              'tagname': 'HWPTAG_SHAPE_COMPONENT'},
             {'level': 3,
              'payload': b'lop$\x00\x00\x00\x00\xcc\x1b\x00\x00\x01\x00\x01\x004\xbc\x00\x00\xa0\xea\x00\x004\xbc\x00\x00\xa0\xea\x00\x00\x00\x00\x00\x00\x10\x00\x1a^\x00\x00Pu\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\xcc\xbb@\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe4\x00\x00\xc8\x00\x00\x00\x01\x00\x00\xd1\x00\x00\x00\x00\x00\x00\x00\x00\x00',  # noqa
              'seqno': 14,
              'size': 309,
              'tagid': 76,
              'tagname': 'HWPTAG_SHAPE_COMPONENT'},
             {'level': 4,
              'payload': b'\x06\x00\x00\x00`,\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x9c\xea\x00\x000\xbc\x00\x00\x9c\xea\x00\x000\xbc\x00\x00\x00\x00\x00\x00\xac\x8a\x00\x00\x00\x00\x00\x00',  # noqa
              'seqno': 15,
              'size': 52,
              'tagid': 82,
              'tagname': 'HWPTAG_SHAPE_COMPONENT_POLYGON'},
             {'level': 3,
              'payload': b'noc$\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00tb\x00\x00\xf4-\x00\x00tb\x00\x00\xf4-\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\r\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x05\x00cer$cer$cer$cer$cer$',  # noqa
              'seqno': 16,
              'size': 310,
              'tagid': 76,
              'tagname': 'HWPTAG_SHAPE_COMPONENT'},
             {'level': 4,
              'payload': b'cer$\xd8,\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x04\x0f\x00\x00\xf4-\x00\x00\x04\x0f\x00\x00\xf4-\x00\x00\x00\x00\x00\x01\x00\x00\x82\x07\x00\x00\xfa\x16\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00l\xc6@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\xc8\x00\x00\x00\x00\x00\x00\xd1\x00\x05\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x01\xb4\x00\x00\x00\x00\x00\x00\x00d\x00\x00\x002\x00\x00\x00\x02\x00\x00\x00\x00\xfc\x00\x00\xe0\xfc\xc8\x00\x01\x00\x00\x002',  # noqa
              'seqno': 17,
              'size': 447,
              'tagid': 76,
              'tagname': 'HWPTAG_SHAPE_COMPONENT'}]

        context = dict(version=(5, 0, 0, 5))
        models = parse_models(context, records)
        models = list(models)
        self.assertEqual(1280, models[-1]['content']['fill_flags'])
        colorpattern = models[-1]['content']['fill_colorpattern']
        gradation = models[-1]['content']['fill_gradation']
        self.assertEqual(32768, colorpattern['background_color'])
        self.assertEqual(0, colorpattern['pattern_color'])
        self.assertEqual(0xffffffff, colorpattern['pattern_type_flags'])

        self.assertEqual(50, gradation['blur'])
        self.assertEqual(dict(x=0, y=100), gradation['center'])
        self.assertEqual([64512, 13171936], gradation['colors'])
        self.assertEqual(180, gradation['shear'])
        self.assertEqual(1, gradation['type'])
        self.assertEqual(1, models[-1]['content']['fill_shape'])
        self.assertEqual(50, models[-1]['content']['fill_blur_center'])

    def test_colorpattern_gradation_5017(self):
        fixturename = '5017-shapecomponent-with-colorpattern-and-gradation.bin'
        f = self.open_fixture(fixturename, 'rb')
        try:
            records = list(read_records(f))
        finally:
            f.close()

        context = dict(version=(5, 0, 1, 7))
        models = parse_models(context, records)
        models = list(models)
        self.assertEqual(1280, models[-1]['content']['fill_flags'])
        colorpattern = models[-1]['content']['fill_colorpattern']
        gradation = models[-1]['content']['fill_gradation']
        self.assertEqual(32768, colorpattern['background_color'])
        self.assertEqual(0, colorpattern['pattern_color'])
        self.assertEqual(0xffffffff, colorpattern['pattern_type_flags'])

        self.assertEqual(50, gradation['blur'])
        self.assertEqual(dict(x=0, y=100), gradation['center'])
        self.assertEqual([64512, 13171936], gradation['colors'])
        self.assertEqual(180, gradation['shear'])
        self.assertEqual(1, gradation['type'])
        self.assertEqual(1, models[-1]['content']['fill_shape'])
        self.assertEqual(50, models[-1]['content']['fill_blur_center'])


class HeaderFooterTest(TestBase):

    hwp5file_name = 'headerfooter.hwp'

    @cached_property
    def header_record(self):
        return self.bodytext.section(0).record(16)

    @cached_property
    def header_paragraph_list_record(self):
        return self.bodytext.section(0).record(17)

    def test_parse_child(self):
        record = self.header_record
        context = init_record_parsing_context(testcontext, record)
        model = record
        parse_model(context, model)

        child_record = self.header_paragraph_list_record
        child_context = init_record_parsing_context(testcontext,
                                                    child_record)
        child_context['parent'] = context, model
        child_model = child_record
        parse_model(child_context, child_model)
        self.assertEqual(HeaderParagraphList, child_model['type'])
        self.assertEqual(dict(textrefsbitmap=0,
                              numberrefsbitmap=0,
                              height=4252,
                              listflags=0,
                              width=42520,
                              unknown1=0,
                              paragraphs=1), child_model['content'])
        # TODO
        # self.assertEqual('', child_context['stream'].read())


class ListHeaderTest(TestCase):
    ctx = TestContext()
    record_bytes = (b'H\x08`\x02\x01\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00'
                    b'\x01\x00\x01\x00\x03O\x00\x00\x1a\x01\x00\x00\x8d\x00'
                    b'\x8d\x00\x8d\x00\x8d\x00\x01\x00\x03O\x00\x00')
    stream = BytesIO(record_bytes)

    def testParse(self):
        record = next(read_records(self.stream))
        context = init_record_parsing_context(testcontext, record)
        model = record
        parse_model(context, model)

        self.assertEqual(ListHeader, model['type'])
        self.assertEqual(1, model['content']['paragraphs'])
        self.assertEqual(0x20, model['content']['listflags'])
        self.assertEqual(0, model['content']['unknown1'])
        self.assertEqual(8, context['stream'].tell())


class TableBodyTest(TestCase):
    ctx = TestContext(version=(5, 0, 1, 7))
    stream = BytesIO(b'M\x08\xa0\x01\x06\x00\x00\x04\x02\x00\x02\x00\x00\x00'
                     b'\x8d\x00\x8d\x00\x8d\x00\x8d\x00\x02\x00\x02\x00\x01'
                     b'\x00\x00\x00')

    def test_parse_model(self):
        record = next(read_records(self.stream))
        context = init_record_parsing_context(self.ctx, record)
        model = record

        parse_model(context, model)
        model_type = model['type']
        model_content = model['content']

        self.assertEqual(TableBody, model_type)
        self.assertEqual(dict(left=141, right=141, top=141, bottom=141),
                         model_content['padding'])
        self.assertEqual(0x4000006, model_content['flags'])
        self.assertEqual(2, model_content['cols'])
        self.assertEqual(2, model_content['rows'])
        self.assertEqual(1, model_content['borderfill_id'])
        self.assertEqual([2, 2], model_content['rowcols'])
        self.assertEqual(0, model_content['cellspacing'])
        self.assertEqual([], model_content['validZones'])


class Pass2Test(TestCase):
    ctx = TestContext()

    def test_pass2_events(self):

        def items():
            yield Record(HWPTAG_BEGIN + 4, 0, ''),
            yield Record(HWPTAG_BEGIN + 3, 1, ''),
            yield Record(HWPTAG_BEGIN + 2, 0, ''),
            yield Record(HWPTAG_BEGIN + 1, 0, ''),
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
        self.assertEqual(expected, events)


class LineSegTest(TestCase):
    def testDecode(self):
        data = ('00000000481e0000e8030000e80300005203000058020000dc0500003ca00'
                '000000006003300000088240000e8030000e80300005203000058020000dc'
                '0500003ca000000000060067000000c82a0000e8030000e80300005203000'
                '058020000dc0500003ca0000000000600')
        data = binascii.a2b_hex(data)
        lines = list(ParaLineSegList.decode(dict(), data))
        self.assertEqual(0, lines[0]['chpos'])
        self.assertEqual(51, lines[1]['chpos'])
        self.assertEqual(103, lines[2]['chpos'])


class TableCaptionCellTest(TestCase):
    ctx = TestContext(version=(5, 0, 1, 7))
    records_bytes = (b'G\x04\xc0\x02 lbt\x10#*(\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa
                     b'\x06\x9e\x00\x00\x04\n\x00\x00\x03\x00\x00\x00\x1b\x01R'   # noqa
                     b'\x037\x02n\x04\n^\xc0V\x00\x00\x00\x00H\x08`\x01\x02\x00'  # noqa
                     b'\x00\x00\x00\x00\x00\x00\x03\x00\x00\x008!\x00\x00R\x03'   # noqa
                     b'\x06\x9e\x00\x00M\x08\xa0\x01\x06\x00\x00\x04\x02\x00'     # noqa
                     b'\x02\x00\x00\x00\x8d\x00\x8d\x00\x8d\x00\x8d\x00\x02\x00'  # noqa
                     b'\x02\x00\x01\x00\x00\x00H\x08`\x02\x01\x00\x00\x00 \x00'   # noqa
                     b'\x00\x00\x00\x00\x00\x00\x01\x00\x01\x00\x03O\x00\x00'     # noqa
                     b'\x1a\x01\x00\x00\x8d\x00\x8d\x00\x8d\x00\x8d\x00\x01\x00'  # noqa
                     b'\x03O\x00\x00')

    def testParsePass1(self):
        stream = BytesIO(self.records_bytes)
        records = list(read_records(stream))
        result = list(parse_models_intern(self.ctx, records))

        tablecaption = result[1]
        context, model = tablecaption
        model_type = model['type']
        model_content = model['content']
        stream = context['stream']

        self.assertEqual(TableCaption, model_type)
        self.assertEqual(22, stream.tell())
        # ListHeader attributes
        self.assertEqual(2, model_content['paragraphs'])
        self.assertEqual(0x0, model_content['listflags'])
        self.assertEqual(0, model_content['unknown1'])
        # TableCaption model_content
        self.assertEqual(3, model_content['flags'])
        self.assertEqual(8504, model_content['width'])
        self.assertEqual(850, model_content['separation'])
        self.assertEqual(40454, model_content['max_width'])

        tablecell = result[3]
        context, model = tablecell
        model_type = model['type']
        model_content = model['content']
        stream = context['stream']
        self.assertEqual(TableCell, model_type)
        self.assertEqual(38, stream.tell())
        # ListHeader model_content
        self.assertEqual(1, model_content['paragraphs'])
        self.assertEqual(0x20, model_content['listflags'])
        self.assertEqual(0, model_content['unknown1'])
        # TableCell model_content
        self.assertEqual(0, model_content['col'])
        self.assertEqual(0, model_content['row'])
        self.assertEqual(1, model_content['colspan'])
        self.assertEqual(1, model_content['rowspan'])
        self.assertEqual(0x4f03, model_content['width'])
        self.assertEqual(0x11a, model_content['height'])
        self.assertEqual(dict(left=141, right=141, top=141, bottom=141),
                         model_content['padding'])
        self.assertEqual(1, model_content['borderfill_id'],)
        self.assertEqual(0x4f03, model_content['unknown_width'])


class TestRecordModel(TestCase):
    def test_assign_enum_flags_name(self):

        class FooRecord(RecordModel):
            Bar = Flags(UINT32)
            Baz = Enum()
        self.assertEqual('Bar', FooRecord.Bar.__name__)
        self.assertEqual('Baz', FooRecord.Baz.__name__)


class TestControlType(TestCase):
    def test_ControlType(self):

        class FooControl(Control):
            chid = 'foo!'
        try:
            class Foo2Control(Control):
                chid = 'foo!'
        except Exception:
            pass
        else:
            assert False, 'Exception expected'


class TestControlChar(TestBase):

    def test_decode(self):
        paratext_record = self.hwp5file.bodytext.section(0).record(1)
        payload = paratext_record['payload']
        controlchar = ControlChar.decode(payload[0:16])
        self.assertEqual(dict(code=ord(ControlChar.SECTION_COLUMN_DEF),
                              chid='secd',
                              param=b'\x00' * 8), controlchar)

    def test_find(self):
        bytes = b'\x41\x00'
        self.assertEqual((2, 2), ControlChar.find(bytes, 0))

    def test_tab(self):
        self.hwp5file_name = 'tabdef.hwp'
        models = self.hwp5file.bodytext.section(0).models()
        paratexts = list(model for model in models
                         if model['type'] is ParaText)

        def paratext_tabs(paratext):
            for range, chunk in paratext['content']['chunks']:
                if isinstance(chunk, dict):
                    if unichr(chunk['code']) == ControlChar.TAB:
                        yield chunk
        self.assertEqual(set(['code', 'param']),
                         set(next(paratext_tabs(paratexts[0])).keys()))

        def paratext_tab_params(paratext):
            for tab in paratext_tabs(paratext):
                yield tab['param']

        tabs = list(paratext_tab_params(paratexts.pop(0)))
        self.assertEqual([(4000, 1)] * 3,
                         list((tab['width'], tab['unknown1'])
                              for tab in tabs))

        tabs = list(paratext_tab_params(paratexts.pop(0)))
        self.assertEqual([(2000, 1), (1360, 1), (1360, 1)],
                         list((tab['width'], tab['unknown1'])
                              for tab in tabs))

        tabs = list(paratext_tab_params(paratexts.pop(0)))
        self.assertEqual([(2328, 2)] * 3,
                         list((tab['width'], tab['unknown1'])
                              for tab in tabs))

        tabs = list(paratext_tab_params(paratexts.pop(0)))
        self.assertEqual([(2646, 3), (2292, 3), (2292, 3)],
                         list((tab['width'], tab['unknown1'])
                              for tab in tabs))

        tabs = list(paratext_tab_params(paratexts.pop(0)))
        self.assertEqual([(2104, 4)] * 3,
                         list((tab['width'], tab['unknown1'])
                              for tab in tabs))

        tabs = list(paratext_tab_params(paratexts.pop(0)))
        self.assertEqual([(4000, 1), (3360, 1), (3360, 1)],
                         list((tab['width'], tab['unknown1'])
                              for tab in tabs))

        tabs = list(paratext_tab_params(paratexts.pop(0)))
        self.assertEqual([(4000, 1), (3328, 1)],
                         list((tab['width'], tab['unknown1'])
                              for tab in tabs))

        tabs = list(paratext_tab_params(paratexts.pop(0)))
        self.assertEqual([(4000, 1), (3672, 1), (33864, 2)],
                         list((tab['width'], tab['unknown1'])
                              for tab in tabs))


class TestFootnoteShape(TestBase):

    def test_footnote_shape(self):
        path = get_fixture_path('footnote-endnote.hwp')
        hwp5file_opener = Hwp5FileOpener(self.olestorage_opener, Hwp5File)
        hwp5file = hwp5file_opener.open_hwp5file(path)

        models = hwp5file.bodytext.section(0).models()
        models = list(models)
        fnshape = models[6]
        self.assertEqual(850, fnshape['content']['splitter_margin_top'])
        self.assertEqual(567, fnshape['content']['splitter_margin_bottom'])


class TestControlData(TestBase):
    def test_parse(self):
        # 5006-controldata.record
        record = \
            {'level': 2,
             'payload': b'\x1b\x02\x01\x00\x00\x00\x00@\x01\x00\x03\x00X\xc7H\xc5\x85\xba',  # noqa
             'seqno': 27,
             'size': 18,
             'tagid': 87,
             'tagname': 'HWPTAG_CTRL_DATA'}
        context = init_record_parsing_context(dict(), record)
        model = record
        parse_model(context, model)
        self.assertEqual(ControlData, model['type'])
        self.assertEqual(dict(), model['content'])


class TestModelJson(TestBase):
    def test_model_to_json(self):
        model = self.hwp5file.docinfo.model(0)
        json_string = model_to_json(model)

        jsonobject = json.loads(json_string)
        self.assertEqual('DocumentProperties', jsonobject['type'])

    def test_model_to_json_should_not_modify_input(self):
        model = self.hwp5file.docinfo.model(0)
        model_to_json(model, indent=2, sort_keys=True)
        self.assertFalse(isinstance(model['type'], basestring))

    def test_model_to_json_with_controlchar(self):
        model = self.hwp5file.bodytext.section(0).model(1)
        json_string = model_to_json(model)

        jsonobject = json.loads(json_string)
        self.assertEqual('ParaText', jsonobject['type'])
        self.assertEqual([[0, 8],
                          dict(code=2, param='\x00' * 8, chid='secd')],
                         jsonobject['content']['chunks'][0])

    def test_model_to_json_with_unparsed(self):

        model = dict(type=RecordModel, content=[], payload=b'\x00\x01\x02\x03',
                     unparsed=b'\xff\xfe\xfd\xfc')
        json_string = model_to_json(model)

        jsonobject = json.loads(json_string)
        self.assertEqual(['ff fe fd fc'], jsonobject['unparsed'])

    def test_generate_models_json_array(self):
        models_json = self.hwp5file.bodytext.section(0).models_json()
        gen = models_json.generate()

        json_array = json.loads(''.join(gen))
        self.assertEqual(128, len(json_array))


class TestModelStream(TestBase):
    @cached_property
    def docinfo(self):
        return ModelStream(self.hwp5file_rec['DocInfo'],
                           self.hwp5file_rec.header.version)

    def test_models(self):
        self.assertEqual(67, len(list(self.docinfo.models())))

    def test_models_treegrouped(self):
        section = self.bodytext.section(0)
        for idx, paragraph_models in enumerate(section.models_treegrouped()):
            paragraph_models = list(paragraph_models)
            leader = paragraph_models[0]
            # leader should be a Paragraph
            self.assertEqual(Paragraph, leader['type'])
            # leader should be at top-level
            self.assertEqual(0, leader['level'])
            # print idx, leader['record']['seqno'], len(paragraph_models)

    def test_model(self):
        model = self.docinfo.model(0)
        self.assertEqual(0, model['seqno'])

        model = self.docinfo.model(10)
        self.assertEqual(10, model['seqno'])

    def test_models_json_open(self):
        f = self.docinfo.models_json().open()
        f = codecs.getreader('utf-8')(f)
        try:
            self.assertEqual(67, len(json.load(f)))
        finally:
            f.close()
