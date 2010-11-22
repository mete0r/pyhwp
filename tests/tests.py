# -*- coding: utf-8 -*-
import unittest
from hwp import hwp50
from hwp import hwp50html
from hwp import dataio

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    import xml.etree.ElementTree as ET
except ImportError:
    import elementtree.ElementTree as ET

class HelloTestCase(unittest.TestCase):
    sample = hwp50.Document('samples/sample-5017.hwp')
    def testFindControlChar(self):
        data = '\x02\x00dces01234567\x02\x00\x02\x00dloc01234567\x02\x00ABC\r'
        pos, pos_end = self.sample.ControlChar.find(data, 0)
        self.assertEquals(pos, 0)
        self.assertEquals(pos_end, 16)

    def testDatatypes(self):
        import struct
        self.assertEquals( dataio.UINT32.parse( StringIO(struct.pack('<I', 1)) ), 1)
        self.assertEquals( dataio.INT32.parse( StringIO('\xff\xff\xff\xff') ), -1)
        self.assertEquals( dataio.DOUBLE.parse(StringIO('\x00\x00\x00\x00\x00\x00\xf0\x3f')), 1.0)

    def testControlChar(self):
        ControlChar = self.sample.ControlChar
        self.assertEquals(ControlChar.char, ControlChar.kinds[u'\x00'])

class ParagraphTest(unittest.TestCase):
    sample = hwp50.Document('samples/sample-5017.hwp')
    def testGetElementsWithControl(self):
        doc = self.sample
        paragraph = doc.sections[0].records[0].model
        x = [getattr(x, 'control', None).__class__ for x in paragraph.getElementsWithControl()]
        self.assertEquals([doc.SectionDef, doc.ColumnsDef, type(None), type(None)], x)

    def testGetSegmentedElements(self):
        doc = self.sample
        paraTextRec = doc.sections[0].records[1]
        self.assertEquals(hwp50.HWPTAG_PARA_TEXT, paraTextRec.tagid)

        paraText = doc.ParaText()
        paraText.record = paraTextRec

        charShapeRec = doc.sections[0].records[2]
        self.assertEquals(hwp50.HWPTAG_PARA_CHAR_SHAPE, charShapeRec.tagid)
        charShapes = doc.ParaCharShape()
        charShapes.parse(charShapeRec.bytestream())

        paragraph = doc.Paragraph()
        paragraph.textdata = paraText
        paragraph.charShapes = charShapes
        shapes = paragraph.getCharShapeSegments

        elemtypes = [doc.ControlChar, doc.ControlChar, doc.Text, doc.Text, doc.Text, doc.Text, doc.Text, doc.ControlChar]
        shapeids = [1, 1, 1, 5, 1, 6, 1, 1]
        self.assertEquals(elemtypes, [elem.__class__ for elem, shapeid in paragraph.getSegmentedElements(paraText.getElements(), shapes())])
        self.assertEquals(shapeids, [shapeid for elem, shapeid in paragraph.getSegmentedElements(paraText.getElements(), shapes())])
        self.assertEquals(zip(elemtypes, shapeids), [(elem.__class__, shapeid) for elem, shapeid in paragraph.getSegmentedElements(paraText.getElements(), shapes())])

    def testGetShapedElements(self):
        doc = self.sample
        paraTextRec = doc.sections[0].records[1]
        self.assertEquals(hwp50.HWPTAG_PARA_TEXT, paraTextRec.tagid)

        paraText = doc.ParaText()
        paraText.record = paraTextRec

        charShapeRec = doc.sections[0].records[2]
        self.assertEquals(hwp50.HWPTAG_PARA_CHAR_SHAPE, charShapeRec.tagid)
        charShapes = doc.ParaCharShape()
        charShapes.parse(charShapeRec.bytestream())

        paragraph = doc.Paragraph()
        paragraph.textdata = paraText
        paragraph.charShapes = charShapes

        elemtypes = [doc.ControlChar, doc.ControlChar, doc.Text, doc.Text, doc.Text, doc.Text, doc.Text]
        shapeids = [1, 1, 1, 5, 1, 6, 1]
        self.assertEquals(elemtypes, [elem.__class__ for elem in paragraph.getShapedElements()])
        self.assertEquals(shapeids, [elem.charShapeId for elem in paragraph.getShapedElements()])
        self.assertEquals(zip(elemtypes, shapeids), [(elem.__class__, elem.charShapeId) for elem in paragraph.getShapedElements()])

    def testGetLineSegments(self):
        doc = self.sample

        recParagraph = doc.sections[0].records[22]
        self.assertEquals(hwp50.HWPTAG_PARA_HEADER, recParagraph.tagid)
        paragraph = doc.Paragraph.parse(recParagraph.bytestream())

        recParaText = doc.sections[0].records[23]
        self.assertEquals(hwp50.HWPTAG_PARA_TEXT, recParaText.tagid)
        paragraph.addsubrec(recParaText)

        recLineSeg = doc.sections[0].records[25]
        self.assertEquals(hwp50.HWPTAG_PARA_LINE_SEG, recLineSeg.tagid)
        paragraph.addsubrec(recLineSeg)

        #print [x for x in paragraph.getLineSegments()]
        self.assertEquals([(0, 51), (51, 103), (103, 112)],
                [(start, end) for start, end, lineSeg in paragraph.getLineSegments()])

    def test_getLines(self):
        doc = hwp50.Document('samples.local/long-table.hwp')
        section = doc.sections[0]
        table = section.records[12].model
        paragraph = hwp50.nth(table.getCell(0, 0).paragraphs, 0)

        for line, elems in paragraph.getLines():
            pass#print line.offsetY, [elem for elem in elems]
        self.assertEquals([[u'a'], [u'b'], [u'c']], [ [unicode(elem) for elem in elems] for line, elems in paragraph.getLines()] )

    def test_getPagedLines(self):
        doc = hwp50.Document('samples.local/long-table.hwp')
        section = doc.sections[0]
        table = section.records[12].model
        paragraph = hwp50.nth(table.getCell(0, 0).paragraphs, 0)

        paged_lines = [(page, line, line_elements) for page, line, line_elements in paragraph.getPagedLines()]
        for page, line, line_elements in paged_lines:
            pass#print page, line.offsetY, ' '.join([unicode(elem) for elem in line_elements])
        self.assertEquals([(0, [u'a']), (0, [u'b']), (1, [u'c'])], [(page, [unicode(elem) for elem in line_elements]) for page, line, line_elements in paragraph.getPagedLines()])

    def test_getPages(self):
        doc = hwp50.Document('samples.local/long-table.hwp')
        section = doc.sections[0]
        table = section.records[12].model
        paragraph = hwp50.nth(table.getCell(0, 0).paragraphs, 0)

        for (page, page_lines) in paragraph.getPages(0, None):
            pass#print 'PAGE %d'%page
            for line, line_elements in page_lines:
                pass#print [elem for elem in line_elements]
        self.assertEquals([(0, [u'a', u'b']), (1, [u'c'])],
                [(page, [u''.join([unicode(elem) for elem in line_elements]) for line, line_elements in page_lines]) for page, page_lines in paragraph.getPages(0, None)])

    def test_getPagedParagraphs(self):
        sample = hwp50.Document('samples/sample-5003.hwp')
        section = sample.sections[0]
        pass#print ''
        for page, paragraphs in enumerate(hwp50.getPagedParagraphs(section.paragraphs)):
            pass#print '-- page %d '%page+'-'*40
            for (paragraph, paragraph_lines) in paragraphs:
                pass#print 'paragraph #%d'%(paragraph.record.seqno)
                for (line, line_elements) in paragraph_lines:
                    pass#print '% 8d'%line.offsetY, u''.join([unicode(elem) for elem in line_elements])

#        for page, paragraph, line, line_elements in hwp50.getPagedParagraphs(section.paragraphs):
#            print 'page %02d, #%d %08d %s'%(page, paragraph.record.seqno, line.offsetY, 
#                u''.join([unicode(elem) for elem in line_elements]))

class TableTest(unittest.TestCase):
    sample = hwp50.Document('samples/sample-5017.hwp')
    def testGetRows(self):
        section = self.sample.sections[0]
        table = section.records[30].model
        rows = [(row, cells) for row, cells in table.getRows()]
        self.assertEquals(2, len(rows))
        self.assertEquals([2, 2], [len([cell for cell in cells]) for (row, cells) in table.getRows()])

    def testHello(self):
        doc = hwp50.Document('samples.local/long-table.hwp')
        section = doc.sections[0]
        table = section.records[12].model
        self.assertEquals([1, 2, 3, 2, 3, 0, 1, 2, 3],
                [ev for ev, param in hwp50.getElementEvents(table.getCell(0,0).paragraphs)])

    def testLongCell(self):
        doc = hwp50.Document('samples.local/long-table-AB.hwp')
        section = doc.sections[0]
        table = section.records[12].model
        for paragraphs in table.body.cells[0].getPages():
            for paragraph, paragraph_lines in paragraphs:
                pass#print paragraph_lines
                for line, line_elements in paragraph_lines:
                    pass#print '% 8d'%line.offsetY, u''.join([unicode(elem) for elem in line_elements])

class SectionTest(unittest.TestCase):
    sample = hwp50.Document('samples/sample-5003.hwp')
    def test_merge_iterators(self):
        a = [1]
        b = ['a', 'b']
        c = []
        self.assertEquals([(1, 'a', None), (None, 'b', None)],
                [x for x in hwp50.merge_iterators(iter(a), iter(b), iter(c))])
    def testGetPagedLines(self):
        doc = hwp50.Document('samples/sample-5017.hwp')
        section = doc.sections[0]
        paged_elements = [x for x in hwp50.getPagedLines(section.paragraphs)]
        self.assertTrue(all([page==0 for (page, paragraph, line, line_elements) in paged_elements[0:-1]]))
        self.assertTrue(all([page==1 for (page, paragraph, line, line_elements) in paged_elements[-1:]]))
    def testGroupByPage(self):
        doc = hwp50.Document('samples/sample-5017.hwp')
        section = doc.sections[0]
        for page_paragraphs in hwp50.groupByPage(hwp50.getPagedLines(section.paragraphs)):
            pass#print '---- Page '+'-'*40
            for paragraph, paragraph_lines in page_paragraphs:
                pass#print '#%d'%paragraph.record.seqno
                for (line, line_elements) in paragraph_lines:
                    pass#print line.offsetY, [unicode(elem) for elem in line_elements]
                pass#print ''
        self.assertEquals(
                [
                    [
                        (0, []),
                        (15, []),
                        (22, []),
                        (26, []),
                        (63, []),
                        (95, []),
                        (102, []),
                        (106, []),
                        (113, []),
                        (117, []),
                    ],
                    [   (121, []) ]
                ], 
                [
                    [
                        (paragraph.record.seqno, []) for paragraph, paragraph_lines in page_paragraphs
                    ] for page_paragraphs in hwp50.groupByPage(hwp50.getPagedLines(section.paragraphs))
                ])
        
    def testGetElementEvents(self):
        doc = hwp50.Document('samples/sample-5017.hwp')
        section = doc.sections[0]
        expected = [1, 2, 1, 1, 2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1, 2, 1, 2, 1, 1, 2, 2, 2, 1, 2, 1, 2, 1, 2, 0, 1, 2,]
        events = filter(lambda x: x != hwp50.EV_ELEMENT, [ev for ev, param in hwp50.getElementEvents(section.paragraphs)])
        self.assertEquals(expected, events)

    def testGetPages(self):
        class PageFactory:
            class Page(list):
                class Paragraph(list):
                    def __init__(self, model):
                        self.model = model
                    class Line(list):
                        def __init__(self, model):
                            pass
                        class Element:
                            def __init__(self, model):
                                self.model = model
        doc = hwp50.Document('samples/sample-5017.hwp')
        pages = [page for page in doc.sections[0].getPages(PageFactory)]
        expected_paragraphs_by_page = [
                [ 0, 12, 15, 19, 22, 26, 63, 95, 99, 102, 106, 113, 117 ], 
                [ 121 ],
        ]

        self.assertEquals(expected_paragraphs_by_page,
                [[paragraph.model.record.seqno for paragraph in page] for page in pages])

        for page in pages:
            for paragraph in page:
                for line in paragraph:
                    pass#print ' '.join([unicode(elem.model) for elem in line])
                pass#print ''
            pass#print '----'

class ParaTextTest(unittest.TestCase):
    sample = hwp50.Document('samples/sample-5017.hwp')
    def testGetElements(self):
        doc = self.sample
        paraTextRec = doc.sections[0].records[1]
        self.assertEquals(hwp50.HWPTAG_PARA_TEXT, paraTextRec.tagid)

        paraText = doc.ParaText()
        paraText.record = paraTextRec
        elemtypes = [doc.ControlChar, doc.ControlChar, doc.Text, doc.ControlChar]
        self.assertEquals(elemtypes, [elem.__class__ for elem in paraText.getElements()])

    def testApplyCharShapes(self):
        doc = self.sample
        paraTextRec = doc.sections[0].records[1]
        self.assertEquals(hwp50.HWPTAG_PARA_TEXT, paraTextRec.tagid)
        paraCharShapeRec = doc.sections[0].records[2]
        self.assertEquals(hwp50.HWPTAG_PARA_CHAR_SHAPE, paraCharShapeRec.tagid)

        paraText = doc.ParaText()
        paraText.decode(paraTextRec.bytes)
        paraCharShapes = doc.ParaCharShape()
        paraCharShapes.parse(paraCharShapeRec.bytestream())

        paraText.applyCharShapes(paraCharShapes)

        shapeids = [1, 1, 1, 5, 1, 6, 1, 1]
        self.assertEquals(shapeids, [elem.charShapeId for elem in paraText])
        elemtypes = [doc.ControlChar, doc.ControlChar, doc.Text, doc.Text, doc.Text, doc.Text, doc.Text, doc.ControlChar]
        self.assertEquals(elemtypes, [elem.__class__ for elem in paraText])
    def test_controlchars_by_chid(self):
        doc = self.sample
        paraTextRec = doc.sections[0].records[1]
        paraCharShapeRec = doc.sections[0].records[2]
        self.assertEquals(hwp50.HWPTAG_PARA_TEXT, paraTextRec.tagid)
        self.assertEquals(hwp50.HWPTAG_PARA_CHAR_SHAPE, paraCharShapeRec.tagid)

        paraText = doc.ParaText()
        paraText.decode(paraTextRec.bytes)
        paraCharShapes = doc.ParaCharShape()
        paraCharShapes.parse(paraCharShapeRec.bytestream())

        paraText.applyCharShapes(paraCharShapes)

        x = [c for c in paraText.controlchars_by_chid('secd')]
        self.assertEquals(1, len(x))

        x = [c for c in paraText.controlchars_by_chid('cold')]
        self.assertEquals(1, len(x))


class Sample5017TestCase(unittest.TestCase):
    sample = hwp50.Document('samples/sample-5017.hwp')
    def testVersion(self):
        self.assertEquals((5, 0, 1, 7), self.sample.header.version)

    def testGetRecord(self):
        f = self.sample.streams.docinfo
        rec = hwp50.decode_rechdr(f)
        self.assertTrue(rec is not None)
        (tagid, level, size) = rec
        self.assertEquals(tagid, hwp50.HWPTAG_DOCUMENT_PROPERTIES)
        self.assertEquals(size, 26)
        #self.assertEquals(rec.data.sectionCount, 1)

    def testDocInfoStream(self):
        pass
        f = self.sample.streams.docinfo

        f.seek(0)
        for rec in hwp50.getRecords(f):
            pass

    def testDocInfo(self):
        #print self.sample.docinfo.mappings
        docinfo = self.sample.docinfo
        idx = 0
        for faceName in docinfo.mappings[self.sample.FaceName]:
            #print 'FaceName %d: %s'%(faceName.id, faceName)
            self.assertEquals(idx, faceName.id)
            idx += 1
        idx = 0
        for paraShape in docinfo.mappings[self.sample.ParaShape]:
            #print 'ParaShape %d: %s'%(paraShape.id, paraShape)
            self.assertEquals(idx, paraShape.id)
            idx += 1
        idx = 0
        for charShape in docinfo.mappings[self.sample.CharShape]:
            #print 'CharShape %d: %s'%(charShape.id, charShape)
            self.assertEquals(idx, charShape.id)
            idx += 1
        idx = 0
        for borderFill in docinfo.mappings[self.sample.BorderFill]:
            self.assertEquals(idx, borderFill.id)
            #print 'BorderFill %d:\n%s'%(borderFill.id, borderFill)
            idx += 1
        for style in docinfo.mappings[self.sample.Style]:
            #print u'Style %d : %s(%s)'%(style.id, style.localName, style.name)
            #print '\tParagraph Shape: %d'%style.paragraphShapeId
            paraShape = docinfo.mappings[self.sample.ParaShape][style.paragraphShapeId]
            #print '\t', paraShape
            #print '\tBorder Fill: %d'%paraShape.borderFillId
            #borderFill = docinfo.mappings[self.sample.BorderFill][paraShape.borderFillId-1]
            #print '\t', borderFill
            #print '\tTab Def: %d'%paraShape.tabDefId
            #tabDef = docinfo.mappings[self.sample.TabDef][paraShape.tabDefId]
            #print '\t', tabDef
            #print '\tCharacter Shape: %d'%style.characterShapeId
            #print docinfo.mappings[self.sample.CharShape][style.characterShapeId]
        self.assertEquals(docinfo.mappings[self.sample.Style][0].localName, u'바탕글')

    def testSectionStream(self):
        f = self.sample.streams.section[0]
        records = []
        for rec in hwp50.getRecords(f):
            records.append(rec.tagid)
        self.assertEquals( records[0], hwp50.HWPTAG_PARA_HEADER )
        self.assertEquals( records[1], hwp50.HWPTAG_PARA_TEXT )

        f.seek(0)
        sect = self.sample.Section()
        hwp50.buildModelTree(sect, f)

    def testGSO(self):
        bindatas = self.sample.docinfo.mappings[self.sample.BinData]
        self.assertEquals( bindatas[0].name, 'BIN0003.png')
        self.assertEquals( bindatas[1].name, 'BIN0001.jpg')
        self.assertTrue( bindatas[1].datastream.read is not None)
        self.assertTrue( self.sample.streams.bindata['BIN0001.jpg'].read is not None)
        self.assertEquals( len(bindatas[1].datastream.read()), 15895)

        gso = self.sample.sections[0].paragraphs[-4].controls['gso '][0]
        picinfo = gso.shapecomponent.shape.pictureInfo
        self.assertEquals(picinfo.binData.name, 'BIN0001.jpg')

def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(HelloTestCase),
        unittest.TestLoader().loadTestsFromTestCase(ParaTextTest),
        unittest.TestLoader().loadTestsFromTestCase(ParagraphTest),
        unittest.TestLoader().loadTestsFromTestCase(TableTest),
        unittest.TestLoader().loadTestsFromTestCase(SectionTest),
        unittest.TestLoader().loadTestsFromTestCase(Sample5017TestCase),
        ])
