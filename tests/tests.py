# -*- coding: utf-8 -*-
import unittest
import hwp50
import hwp50html
import dataio

import StringIO
try:
    import xml.etree.ElementTree as ET
except ImportError:
    import elementtree.ElementTree as ET

if getattr(unittest.TestCase, 'assertTrue', None) is None:
    unittest.TestCase.assertTrue = unittest.TestCase.failUnless

class HelloTestCase(unittest.TestCase):
    sample = hwp50.Document('samples/sample-5017.hwp')
    def testFindControlChar(self):
        data = '\x02\x00dces01234567\x02\x00\x02\x00dloc01234567\x02\x00ABC\r'
        pos, pos_end = self.sample.ControlChar.find(data, 0)
        self.assertEquals(pos, 0)
        self.assertEquals(pos_end, 16)

    def testDatatypes(self):
        import struct
        self.assertEquals( dataio.UINT32.decode( StringIO.StringIO(struct.pack('<I', 1)) ), 1)
        self.assertEquals( dataio.INT32.decode( StringIO.StringIO('\xff\xff\xff\xff') ), -1)
        self.assertEquals( dataio.DOUBLE.decode(StringIO.StringIO('\x00\x00\x00\x00\x00\x00\xf0\x3f')), 1.0)

        print hwp50html.CssDecls.parse('color: black; border:1px solid black;; margin:1em;')

class Sample5017TestCase(unittest.TestCase):
    sample = hwp50.Document('samples/sample-5017.hwp')
    def testVersion(self):
        self.assertEquals((5, 0, 1, 7), self.sample.header.version)

    def testHello(self):
        f = self.sample.streams.docinfo
        tagid, level, size = hwp50.decode_rechdr(f)
        self.assertEquals(tagid, hwp50.HWPTAG_DOCUMENT_PROPERTIES)
        rec_type = self.sample.record_types[tagid]
        self.assertTrue(rec_type is not None)

    def testGetRecord(self):
        f = self.sample.streams.docinfo
        rec = hwp50.Record.decode(f)
        self.assertTrue(rec is not None)
        self.assertEquals(rec.tagid, 16)
        self.assertEquals(rec.size, 26)
        #self.assertEquals(rec.data.sectionCount, 1)

        #print str(f.tell()) + '/' + str(len(docinfo))

    def testDocInfoStream(self):
        f = self.sample.streams.docinfo
        i = 0
        while True:
            offset = f.tell()
            rechdr = hwp50.decode_rechdr(f)
            if rechdr is None:
                break
            tagid, level, size = rechdr

            record_type = self.sample.record_types.get(tagid)

            #print '5017 %2d'%i, '%8d'%offset, record_type, rechdr

            data = dataio.readn(f, size)

            if record_type is not None:
                try:
                    data = dataio.decodeModel(record_type, StringIO.StringIO(data))
                except dataio.Eof:
                    print 'EOF: read record data fail(%d %d %d)'%rechdr
                    data = dataio.hexdump(data)
                    #print data
            else:
                data = dataio.hexdump(data)

            i = i + 1

        f.seek(0)
        for rec in hwp50.getRecords(f):
            record_type = self.sample.record_types.get(rec.tagid)
            if record_type is None:
                #print '\t'*rec.level, rec.rechdr
                pass
            else:
                #print '\t'*rec.level, rec.tagid, record_type, rec.size
                #if issubclass(record_type, self.sample.BlobRecord):
                #    print '\t'*(rec.level+1) + str(record_type.decode(rec.datastream)).replace('\n', '\n'+'\t'*(rec.level+1), rec.size)
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
            records.append(rec)
        self.assertEquals( records[0].tagid, hwp50.HWPTAG_PARA_HEADER )
        self.assertEquals( records[1].tagid, hwp50.HWPTAG_PARA_TEXT )

        f.seek(0)
        for rec in hwp50.getRecords(f):
            record_type = self.sample.record_types.get(rec.tagid)
            if record_type is None:
                #print '\t'*rec.level, rec.rechdr
                pass
            else:
                #print '\t'*rec.level, record_type, rec.size
                data = dataio.decodeModel(record_type, rec.datastream)
                #print '\t'*(rec.level+1) + str(data).replace('\n', '\n'+'\t'*(rec.level+1))
                pass

        f.seek(0)
        sect = self.sample.Section()
        hwp50.buildModelTree(sect, hwp50.getRecords(f))

    def testSectionZ(self):
        get_section = lambda x: self.sample.sections[x]

        section = get_section(0)
        self.assertTrue(section.sectionDef is not None)
        self.assertTrue(section.columnsDef is not None)
        paragraphs = section.pages[0].paragraphs

        shapedTexts = paragraphs[0].shapedTexts
        self.assertTrue( isinstance(shapedTexts[0].elements[0].control, self.sample.SectionDef) )
        self.assertTrue( isinstance(shapedTexts[0].elements[1].control, self.sample.ColumnsDef) )
        del shapedTexts[0].elements[1]
        del shapedTexts[0].elements[0]
        self.assertTrue( shapedTexts[0].characterShape is not None )
        self.assertEquals( shapedTexts[0].elements[0], u'한글 ' )
        self.assertEquals( shapedTexts[1].elements[0], u'2005' )
        self.assertEquals( shapedTexts[2].elements[0], u' ')
        self.assertEquals( shapedTexts[3].elements[0], u'예제' )
        self.assertEquals( shapedTexts[4].elements[0], u' 파일입니다.' )

        self.assertEquals( paragraphs[0].style.localName, u'바탕글' )

        self.assertEquals( paragraphs[4].style.characterShapeId, 1)

        shapedTexts = [t for t in paragraphs[5].shapedTexts]
        self.assertEquals( shapedTexts[0].characterShapeId, 1 )
        self.assertEquals( shapedTexts[1].characterShapeId, 5 )
        self.assertEquals( shapedTexts[0].elements[0], u'표' )
        self.assertTrue( isinstance(shapedTexts[0].elements[1], self.sample.ControlChar ) )
        self.assertTrue( isinstance(shapedTexts[0].elements[1].control, self.sample.Table) )
        self.assertEquals( shapedTexts[0].elements[1].control.body.nRows, 2)
        self.assertEquals( shapedTexts[0].elements[1].control.body.nCols, 2)
        self.assertEquals( shapedTexts[0].elements[2], u'표' )
        self.assertEquals( shapedTexts[1].elements[0], u'끝' )
        self.assertTrue( isinstance(shapedTexts[1].elements[1], self.sample.ControlChar ) )
        self.assertTrue( isinstance(shapedTexts[1].elements[1].control, self.sample.Table) )
        self.assertEquals( shapedTexts[1].elements[1].control.body.nRows, 1)
        self.assertEquals( shapedTexts[1].elements[1].control.body.nCols, 1)
        def try_get_paragraph_break():
            return shapedTexts[1].elements[2]
        self.assertRaises(IndexError, try_get_paragraph_break)

        self.assertEquals( paragraphs[5].shapedTexts[0].characterShapeId, 1)
        self.assertEquals( paragraphs[5].shapedTexts[0].elements[0], u'표')
        self.assertEquals( paragraphs[5].shapedTexts[0].elements[1].control.chid, 'tbl ')
        self.assertEquals( paragraphs[5].shapedTexts[0].elements[2], u'표')
        self.assertEquals( paragraphs[5].shapedTexts[1].characterShapeId, 5)
        self.assertEquals( paragraphs[5].shapedTexts[1].elements[0], u'끝')
        self.assertEquals( paragraphs[5].shapedTexts[1].elements[1].control.chid, 'tbl ')

        self.assertEquals( paragraphs[5].controls['tbl '][0].body.cells[0].paragraphs[0].style.localName, u'바탕글' )

        self.assertEquals( paragraphs[7].shapedTexts[0].elements[0], u'다음 문단')
        # paragraphs[8]
        #paragraphs[9]
        self.assertEquals( paragraphs[10].shapedTexts[0].characterShapeId, 1)
        self.assertEquals( paragraphs[10].shapedTexts[0].elements[0].chid, 'gso ')

        self.assertRaises(IndexError, get_section, (1))

    def testMakeHTML(self):
        import hwp50html, sys
        cvt = hwp50html.HtmlConverter()
        tree = cvt.makeTree(self.sample)
        body = tree.find('body')
        sectdiv = body[0]
        pagediv = sectdiv[0]
        div = pagediv
        self.assertEquals(div[0].get('class'), 'Normal ParaShape-0')
        self.assertEquals(div[1].get('class'), 'Normal ParaShape-0')
        self.assertEquals(div[2].get('class'), 'Header ParaShape-11')
        self.assertEquals(div[3].get('class'), 'Normal ParaShape-0')
        self.assertEquals(div[4].get('class'), 'Body')
        self.assertEquals(div[5].get('class'), 'Body')

        def childElems(seq):
            return filter(lambda x: x.tag != ET.Comment, seq)
        self.assertEquals( [str(x.tag) for x in childElems(div[5])], ['span', 'table', 'span', 'span', 'table', 'span'] )

        self.assertEquals(div[6].tag, 'div')
        div6 = childElems(div[6])
        self.assertEquals(div6[0].tag, 'span')
        self.assertEquals(div6[1].tag, 'table')
        self.assertEquals(div6[1][0].tag, 'caption')
        self.assertEquals(div6[1][0][0].tag, 'div')
        #print div6[1][0][0][0].text
        #self.assertEquals(div6[1][0][0][0].text, u'2x2짜리표')
        self.assertEquals(div6[1][0][1].tag, 'div')
        self.assertEquals(div6[1][0][1][0].text, u'가나다')
        self.assertEquals(div6[2].tag, 'span')

        f = self.sample.streams.section[0]
        root = ET.Element('section')
        doc = ET.ElementTree(root)
        for evt, (tagid, data) in hwp50.pullparse( f ):
            if evt == hwp50.STARTREC:
                e = ET.SubElement(root, str(self.sample.record_types.get(tagid)).split('.')[-1])
                e.text = dataio.hexdump(data)
                e._parent = root
                root = e
            if evt == hwp50.ENDREC:
                root = root._parent

    def testGSO(self):
        bindatas = self.sample.docinfo.mappings[self.sample.BinData]
        self.assertEquals( bindatas[0].name, 'BIN0001.jpg')
        self.assertTrue( bindatas[0].datastream.read is not None)
        self.assertTrue( self.sample.streams.bindata['BIN0001.jpg'].read is not None)
        self.assertEquals( len(bindatas[0].datastream.read()), 15895)

        gso = self.sample.sections[0].pages[0].paragraphs[-3].controls['gso '][0]
        picinfo = gso.shapecomponent.shape.pictureInfo
        self.assertEquals(picinfo.binData.name, 'BIN0001.jpg')

    def testZZZ(self):
        import os.path
        testfiles = [ line.replace('\n', '') for line in file('testfiles', 'r') ]
        try:
            testfiles += [ line.replace('\n', '') for line in file('testfiles.local', 'r') ]
        except IOError:
            pass
        for fn in testfiles:
            if fn[0] == '#':
                continue
            cvt = hwp50html.HtmlConverter()
            try:
                doc = hwp50.Document(fn)
                print doc.header.version, fn
                rootname = os.path.splitext(os.path.basename(fn))[0]
                cvt.convert(doc, hwp50html.LocalDestination(os.path.join('gen', rootname)))
            except IOError, e:
                print fn, e

if __name__=='__main__':
    unittest.main()
