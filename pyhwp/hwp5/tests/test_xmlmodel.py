# -*- coding: utf-8 -*-
from unittest import TestCase
from hwp5.tests import test_binmodel
from hwp5.utils import cached_property


class TestBase(test_binmodel.TestBase):

    @cached_property
    def hwp5file_xml(self):
        from hwp5.xmlmodel import Hwp5File
        return Hwp5File(self.olestg)

    hwp5file = hwp5file_xml


class TestModelEventStream(TestBase):

    @cached_property
    def docinfo(self):
        from hwp5.xmlmodel import ModelEventStream
        return ModelEventStream(self.hwp5file_bin['DocInfo'],
                                self.hwp5file_bin.header.version)

    def test_modelevents(self):
        self.assertEquals(len(list(self.docinfo.models())) * 2,
                          len(list(self.docinfo.modelevents())))
        #print len(list(self.docinfo.modelevents()))


class TestDocInfo(TestBase):

    @cached_property
    def docinfo(self):
        from hwp5.xmlmodel import DocInfo
        return DocInfo(self.hwp5file_bin['DocInfo'],
                       self.hwp5file_bin.header.version)

    def test_events(self):
        events = list(self.docinfo.events())
        self.assertEquals(112, len(events))
        #print len(events)

        # without embedbin, no <text> is embedded
        self.assertTrue('<text>' not in events[4][1][1]['bindata'])

    def test_events_with_embedbin(self):
        import base64
        bindata = self.hwp5file_bin['BinData']
        events = list(self.docinfo.events(embedbin=bindata))
        self.assertTrue('<text>' in events[4][1][1]['bindata'])
        self.assertEquals(bindata['BIN0002.jpg'].open().read(),
                          base64.b64decode(events[4][1][1]['bindata']['<text>']))


class TestSection(TestBase):

    def test_events(self):
        from hwp5.xmlmodel import Section
        from hwp5.treeop import STARTEVENT, ENDEVENT
        from hwp5.binmodel import SectionDef, PageDef
        section = Section(self.hwp5file_bin['BodyText']['Section0'],
                          self.hwp5file_bin.fileheader.version)
        events = list(section.events())
        ev, (tag, attrs, ctx) = events[0]
        self.assertEquals((STARTEVENT, SectionDef), (ev, tag))
        self.assertFalse('section-id' in attrs)

        ev, (tag, attrs, ctx) = events[1]
        self.assertEquals((STARTEVENT, PageDef), (ev, tag))

        ev, (tag, attrs, ctx) = events[2]
        self.assertEquals((ENDEVENT, PageDef), (ev, tag))

        ev, (tag, attrs, ctx) = events[-1]
        self.assertEquals((ENDEVENT, SectionDef), (ev, tag))


class TestHwp5File(TestBase):

    def test_docinfo_class(self):
        from hwp5.xmlmodel import DocInfo
        self.assertTrue(isinstance(self.hwp5file.docinfo, DocInfo))

    def test_events(self):
        list(self.hwp5file.events())

    def test_events_embedbin_without_bindata(self):
        # see issue 76: https://github.com/mete0r/pyhwp/issues/76
        self.hwp5file_name = 'parashape.hwp' # an hwp5file without BinData
        hwp5file = self.hwp5file
        self.assertTrue('BinData' not in hwp5file)
        list(hwp5file.events(embedbin=True))

    def test_xmlevents_dump(self):
        from hwp5.externprogs import xmllint
        xmllint = xmllint('--format')

        outfile = file(self.id() + '.xml', 'w')
        try:
            out = xmllint(outfile=outfile)
            try:
                self.hwp5file.xmlevents().dump(out)
            finally:
                out.close()
        finally:
            outfile.close()


from hwp5.xmlmodel import make_ranged_shapes, split_and_shape


class TestShapedText(TestCase):
    def test_make_shape_range(self):
        charshapes = [(0, 'A'), (4, 'B'), (6, 'C'), (10, 'D')]
        ranged_shapes = make_ranged_shapes(charshapes)
        self.assertEquals([((0, 4), 'A'), ((4, 6), 'B'), ((6, 10), 'C'),
                           ((10, 0x7fffffff), 'D')], list(ranged_shapes))

    def test_split(self):
        chunks = [((0, 3), None, 'aaa'), ((3, 6), None, 'bbb'),
                  ((6, 9), None, 'ccc'), ((9, 12), None, 'ddd')]
        charshapes = [(0, 'A'), (4, 'B'), (6, 'C'), (10, 'D')]
        shaped_chunks = split_and_shape(iter(chunks),
                                        make_ranged_shapes(charshapes))
        shaped_chunks = list(shaped_chunks)
        self.assertEquals([
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
        self.assertEquals([((0, 3), ('a', None), 'xxx'),
                           ((3, 5), ('b', None), 'xx'),
                           ((5, 112), ('c', None), 'x' * 107)], shaped)
        lines = split_and_shape(iter(shaped), make_ranged_shapes(linesegs))
        lines = list(lines)
        self.assertEquals([
            ((0, 3), ('A', ('a', None)), 'xxx'),
            ((3, 5), ('A', ('b', None)), 'xx'),
            ((5, 51), ('A', ('c', None)), 'x' * (51 - 5)),
            ((51, 103), ('B', ('c', None)), 'x' * (103 - 51)),
            ((103, 112), ('C', ('c', None)), 'x' * (112 - 103))], lines)


class TestLineSeg(TestCase):
    def test_line_segmented(self):
        from hwp5.xmlmodel import line_segmented
        chunks = [((0, 3), None, 'aaa'), ((3, 6), None, 'bbb'),
                  ((6, 9), None, 'ccc'), ((9, 12), None, 'ddd')]
        linesegs = [(0, 'A'), (4, 'B'), (6, 'C'), (10, 'D')]
        lines = line_segmented(iter(chunks), make_ranged_shapes(linesegs))
        lines = list(lines)
        self.assertEquals([('A', [((0, 3), None, 'aaa'), ((3, 4), None, 'b')]),
                           ('B', [((4, 6), None, 'bb')]),
                           ('C', [((6, 9), None, 'ccc'), ((9, 10), None, 'd')]),
                           ('D', [((10, 12), None, 'dd')])], lines)


class TestDistributionBodyText(TestBase):

    hwp5file_name = 'viewtext.hwp'

    def test_issue33_missing_paralineseg(self):
        from hwp5.tagids import HWPTAG_PARA_LINE_SEG
        from hwp5.binmodel import ParaLineSeg
        section0 = self.hwp5file_bin.bodytext.section(0)
        tagids = set(model['tagid'] for model in section0.models())
        types = set(model['type'] for model in section0.models())
        self.assertTrue(HWPTAG_PARA_LINE_SEG not in tagids)
        self.assertTrue(ParaLineSeg not in types)

        from hwp5.binmodel import ParaText, ParaCharShape
        paratext = self.hwp5file_bin.bodytext.section(0).model(1)
        self.assertEquals(ParaText, paratext['type'])

        paracharshape = self.bodytext.section(0).model(2)
        self.assertEquals(ParaCharShape, paracharshape['type'])

        from hwp5.xmlmodel import merge_paragraph_text_charshape_lineseg as m
        evs = m((paratext['type'], paratext['content'], dict()),
                (paracharshape['type'], paracharshape['content'], dict()),
                None)

        # we can merge events without a problem
        list(evs)


class TestMatchFieldStartEnd(TestCase):

    def test_match_field_start_end(self):
        from hwp5 import binmodel, xmlmodel

        import pickle
        f = open('fixtures/match-field-start-end.dat', 'r')
        try:
            records = pickle.load(f)
        finally:
            f.close()

        models = binmodel.parse_models(dict(), records)
        events = xmlmodel.prefix_binmodels_with_event(dict(), models)
        events = xmlmodel.make_texts_linesegmented_and_charshaped(events)
        events = xmlmodel.make_extended_controls_inline(events)
        events = xmlmodel.match_field_start_end(events)
        events = list(events)


class TestEmbedBinData(TestBase):

    def test_embed_bindata(self):
        from hwp5.treeop import STARTEVENT, ENDEVENT
        from hwp5.binmodel import BinData
        from hwp5.xmlmodel import embed_bindata

        bindata = dict(flags=BinData.Flags(BinData.StorageType.EMBEDDING),
                       bindata=dict(storage_id=2, ext='jpg'))
        events = [(STARTEVENT, (BinData, bindata, dict())),
                  (ENDEVENT, (BinData, bindata, dict()))]
        events = list(embed_bindata(events, self.hwp5file_bin['BinData']))
        self.assertTrue('<text>' in bindata['bindata'])
