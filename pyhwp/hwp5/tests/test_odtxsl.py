# -*- coding: utf-8 -*-
from unittest import TestCase
from hwp5.utils import cached_property

def example(filename):
    from hwp5.xmlmodel import Hwp5File
    return Hwp5File('fixtures/'+filename)

def example_to_xml(filename):
    hwp5file = example(filename)

    xmlfilename = filename+'.xml'
    xmlfile = file(xmlfilename, 'w')
    try:
        hwp5file.xmlevents().dump(xmlfile)
        return xmlfilename
    finally:
        xmlfile.close()

class example_to_odt(object):
    def __init__(self, filename):
        self.xmlfilename = example_to_xml(filename)

    def open_content(self):
        from hwp5.hwp5odt import convert
        import os
        r, w = os.pipe()
        r = os.fdopen(r, 'r')
        w = os.fdopen(w, 'w')
        try:
            xmlfile = file(self.xmlfilename, 'r')
            try:
                convert.xslt_content(xmlfile, w)
            finally:
                xmlfile.close()
            return r
        except:
            r.close()
            raise
        finally:
            w.close()

    def content(self):
        from lxml import etree
        f = self.open_content()
        try:
            return etree.parse(f)
        finally:
            f.close()
    content = cached_property(content)

    def open_styles(self):
        from hwp5.hwp5odt import convert
        import os
        r, w = os.pipe()
        r = os.fdopen(r, 'r')
        w = os.fdopen(w, 'w')
        try:
            xmlfile = file(self.xmlfilename, 'r')
            try:
                convert.xslt_styles(xmlfile, w)
            finally:
                xmlfile.close()
            return r
        except:
            r.close()
            raise
        finally:
            w.close()

    def styles(self):
        from lxml import etree
        f = self.open_styles()
        try:
            return etree.parse(f)
        finally:
            f.close()
    styles = cached_property(styles)

    def office_style(self, style_name):
        return xpath1(self.styles,
                "//office:styles/style:style[@style:name='%s']"%style_name)

    def office_style_paragraph_properties(self, style_name):
        style = self.office_style(style_name)
        if style is not None:
            return xpath1(style, 'style:paragraph-properties')

    def office_style_text_properties(self, style_name):
        style = self.office_style(style_name)
        if style is not None:
            return xpath1(style, 'style:text-properties')

    def hwp_style(self, name):
        return (self.office_style_paragraph_properties(name),
                self.office_style_text_properties(name))

    def automatic_pagelayout_properties(self, id):
        return xpath1(self.styles,
                      "//office:automatic-styles/style:page-layout[@style:name='PageLayout-%d']/style:page-layout-properties"%id)

    def master_page(self, id):
        return xpath1(self.styles,
                      "//office:master-styles/style:master-page[@style:name='MasterPage-%d']"%id)

    def font_face(self, name):
        return xpath1(self.styles, "//office:font-face-decls/style:font-face[@style:name='%s']"%name)

    def automatic_style(self, style_name):
        return xpath1(self.content,
                "//office:automatic-styles/style:style[@style:name='%s']"%style_name)

    def automatic_style_text(self, paragraph_id, lineseg, span):
        style = self.automatic_style('p%d-%d-%d'%(paragraph_id, lineseg, span))
        if style is not None:
            assert 'text' == xpath1(style, '@style:family')
        return style

    def automatic_style_text_properties(self, paragraph_id, lineseg, span):
        style = self.automatic_style_text(paragraph_id, lineseg, span)
        if style is not None:
            return xpath1(style, 'style:text-properties')

    def automatic_style_paragraph(self, paragraph_id):
        style = self.automatic_style('Paragraph-%d'%paragraph_id)
        if style is not None:
            assert 'paragraph' == xpath1(style, '@style:family')
        return style

    def automatic_style_paragraph_properties(self, paragraph_id):
        style = self.automatic_style_paragraph(paragraph_id)
        if style is not None:
            return xpath1(style, 'style:paragraph-properties')

    def automatic_style_shaperect(self, shape_id):
        style = self.automatic_style('Shape-%d'%shape_id)
        if style is not None:
            assert 'graphic' == xpath1(style, '@style:family')
        return style

    def automatic_style_shaperect_graphic_properties(self, shape_id):
        style = self.automatic_style_shaperect(shape_id)
        if style is not None:
            return xpath1(style, 'style:graphic-properties')

class TestPrecondition(TestCase):
    def test_example(self):
        assert example('linespacing.hwp') is not None

odt_namespaces = dict(office="urn:oasis:names:tc:opendocument:xmlns:office:1.0",
                      style='urn:oasis:names:tc:opendocument:xmlns:style:1.0',
                      text="urn:oasis:names:tc:opendocument:xmlns:text:1.0",
                      table="urn:oasis:names:tc:opendocument:xmlns:table:1.0",
                      draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
                      fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
                      xlink="http://www.w3.org/1999/xlink",
                      svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0")

def xpath(root, path):
    return root.xpath(path, namespaces=odt_namespaces)

def xpath1(root, path):
    resultset = xpath(root, path)
    if len(resultset) > 0:
        return resultset[0]
    else:
        return None

class TestODTXSL(TestCase):

    def test_issue30_noindent(self):
        odt = example_to_odt('issue30.hwp')
        span = xpath1(odt.content, '//text:p/text:span')
        # 첫번째 span의 다음에 new line 문자나 공백이 있으면 안된다.
        #print len(span.tail), type(span.tail), '"', span.tail.encode('string_escape'), '"'
        assert span.tail is None

    def test_styles(self):
        ''' 스타일 '''
        odt = example_to_odt('charshape.hwp')

        paraprops, textprops = odt.hwp_style(u'바탕글')
        assert paraprops is not None
        assert textprops is not None

        paraprops, textprops = odt.hwp_style(u'본문')
        assert paraprops is not None
        assert textprops is not None
        assert '15pt' == xpath1(paraprops, '@fo:margin-left')

    def test_font_face(self):
        ''' 폰트 정의 '''
        odt = example_to_odt('charshape.hwp')

        font = odt.font_face(u'굴림')
        assert u"'굴림'" == xpath1(font, '@svg:font-family')
        assert 'swiss' == xpath1(font, '@style:font-family-generic')
        assert 'variable' == xpath1(font, '@style:font-pitch')

    def test_charshape(self):
        ''' 글자 모양 '''
        odt = example_to_odt('charshape.hwp')

        NOT_SPECIFIED = 1
        BOLD_ITALIC = 2
        UNDERLINES = 3
        FONTSIZE = 4
        FONTFACE = 5

        charshape = odt.automatic_style_text_properties(NOT_SPECIFIED, 1, 1)
        assert charshape is None

        #
        # 진하게
        #

        charshape = odt.automatic_style_text_properties(BOLD_ITALIC, 1, 1)
        assert charshape is not None
        assert None is xpath1(charshape, '@fo:font-weight')
        assert None is xpath1(charshape, '@style:font-weight-asian')
        assert None is xpath1(charshape, '@style:font-weight-complex')

        charshape = odt.automatic_style_text_properties(BOLD_ITALIC, 1, 2)
        assert charshape is not None
        assert 'bold' == xpath1(charshape, '@fo:font-weight')
        assert 'bold' == xpath1(charshape, '@style:font-weight-asian')
        assert 'bold' == xpath1(charshape, '@style:font-weight-complex')

        #
        # 기울임
        #

        charshape = odt.automatic_style_text_properties(BOLD_ITALIC, 1, 1)
        assert charshape is not None
        assert 'italic' == xpath1(charshape, '@fo:font-style')
        assert 'italic' == xpath1(charshape, '@style:font-style-asian')
        assert 'italic' == xpath1(charshape, '@style:font-style-complex')

        charshape = odt.automatic_style_text_properties(BOLD_ITALIC, 1, 2)
        assert charshape is not None
        assert None is xpath1(charshape, '@fo:font-style')
        assert None is xpath1(charshape, '@style:font-style-asian')
        assert None is xpath1(charshape, '@style:font-style-complex')

        #
        # 밑줄
        #

        # underline: none
        charshape = odt.automatic_style_text_properties(UNDERLINES, 1, 1)
        assert 'none' == xpath1(charshape, '@style:text-underline-type')
        assert None is xpath1(charshape, '@style:text-underline-style')
        assert None is xpath1(charshape, '@style:text-underline-width')
        assert None is xpath1(charshape, '@style:text-underline-color')
        assert 'none' == xpath1(charshape, '@style:text-line-through-type')
        assert None is xpath1(charshape, '@style:text-line-through-style')
        assert None is xpath1(charshape, '@style:text-line-through-width')
        assert None is xpath1(charshape, '@style:text-line-through-color')
        assert 'none' == xpath1(charshape, '@style:text-overline-type')
        assert None is xpath1(charshape, '@style:text-overline-style')
        assert None is xpath1(charshape, '@style:text-overline-width')
        assert None is xpath1(charshape, '@style:text-overline-color')

        # underline: underline
        charshape = odt.automatic_style_text_properties(UNDERLINES, 1, 2)
        assert 'single' == xpath1(charshape, '@style:text-underline-type')
        assert 'solid' == xpath1(charshape, '@style:text-underline-style')
        assert 'auto' == xpath1(charshape, '@style:text-underline-width')
        assert '#000000' == xpath1(charshape, '@style:text-underline-color')
        assert 'none' == xpath1(charshape, '@style:text-line-through-type')
        assert None is xpath1(charshape, '@style:text-line-through-style')
        assert None is xpath1(charshape, '@style:text-line-through-width')
        assert None is xpath1(charshape, '@style:text-line-through-color')
        assert 'none' == xpath1(charshape, '@style:text-overline-type')
        assert None is xpath1(charshape, '@style:text-overline-style')
        assert None is xpath1(charshape, '@style:text-overline-width')
        assert None is xpath1(charshape, '@style:text-overline-color')

        # underline: unknown (TODO: should be linethrough)
        charshape = odt.automatic_style_text_properties(UNDERLINES, 1, 3)
        assert 'none' == xpath1(charshape, '@style:text-underline-type')
        assert None is xpath1(charshape, '@style:text-underline-style')
        assert None is xpath1(charshape, '@style:text-underline-width')
        assert None is xpath1(charshape, '@style:text-underline-color')
        assert 'single' == xpath1(charshape, '@style:text-line-through-type')
        assert 'solid' == xpath1(charshape, '@style:text-line-through-style')
        assert 'auto' == xpath1(charshape, '@style:text-line-through-width')
        assert '#000000' == xpath1(charshape, '@style:text-line-through-color')
        assert 'none' == xpath1(charshape, '@style:text-overline-type')
        assert None is xpath1(charshape, '@style:text-overline-style')
        assert None is xpath1(charshape, '@style:text-overline-width')
        assert None is xpath1(charshape, '@style:text-overline-color')

        # underline: upperline (TODO: should be overline)
        charshape = odt.automatic_style_text_properties(UNDERLINES, 1, 4)
        assert 'none' == xpath1(charshape, '@style:text-underline-type')
        assert None is xpath1(charshape, '@style:text-underline-style')
        assert None is xpath1(charshape, '@style:text-underline-width')
        assert None is xpath1(charshape, '@style:text-underline-color')
        assert 'none' == xpath1(charshape, '@style:text-line-through-type')
        assert None is xpath1(charshape, '@style:text-line-through-style')
        assert None is xpath1(charshape, '@style:text-line-through-width')
        assert None is xpath1(charshape, '@style:text-line-through-color')
        assert 'single' == xpath1(charshape, '@style:text-overline-type')
        assert 'solid' == xpath1(charshape, '@style:text-overline-style')
        assert 'auto' == xpath1(charshape, '@style:text-overline-width')
        assert '#000000' == xpath1(charshape, '@style:text-overline-color')

        #
        # 글자 크기
        #

        # 대표크기 10pt
        charshape = odt.automatic_style_text_properties(FONTSIZE, 1, 2)
        assert '10pt' == xpath1(charshape, '@fo:font-size')
        assert '10pt' == xpath1(charshape, '@style:font-size-asian')
        #assert '10pt' == xpath1(charshape, '@style:font-size-complex') # TODO

        # ko=90%
        charshape = odt.automatic_style_text_properties(FONTSIZE, 1, 3)
        assert '10pt' == xpath1(charshape, '@fo:font-size')
        #assert '9pt' == xpath1(charshape, '@style:font-size-asian') # TODO RelativeSize 반영
        #assert '10pt' == xpath1(charshape, '@style:font-size-complex') # TODO

        # en=80% TODO RelativeSizes 반영
        charshape = odt.automatic_style_text_properties(FONTSIZE, 1, 4)
        #assert '8pt' == xpath1(charshape, '@fo:font-size') # TODO RelativeSize 반영
        assert '10pt' == xpath1(charshape, '@style:font-size-asian')
        #assert '10pt' == xpath1(charshape, '@style:font-size-complex') # TODO

        # other=70% TODO RelativeSizes 반영
        charshape = odt.automatic_style_text_properties(FONTSIZE, 1, 5)
        assert '10pt' == xpath1(charshape, '@fo:font-size')
        assert '10pt' == xpath1(charshape, '@style:font-size-asian')
        #assert '10pt' == xpath1(charshape, '@style:font-size-complex') # TODO Relative Size 반영

        #
        # 폰트
        #
        # TODO: 영문, 외국어 폰트의 참조 방법을 찾아야. 현재 Courier New가 제대로 참조되지 않고 있다.

        charshape = odt.automatic_style_text_properties(FONTFACE, 1, 2)
        #assert u'바탕' == xpath1(charshape, '@style:font-name')
        assert u'돋움' == xpath1(charshape, '@style:font-name-asian')
        #assert u'바탕' == xpath1(charshape, '@style:font-name-complex') # TODO

        charshape = odt.automatic_style_text_properties(FONTFACE, 1, 3)
        # TODO
        #print xpath1(charshape, '@style:font-name')
        #assert u'Courier New' == xpath1(charshape, '@style:font-name')
        #assert u'바탕' == xpath1(charshape, '@style:font-name-asian')
        #assert u'바탕' == xpath1(charshape, '@style:font-name-complex') # TODO

        charshape = odt.automatic_style_text_properties(FONTFACE, 1, 4)
        # TODO
        #print xpath1(charshape, '@style:font-name-complex')
        #assert u'바탕' == xpath1(charshape, '@style:font-name')
        #assert u'바탕' == xpath1(charshape, '@style:font-name-asian')
        #assert u'Lucida Sans Unicode' == xpath1(charshape, '@style:font-name-complex')

    def test_paragraph(self):
        ''' 문단 모양 '''
        odt = example_to_odt('parashape.hwp')

        para = xpath1(odt.content, '//text:p[1]')
        assert 'Paragraph-1' == xpath1(para, '@text:style-name')
        parashape = odt.automatic_style_paragraph_properties(1)
        assert parashape is not None
        assert 'justify' == xpath1(parashape, '@fo:text-align')
        assert '0pt' == xpath1(parashape, '@fo:text-indent')
        assert '11pt' == xpath1(parashape, '@fo:margin-left')
        assert '12pt' == xpath1(parashape, '@fo:margin-right')
        assert '13pt' == xpath1(parashape, '@fo:margin-top')
        assert '14pt' == xpath1(parashape, '@fo:margin-bottom')

        para = xpath1(odt.content, '//text:p[2]')
        assert u'바탕글' == xpath1(para, '@text:style-name')
        assert None is odt.automatic_style_paragraph_properties(2)

        para = xpath1(odt.content, '//text:p[3]')
        assert 'Paragraph-3' == xpath1(para, '@text:style-name')
        parashape = odt.automatic_style_paragraph_properties(3)
        assert parashape is not None
        assert '10pt' == xpath1(parashape, '@fo:text-indent')
        assert '0pt' == xpath1(parashape, '@fo:margin-left')

        para = xpath1(odt.content, '//text:p[4]')
        assert 'Paragraph-4' == xpath1(para, '@text:style-name')
        parashape = odt.automatic_style_paragraph_properties(4)
        assert parashape is not None
        assert '-10pt' == xpath1(parashape, '@fo:text-indent')
        assert '10pt' == xpath1(parashape, '@fo:margin-left')

        #
        # fo:text-align
        #
        parashape = odt.automatic_style_paragraph_properties(5)
        assert 'left' == xpath1(parashape, '@fo:text-align')

        parashape = odt.automatic_style_paragraph_properties(6)
        assert 'right' == xpath1(parashape, '@fo:text-align')

        parashape = odt.automatic_style_paragraph_properties(7)
        assert 'center' == xpath1(parashape, '@fo:text-align')

        parashape = odt.automatic_style_paragraph_properties(8)
        assert 'justify' == xpath1(parashape, '@fo:text-align')

        parashape = odt.automatic_style_paragraph_properties(9)
        #assert 'justify' == xpath1(parashape, '@fo:text-align') # TODO

    def test_linespacing_type(self):
        ''' 문단 모양 - 줄 간격 '''
        odt = example_to_odt('linespacing.hwp')

        # linespacing-type = ratio, 150%
        paraprops = odt.automatic_style_paragraph_properties(3)
        assert '150%' == xpath1(paraprops, '@fo:line-height')
        assert [] == xpath(paraprops, '@style:vertical-align')
        assert [] == xpath(paraprops, '@style:line-spacing')

        # linespacing-type = fixed, 15pt
        paraprops = odt.automatic_style_paragraph_properties(5)
        assert '15pt' == xpath1(paraprops, '@fo:line-height')
        assert 'top' == xpath1(paraprops, '@style:vertical-align')
        assert [] == xpath(paraprops, '@style:line-spacing')

        # linespacing-type = spaceonly, 5pt
        paraprops = odt.automatic_style_paragraph_properties(7)
        assert [] == xpath(paraprops, '@fo:line-height')
        assert [] == xpath(paraprops, '@style:vertical-align')
        assert '2.5pt' == xpath1(paraprops, '@style:line-spacing')

    def test_paragraph_split_page(self):
        ''' 쪽 나누기 (Ctrl+Enter)
        
            만약 Paragraph/@new-page = 1이면
            @fo:break-before = 'page'
        '''
        odt = example_to_odt('paragraph-split-page.hwp')

        assert None is odt.automatic_style_paragraph_properties(1)

        assert None is odt.automatic_style_paragraph_properties(2)

        paraprops = odt.automatic_style_paragraph_properties(3)
        assert 'page' == xpath1(paraprops, '@fo:break-before')

    def test_pagedefs(self):
        ''' PageDef 변환 테스트
        
            style:page-layout
            style:master-page
            @style:master-page-name
            '''
        odt = example_to_odt('pagedefs.hwp')

        plprops = odt.automatic_pagelayout_properties(1)
        assert 'portrait' == xpath1(plprops, '@style:print-orientation')
        assert '21cm' == xpath1(plprops, '@fo:page-width')
        assert '29.7cm' == xpath1(plprops, '@fo:page-height')
        assert '3cm' == xpath1(plprops, '@fo:margin-left')
        assert '3cm' == xpath1(plprops, '@fo:margin-right')
        assert '2cm' == xpath1(plprops, '@fo:margin-top')
        assert '1.5cm' == xpath1(plprops, '@fo:margin-bottom')

        plprops = odt.automatic_pagelayout_properties(2)
        assert 'landscape' == xpath1(plprops, '@style:print-orientation')
        assert '29.7cm' == xpath1(plprops, '@fo:page-width')
        assert '21cm' == xpath1(plprops, '@fo:page-height')
        # TODO: landscape가 되면, width/height처럼 margin들도 바뀌어야 하는 건 아닌가? 확인 필요
        assert '3cm' == xpath1(plprops, '@fo:margin-left')
        assert '3cm' == xpath1(plprops, '@fo:margin-right')
        assert '2cm' == xpath1(plprops, '@fo:margin-top')
        assert '1.5cm' == xpath1(plprops, '@fo:margin-bottom')

        mstpage = odt.master_page(1)
        assert 'PageLayout-1' == xpath1(mstpage, '@style:page-layout-name')

        mstpage = odt.master_page(2)
        assert 'PageLayout-2' == xpath1(mstpage, '@style:page-layout-name')

        parastyle = odt.automatic_style_paragraph(1)
        assert 'MasterPage-1' == xpath1(parastyle, '@style:master-page-name')

        parastyle = odt.automatic_style_paragraph(2)
        assert 'MasterPage-2' == xpath1(parastyle, '@style:master-page-name')

    def test_table(self):
        ''' 표 '''
        odt = example_to_odt('table.hwp')

        table = xpath1(odt.content, '//table:table')
        assert '3' == xpath1(table, 'table:table-column/@table:number-columns-repeated')
        assert '1' == xpath1(table, 'table:table-row[1]/table:table-cell[1]/@table:number-columns-spanned')
        assert '1' == xpath1(table, 'table:table-row[1]/table:table-cell[1]/@table:number-rows-spanned')
        assert '1' == xpath1(table, 'table:table-row[1]/table:table-cell[2]/@table:number-columns-spanned')
        assert '1' == xpath1(table, 'table:table-row[1]/table:table-cell[2]/@table:number-rows-spanned')
        assert '1' == xpath1(table, 'table:table-row[1]/table:table-cell[3]/@table:number-columns-spanned')
        assert '2' == xpath1(table, 'table:table-row[1]/table:table-cell[3]/@table:number-rows-spanned')
        assert '2' == xpath1(table, 'table:table-row[2]/table:table-cell[1]/@table:number-columns-spanned')
        assert '1' == xpath1(table, 'table:table-row[2]/table:table-cell[1]/@table:number-rows-spanned')
        assert None is xpath1(table, 'table:table-row[2]/table:table-cell[2]/@table:number-columns-spanned')
        assert None is xpath1(table, 'table:table-row[2]/table:table-cell[2]/@table:number-rows-spanned')
        assert None is xpath1(table, 'table:table-row[2]/table:table-cell[3]/@table:number-columns-spanned')
        assert None is xpath1(table, 'table:table-row[2]/table:table-cell[3]/@table:number-rows-spanned')

    def test_shaperect(self):
        ''' 그리기 객체 ShapeRectangle '''
        odt = example_to_odt('shaperect.hwp')

        rect = xpath1(odt.content, '//draw:rect[2]')
        assert rect is not None
        assert 'Shape-2' == xpath1(rect, '@draw:style-name')
        assert '39.69mm' == xpath1(rect, '@svg:x')
        assert '73.55mm' == xpath1(rect, '@svg:y')
        assert '71.26mm' == xpath1(rect, '@svg:width')
        assert '12.17mm' == xpath1(rect, '@svg:height')
        assert 'paragraph' == xpath1(rect, '@text:anchor-type')
        assert u'글 상자' == xpath1(rect, 'text:p/text:span/text()')

        # fill solid
        # stroke none
        props = odt.automatic_style_shaperect_graphic_properties(1)
        assert 'solid' == xpath1(props, '@draw:fill')
        assert '#66ccff' ==  xpath1(props, '@draw:fill-color')
        assert 'none' == xpath1(props, '@draw:stroke')
        assert '0.12mm' == xpath1(props, '@svg:stroke-width')
        assert '#000000' == xpath1(props, '@svg:stroke-color')

        # TODO: gradation fill
        props = odt.automatic_style_shaperect_graphic_properties(2)
        assert 'none' == xpath1(props, '@draw:fill')
        assert None is xpath1(props, '@draw:fill-color')
        assert 'dash' == xpath1(props, '@draw:stroke')
        assert '0.12mm' == xpath1(props, '@svg:stroke-width')
        assert '#000000' == xpath1(props, '@svg:stroke-color')

        # fill none
        # stroke solid
        props = odt.automatic_style_shaperect_graphic_properties(3)
        assert 'none' == xpath1(props, '@draw:fill')
        assert None is xpath1(props, '@draw:fill-color')
        assert 'dash' == xpath1(props, '@draw:stroke')
        assert '0.12mm' == xpath1(props, '@svg:stroke-width')
        assert '#000000' == xpath1(props, '@svg:stroke-color')

        # TODO: hatched fill
        props = odt.automatic_style_shaperect_graphic_properties(4)
        assert 'solid' == xpath1(props, '@draw:fill')
        assert '#ffffff' == xpath1(props, '@draw:fill-color')
        assert 'solid' == xpath1(props, '@draw:stroke')
        assert '0.12mm' == xpath1(props, '@svg:stroke-width')
        assert '#ff0033' == xpath1(props, '@svg:stroke-color')

    def test_shapeline(self):
        ''' 그리기 객체 ShapeLine '''
        odt = example_to_odt('shapeline.hwp')

        line = xpath1(odt.content, '//draw:line[1]')
        assert line is not None
        assert '32.98mm' == xpath1(line, '@svg:x1')
        assert '38.28mm' == xpath1(line, '@svg:y1')
        assert '40.39mm' == xpath1(line, '@svg:x2')
        assert '45.51mm' == xpath1(line, '@svg:y2')

    def test_shapepicture(self):
        ''' 그림 객체 ShapePicture '''
        odt = example_to_odt('sample-5017.hwp')

        assert 2 == len(xpath(odt.content, '//draw:frame'))

        frame1, frame2 = xpath(odt.content, '//draw:frame')

        assert frame1 is not None
        assert 'Shape-1' == xpath1(frame1, '@draw:style-name')
        assert 'paragraph' == xpath1(frame1, '@text:anchor-type')
        assert '111.73pt' == xpath1(frame1, '@svg:x')
        assert '4.9pt' == xpath1(frame1, '@svg:y')
        assert '2' == xpath1(frame1, '@draw:z-index')
        assert '57.68mm' == xpath1(frame1, '@svg:width')
        assert '34.61mm' == xpath1(frame1, '@svg:height')
        assert 'bindata/BIN0002.jpg' == xpath1(frame1, 'draw:image/@xlink:href')

        assert frame2 is not None
        assert 'Shape-2' == xpath1(frame2, '@draw:style-name')
        # inline: as-char and no svg:x,y
        assert 'as-char' == xpath1(frame2, '@text:anchor-type')
        assert None is xpath1(frame2, '@svg:x')
        assert None is xpath1(frame2, '@svg:y')
        assert '4' == xpath1(frame2, '@draw:z-index')
        assert '5.69mm' == xpath1(frame2, '@svg:width')
        assert '5.69mm' == xpath1(frame2, '@svg:height')
        assert 'bindata/BIN0003.png' == xpath1(frame2, 'draw:image/@xlink:href')

    def test_shapepict_scaled(self):
        ''' 그림 객체 ShapePicture (scaled) '''
        odt = example_to_odt('shapepict-scaled.hwp')

        assert 2 == len(xpath(odt.content, '//draw:frame'))

        frame1, frame2 = xpath(odt.content, '//draw:frame')

        assert frame1 is not None
        assert 'Shape-1' == xpath1(frame1, '@draw:style-name')
        assert 'paragraph' == xpath1(frame1, '@text:anchor-type')
        assert '0pt' == xpath1(frame1, '@svg:x')
        assert '0pt' == xpath1(frame1, '@svg:y')
        assert '0' == xpath1(frame1, '@draw:z-index')
        assert '20.07mm' == xpath1(frame1, '@svg:width')
        assert '12.04mm' == xpath1(frame1, '@svg:height')
        assert 'bindata/BIN0002.jpg' == xpath1(frame1, 'draw:image/@xlink:href')

        assert frame2 is not None
        assert 'Shape-2' == xpath1(frame2, '@draw:style-name')
        assert '0pt' == xpath1(frame2, '@svg:x')
        assert '0pt' == xpath1(frame2, '@svg:y')
        assert '1' == xpath1(frame2, '@draw:z-index')
        assert '20.07mm' == xpath1(frame2, '@svg:width')
        assert '12.04mm' == xpath1(frame2, '@svg:height')
        assert 'bindata/BIN0002.jpg' == xpath1(frame2, 'draw:image/@xlink:href')

    def test_shapepict_scaled_in_group(self):
        ''' 그림 객체 ShapePicture (scaled, grouped) '''
        odt = example_to_odt('shapecontainer-2.hwp')

        assert 1 == len(xpath(odt.content, '//draw:frame'))

        frame1 = xpath1(odt.content, '//draw:frame')

        assert frame1 is not None
        assert 'Shape-3' == xpath1(frame1, '@draw:style-name')
        assert None is xpath1(frame1, '@text:anchor-type')
        assert None is xpath1(frame1, '@svg:x')
        assert None is xpath1(frame1, '@svg:y')
        assert None is xpath1(frame1, '@draw:z-index')  # TODO
        assert '161.92mm' == xpath1(frame1, '@svg:width')
        assert '22.23mm' == xpath1(frame1, '@svg:height')
        assert 'bindata/BIN0001.jpg' == xpath1(frame1, 'draw:image/@xlink:href')

    def test_aligns(self):
        ''' 그림 객체 ShapePicture '''
        odt = example_to_odt('aligns.hwp')
        rect = xpath(odt.content, '//draw:rect')

        # NOTE: svg:x/svg:y와 연계해서 위치를 지정할 수 있는 건
        # from-left, from-top 뿐이므로, 다른 방향으로부터 지정된
        # 값들은 기준 공간과 객체의 너비/높이를 사용하여
        # from-left와 ftom-top의 값으로 변환되어야 함
        # 이때 기준 공간은 horizontal/vertical-rel 값으로
        # 정해짐. 이 테스트에서는 page-content로 고정되어 있으므로,
        # 기준 공간은 종이의 여백을 제외한 텍스트 영역이 됨.

        # NOTE: horizontal/vertical-pos를 center/right/middle/bottom
        # 등으로 지정할 수 있는 특수한 경우들에 대한 처리가 되는지 확인한다
        # 가령 halign=center, x=0 이라면 horizontal-pos를 center로
        # 지정할 수 있다

        # halign: left 0mm
        props = odt.automatic_style_shaperect_graphic_properties(1)
        self.assertEquals('from-left', xpath1(props, '@style:horizontal-pos'))
        self.assertEquals('0mm', xpath1(rect[0], '@svg:x'))

        # halign: left 10mm
        props = odt.automatic_style_shaperect_graphic_properties(2)
        self.assertEquals('from-left', xpath1(props, '@style:horizontal-pos'))
        self.assertEquals('10mm', xpath1(rect[1], '@svg:x'))

        # halign: center 0mm
        props = odt.automatic_style_shaperect_graphic_properties(3)
        self.assertEquals('center', xpath1(props, '@style:horizontal-pos'))
        self.assertEquals('0mm', xpath1(rect[2], '@svg:x'))

        # halign: center -10mm
        props = odt.automatic_style_shaperect_graphic_properties(4)
        #self.assertEquals('center', xpath1(props, '@style:horizontal-pos'))
        #self.assertEquals('0mm', xpath1(rect[3], '@svg:x'))

        # halign: right 0mm
        props = odt.automatic_style_shaperect_graphic_properties(5)
        self.assertEquals('right', xpath1(props, '@style:horizontal-pos'))
        self.assertEquals('0mm', xpath1(rect[4], '@svg:x'))

        # halign: right 10mm
        props = odt.automatic_style_shaperect_graphic_properties(6)
        #self.assertEquals('right', xpath1(props, '@style:horizontal-pos'))
        #self.assertEquals('0mm', xpath1(rect[5], '@svg:x'))

        # halign: inside 0mm
        props = odt.automatic_style_shaperect_graphic_properties(7)
        self.assertEquals('from-inside', xpath1(props, '@style:horizontal-pos'))
        self.assertEquals('0mm', xpath1(rect[6], '@svg:x'))

        # halign: inside 10mm
        props = odt.automatic_style_shaperect_graphic_properties(8)
        #self.assertEquals('from-inside', xpath1(props, '@style:horizontal-pos'))
        #self.assertEquals('0mm', xpath1(rect[7], '@svg:x'))

        # halign: outside 0mm
        props = odt.automatic_style_shaperect_graphic_properties(9)
        self.assertEquals('outside', xpath1(props, '@style:horizontal-pos'))
        self.assertEquals('0mm', xpath1(rect[8], '@svg:x'))

        # halign: outside 10mm
        props = odt.automatic_style_shaperect_graphic_properties(10)
        #self.assertEquals('outside', xpath1(props, '@style:horizontal-pos'))
        #self.assertEquals('0mm', xpath1(rect[9], '@svg:x'))

        # valign: top 0mm
        props = odt.automatic_style_shaperect_graphic_properties(11)
        self.assertEquals('from-top', xpath1(props, '@style:vertical-pos'))
        self.assertEquals('0mm', xpath1(rect[10], '@svg:y'))

        # valign: top 10mm
        props = odt.automatic_style_shaperect_graphic_properties(12)
        self.assertEquals('from-top', xpath1(props, '@style:vertical-pos'))
        self.assertEquals('10mm', xpath1(rect[11], '@svg:y'))

        # valign: center 0mm
        props = odt.automatic_style_shaperect_graphic_properties(13)
        self.assertEquals('middle', xpath1(props, '@style:vertical-pos'))
        #self.assertEquals('0mm', xpath1(rect[12], '@svg:y'))

        # valign: center 10mm
        props = odt.automatic_style_shaperect_graphic_properties(14)
        #self.assertEquals('middle', xpath1(props, '@style:vertical-pos'))
        #self.assertEquals('10mm', xpath1(rect[13], '@svg:y'))

        # valign: bottom 0mm
        props = odt.automatic_style_shaperect_graphic_properties(15)
        self.assertEquals('bottom', xpath1(props, '@style:vertical-pos'))
        self.assertEquals('0mm', xpath1(rect[14], '@svg:y'))

        # valign: bottom 10mm
        props = odt.automatic_style_shaperect_graphic_properties(16)
        #self.assertEquals('bottom', xpath1(props, '@style:vertical-pos'))
        #self.assertEquals('10mm', xpath1(rect[15], '@svg:y'))


class TestConverter(TestCase):

    def test_convert_bindata(self):
        hwp5file = example('sample-5017.hwp')
        try:
            f = hwp5file['BinData']['BIN0002.jpg'].open()
            try:
                data1 = f.read()
            finally:
                f.close()

            from hwp5.hwp5odt import convert, ODTPackage
            odtpkg = ODTPackage('sample-5017.odt')
            try:
                convert(hwp5file, odtpkg)
            finally:
                odtpkg.close()
        finally:
            hwp5file.close()

        from zipfile import ZipFile
        zf = ZipFile('sample-5017.odt')
        data2 = zf.read('bindata/BIN0002.jpg')

        self.assertEquals(data1, data2)
