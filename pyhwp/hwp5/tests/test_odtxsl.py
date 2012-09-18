# -*- coding: utf-8 -*-
from unittest import TestCase
from hwp5.utils import cached_property

def example(filename):
    from hwp5.tests import get_fixture_path
    from hwp5.xmlmodel import Hwp5File
    path = get_fixture_path(filename)
    return Hwp5File(path)

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
        from tempfile import TemporaryFile
        f = TemporaryFile()
        try:
            xmlfile = file(self.xmlfilename, 'r')
            try:
                convert.xslt_content(xmlfile, f)
                f.seek(0)
            finally:
                xmlfile.close()
            return f
        except:
            f.close()
            raise

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
        from tempfile import TemporaryFile
        f = TemporaryFile()
        try:
            xmlfile = file(self.xmlfilename, 'r')
            try:
                convert.xslt_styles(xmlfile, f)
                f.seek(0)
            finally:
                xmlfile.close()
            return f
        except:
            f.close()
            raise

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
