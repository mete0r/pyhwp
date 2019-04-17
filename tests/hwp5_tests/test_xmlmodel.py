# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from io import BytesIO
from unittest import TestCase
from xml.etree import ElementTree
import base64
import io

from hwp5 import binmodel
from hwp5 import xmlmodel
from hwp5 import treeop
from hwp5.binmodel import BinData
from hwp5.binmodel import ControlChar
from hwp5.binmodel import PageDef
from hwp5.binmodel import ParaCharShape
from hwp5.binmodel import ParaLineSeg
from hwp5.binmodel import ParaText
from hwp5.binmodel import SectionDef
from hwp5.plat import createOleStorageOpener
from hwp5.tagids import HWPTAG_PARA_LINE_SEG
from hwp5.treeop import STARTEVENT, ENDEVENT
from hwp5.utils import cached_property
from hwp5.xmlmodel import DocInfo
from hwp5.xmlmodel import Hwp5File
from hwp5.xmlmodel import ModelEventStream
from hwp5.xmlmodel import Section
from hwp5.xmlmodel import XmlEvents
from hwp5.xmlmodel import embed_bindata
from hwp5.xmlmodel import line_segmented
from hwp5.xmlmodel import make_ranged_shapes
from hwp5.xmlmodel import merge_paragraph_text_charshape_lineseg
from hwp5.xmlmodel import split_and_shape

from . import test_binmodel
from .fixtures import get_fixture_path


class TestBase(test_binmodel.TestBase):

    @cached_property
    def hwp5file_xml(self):
        return Hwp5File(self.olestg)

    hwp5file = hwp5file_xml


class TestXmlEvents(TestBase):

    def test_dump_quoteattr_cr(self):
        sio = BytesIO()

        context = dict()
        attrs = dict(char='\r')
        events = [(STARTEVENT, (ControlChar, attrs, context)),
                  (ENDEVENT, (ControlChar, attrs, context))]
        xmlevents = XmlEvents(iter(events))
        xmlevents.dump(sio)

        data = sio.getvalue()
        self.assertTrue(b'&#13;' in data)

    def test_bytechunks_quoteattr_cr(self):

        context = dict()
        attrs = dict(char='\r')
        item = (ControlChar, attrs, context)
        modelevents = [(STARTEVENT, item),
                       (ENDEVENT, item)]
        xmlevents = XmlEvents(iter(modelevents))
        xml = b''.join(xmlevents.bytechunks())

        self.assertTrue(b'&#13;' in xml)


class TestModelEventStream(TestBase):

    @cached_property
    def docinfo(self):
        return ModelEventStream(
            self.hwp5file_bin,
            self.hwp5file_bin,
            self.hwp5file_bin['DocInfo'],
        )

    def test_modelevents(self):
        self.assertEqual(len(list(self.docinfo.models())) * 2,
                         len(list(self.docinfo.modelevents())))
        # print len(list(self.docinfo.modelevents()))


class TestDocInfo(TestBase):

    @cached_property
    def docinfo(self):
        return DocInfo(
            self.hwp5file_bin,
            self.hwp5file_bin,
            self.hwp5file_bin['DocInfo'],
        )

    def test_events(self):
        events = list(self.docinfo.events())
        self.assertEqual(136, len(events))
        # print len(events)

        # without embedbin, no <text> is embedded
        self.assertTrue('<text>' not in events[4][1][1]['bindata'])

    def test_events_with_embedbin(self):
        bindata = self.hwp5file_bin['BinData']
        events = list(self.docinfo.events(embedbin=bindata))
        self.assertTrue('<text>' in events[4][1][1]['bindata'])
        self.assertEqual(bindata['BIN0002.jpg'].open().read(),
                         base64.b64decode(events[4][1][1]
                                          ['bindata']['<text>']))


class TestSection(TestBase):

    def test_events(self):
        section = Section(
            self.hwp5file_bin,
            self.hwp5file_bin['BodyText'],
            self.hwp5file_bin['BodyText']['Section0'],
        )
        events = list(section.events())
        ev, (tag, attrs, ctx) = events[0]
        self.assertEqual((STARTEVENT, SectionDef), (ev, tag))
        self.assertFalse('section-id' in attrs)

        ev, (tag, attrs, ctx) = events[1]
        self.assertEqual((STARTEVENT, PageDef), (ev, tag))

        ev, (tag, attrs, ctx) = events[2]
        self.assertEqual((ENDEVENT, PageDef), (ev, tag))

        ev, (tag, attrs, ctx) = events[-1]
        self.assertEqual((ENDEVENT, SectionDef), (ev, tag))


class TestHwp5File(TestBase):

    def test_docinfo_class(self):
        self.assertTrue(isinstance(self.hwp5file.docinfo, DocInfo))

    def test_events(self):
        list(self.hwp5file.events())

    def test_events_embedbin_without_bindata(self):
        # see issue 76: https://github.com/mete0r/pyhwp/issues/76
        self.hwp5file_name = 'parashape.hwp'  # an hwp5file without BinData
        hwp5file = self.hwp5file
        self.assertTrue('BinData' not in hwp5file)
        list(hwp5file.events(embedbin=True))

    def test_xmlevents(self):
        events = iter(self.hwp5file.xmlevents())
        ev = next(events)
        self.assertEqual((STARTEVENT,
                          ('HwpDoc', dict(version='5.0.1.7'))), ev)
        list(events)

    def test_xmlevents_dump(self):
        with io.open(self.id() + '.xml', 'wb+') as outfile:
            self.hwp5file.xmlevents().dump(outfile)

            outfile.seek(0)
            doc = ElementTree.parse(outfile)

        self.assertEqual('HwpDoc', doc.getroot().tag)


class TestShapedText(TestCase):
    def test_make_shape_range(self):
        charshapes = [(0, 'A'), (4, 'B'), (6, 'C'), (10, 'D')]
        ranged_shapes = make_ranged_shapes(charshapes)
        self.assertEqual([((0, 4), 'A'), ((4, 6), 'B'), ((6, 10), 'C'),
                          ((10, 0x7fffffff), 'D')], list(ranged_shapes))

    def test_split(self):
        chunks = [((0, 3), None, 'aaa'), ((3, 6), None, 'bbb'),
                  ((6, 9), None, 'ccc'), ((9, 12), None, 'ddd')]
        charshapes = [(0, 'A'), (4, 'B'), (6, 'C'), (10, 'D')]
        shaped_chunks = split_and_shape(iter(chunks),
                                        make_ranged_shapes(charshapes))
        shaped_chunks = list(shaped_chunks)
        self.assertEqual([
            ((0, 3), ('A', None), 'aaa'),
            ((3, 4), ('A', None), 'b'),
            ((4, 6), ('B', None), 'bb'),
            ((6, 9), ('C', None), 'ccc'),
            ((9, 10), ('C', None), 'd'),
            ((10, 12), ('D', None), 'dd')],
            shaped_chunks)

        # split twice
        chunks = [((0, 112), None, 'x' * 112)]
        charshapes = [(0, 'a'), (3, 'b'), (5, 'c')]
        linesegs = [(0, 'A'), (51, 'B'), (103, 'C')]
        shaped = split_and_shape(iter(chunks), make_ranged_shapes(charshapes))
        shaped = list(shaped)
        self.assertEqual([((0, 3), ('a', None), 'xxx'),
                          ((3, 5), ('b', None), 'xx'),
                          ((5, 112), ('c', None), 'x' * 107)], shaped)
        lines = split_and_shape(iter(shaped), make_ranged_shapes(linesegs))
        lines = list(lines)
        self.assertEqual([
            ((0, 3), ('A', ('a', None)), 'xxx'),
            ((3, 5), ('A', ('b', None)), 'xx'),
            ((5, 51), ('A', ('c', None)), 'x' * (51 - 5)),
            ((51, 103), ('B', ('c', None)), 'x' * (103 - 51)),
            ((103, 112), ('C', ('c', None)), 'x' * (112 - 103))], lines)


class TestLineSeg(TestCase):
    def test_line_segmented(self):
        chunks = [((0, 3), None, 'aaa'), ((3, 6), None, 'bbb'),
                  ((6, 9), None, 'ccc'), ((9, 12), None, 'ddd')]
        linesegs = [(0, 'A'), (4, 'B'), (6, 'C'), (10, 'D')]
        lines = line_segmented(iter(chunks), make_ranged_shapes(linesegs))
        lines = list(lines)
        self.assertEqual([('A', [((0, 3), None, 'aaa'),
                                 ((3, 4), None, 'b')]),
                          ('B', [((4, 6), None, 'bb')]),
                          ('C', [((6, 9), None, 'ccc'),
                                 ((9, 10), None, 'd')]),
                          ('D', [((10, 12), None, 'dd')])], lines)


class TestDistributionBodyText(TestBase):

    hwp5file_name = 'viewtext.hwp'

    def test_issue33_missing_paralineseg(self):
        section0 = self.hwp5file_bin.bodytext.section(0)
        tagids = set(model['tagid'] for model in section0.models())
        types = set(model['type'] for model in section0.models())
        self.assertTrue(HWPTAG_PARA_LINE_SEG not in tagids)
        self.assertTrue(ParaLineSeg not in types)

        paratext = self.hwp5file_bin.bodytext.section(0).model(1)
        self.assertEqual(ParaText, paratext['type'])

        paracharshape = self.bodytext.section(0).model(2)
        self.assertEqual(ParaCharShape, paracharshape['type'])

        evs = merge_paragraph_text_charshape_lineseg(
            (paratext['type'], paratext['content'], dict()),
            (paracharshape['type'], paracharshape['content'], dict()),
            None
        )

        # we can merge events without a problem
        list(evs)


class TestMatchFieldStartEnd(TestCase):

    def test_match_field_start_end(self):

        records = \
            [{'level': 2,
              'payload': b'\x1c\x00\x00\x00\x18\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x80',  # noqa
              'seqno': 196,
              'size': 22,
              'tagid': 66,
              'tagname': 'HWPTAG_PARA_HEADER'},
             {'level': 3,
              'payload': b'\x04\x00umf\x08\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x03\x00umf%\x00\x00\x00\x00\x00\x00\x00\x00\x03\x002\x009\x009\x00\x04\x00umf\x08\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\r\x00',  # noqa
              'seqno': 197,
              'size': 56,
              'tagid': 67,
              'tagname': 'HWPTAG_PARA_TEXT'},
             {'level': 3,
              'payload': b'\x00\x00\x00\x00\x13\x00\x00\x00',
              'seqno': 198,
              'size': 8,
              'tagid': 68,
              'tagname': b'HWPTAG_PARA_CHAR_SHAPE'},
             {'level': 3,
              'payload': b'\x00\x00\x00\x00\x00\x00\x00\x00\x14\x05\x00\x00\x14\x05\x00\x00Q\x04\x00\x00\xfc\xfe\xff\xff\x00\x00\x00\x00X\x0b\x00\x00\x00\x00\x06\x00',  # noqa
              'seqno': 199,
              'size': 36,
              'tagid': 69,
              'tagname': 'HWPTAG_PARA_LINE_SEG'},
             {'level': 3,
              'payload': b'umf%\x00\x00\x00\x00\x08\x15\x00=\x00S\x00U\x00M\x00(\x00R\x00I\x00G\x00H\x00T\x00)\x00?\x00?\x00%\x00g\x00,\x00;\x00;\x002\x009\x009\x00P\x89\xa0z\x00\x00\x00\x00',  # noqa
              'seqno': 200,
              'size': 61,
              'tagid': 71,
              'tagname': 'HWPTAG_CTRL_HEADER'}]

        models = binmodel.parse_models(dict(), records)
        events = xmlmodel.prefix_binmodels_with_event(dict(), models)
        events = xmlmodel.make_texts_linesegmented_and_charshaped(events)
        events = xmlmodel.make_extended_controls_inline(events)
        events = xmlmodel.match_field_start_end(events)
        events = list(events)

    def test_issue144_fields_crossing_lineseg_boundary(self):

        name = 'issue144-fields-crossing-lineseg-boundary.hwp'
        path = get_fixture_path(name)
        olestorage_opener = createOleStorageOpener(None)
        olestorage = olestorage_opener.open_storage(path)
        hwp5file = xmlmodel.Hwp5File(olestorage)
        xmlevents = hwp5file.bodytext.xmlevents()
        # pprint(list(enumerate(xmlevents)))

        stack_fields = []
        for ev, model in xmlevents:

            if ev is treeop.STARTEVENT:
                tag = model[0]
            else:
                tag = model

            if tag.startswith('Field'):
                if ev is treeop.STARTEVENT:
                    stack_fields.append(model)
                else:
                    stack_fields.pop()
            elif tag == 'LineSeg':
                # NO CROSSING
                if ev is treeop.STARTEVENT:
                    assert len(stack_fields) == 0
                else:
                    assert len(stack_fields) == 0


class TestEmbedBinData(TestBase):

    def test_embed_bindata(self):

        bindata = dict(flags=BinData.Flags(BinData.StorageType.EMBEDDING),
                       bindata=dict(storage_id=2, ext='jpg'))
        events = [(STARTEVENT, (BinData, bindata, dict())),
                  (ENDEVENT, (BinData, bindata, dict()))]
        events = list(embed_bindata(events, self.hwp5file_bin['BinData']))
        self.assertTrue('<text>' in bindata['bindata'])
