# -*- coding: utf-8 -*-
#
#                    GNU AFFERO GENERAL PUBLIC LICENSE
#                       Version 3, 19 November 2007
#
#    pyhwp : hwp file format parser in python
#    Copyright (C) 2010 mete0r@sarangbang.or.kr
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import hwp50
try:
    import xml.etree.ElementTree as ET
except ImportError:
    import elementtree.ElementTree as ET

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import sys
import logging

def indent_xml(elem, level, isLast=False):
    indent = '  '
    p = None
    for e in elem:
        if p is not None:
            indent_xml(p, level+1)
        p = e
    if p is not None:
        indent_xml(p, level+1, True)
        if p.tail is None:
            p.tail = ''
        p.tail += '\n' + indent*level

    if len(elem) > 0:
        if elem.text is None:
            elem.text = ''
        elem.text += '\n' + indent*(level+1)

    if not isLast:
        if elem.tail is None:
            elem.tail = ''
        elem.tail += '\n' + indent*level

mm = lambda x: str(x.mm)+'mm'
pt = lambda x: str(x.pt)+'pt'
px = lambda x: str(x.px)+'px'

class LocalDestination:
    def __init__(self, rootname):
        self.htmlfile = file(rootname+'.html', 'w')
        self._attachmentdir = rootname+'.files/'
    def addAttachment(self, name, data):
        import os, os.path
        if not os.path.isdir(self._attachmentdir):
            os.mkdir(self._attachmentdir)
        attfilename = self._attachmentdir+name
        attfile = file(attfilename, 'wb')
        attfile.write(data)
        attfile.close()
        return attfilename
    def close(self):
        self.htmlfile.close()

class ZipDestination:
    def __init__(self, rootname):
        import zipfile
        self._zf = zipfile.ZipFile(rootname+'.zip', 'w', zipfile.ZIP_DEFLATED)
        self.htmlfile = StringIO()
        self.rootname = rootname
    def addAttachment(self, name, data):
        self._zf.writestr(name, data)
        return name
    def close(self):
        data = self.htmlfile.getvalue()
        self._zf.writestr(self.rootname+'.html', data)

def cssdir(lrtb):
    return [lrtb[2], lrtb[1], lrtb[3], lrtb[0]]

def compact_cssdir(trbl):
    if trbl[0] == trbl[1] == trbl[2] == trbl[3]:
        x = [trbl[0]]
    elif trbl[0] == trbl[2] and trbl[1] == trbl[3]:
        x = [trbl[0], trbl[1]]
    else:
        x = trbl
    return ' '.join(x)

class CssDecls(dict):
    def __unicode__(self):
        return '; '.join([ '%s: %s'%(k,v) for k, v in self.iteritems() ])
    def __repr__(self):
        return 'CssDecls(%s)'%dict.__repr__(self)
    def parse(cls, s):
        decls = s.split(';')
        decls = []
        for decl in s.split(';'):
            decl = [x.strip() for x in decl.split(':', 1)]
            if len(decl) == 2:
                decls.append(decl)
        return cls(decls)
    parse = classmethod(parse)

class CssRule:
    def __init__(self, selectors=None, cssdecls={}):
        ''' selectors: list or string '''
        if selectors is None:
            self.selectors = []
        else:
            if isinstance(selectors, list):
                self.selectors = selectors
            else:
                self.selectors = [selectors]

        self.props = CssDecls(cssdecls)

    def getdecls(self):
        return unicode(self.props)

    def __setitem__(self, name, value):
        self.props[name] = value
    def __getitem__(self, name):
        return self.props[name]

    def __unicode__(self):
        return (u', '.join(self.selectors) + ' { \n'+self.getdecls().replace('; ', ';\n')+'\n}\n')

import re
class AttrClass:
    delim = re.compile('\s+')
    def __init__(self, attrib):
        self.attrib = attrib
    def getclasslist(self):
        classes = self.attrib.get('class', '').strip()
        if len(classes) == 0:
            classes = []
        else:
            classes = self.delim.split(classes)
        return classes
    def append(self, x):
        classes = self.getclasslist()
        classes.append(x)
        self.attrib['class'] = ' '.join(classes)
    def remove(self, x):
        l = self.attrib['class'].split(' ')
        l.remove(x)
        self.attrib['class'] = ' '.join(l)
    def __iter__(self):
        return iter(self.getclasslist())
    def __unicode__(self):
        return self.attrib.get('class', u'')

class AttrStyles:
    def __init__(self, attrib):
        self.attrib = attrib
    def getdict(self):
        styles = self.attrib.get('style', '').strip()
        return CssDecls.parse(styles)
    def setdict(self, styles):
        self.attrib['style'] = unicode(styles)
    def __setitem__(self, key, value):
        styles = self.getdict()
        styles[key] = value
        self.setdict(styles)
    def __delitem__(self, key):
        styles = self.getdict()
        del styles[key]
        self.setdict(styles)

x = ET.Element('div')
def element_getattr(self, name):
    if name == 'classes':
        return AttrClass(self.attrib)
    elif name == 'styles':
        return AttrStyles(self.attrib)
    raise AttributeError(name)
x.__class__.__getattr__ = element_getattr

class HtmlP:
    debug = False
    def __init__(self, paragraph_stylename=None, paraShapeId=None, charShapeId=None):
        p = P()
        if paragraph_stylename is not None:
            p.classes.append(paragraph_stylename)
        if paraShapeId is not None:
            p.classes.append('ParaShape-%d'%paraShapeId)
        if charShapeId is not None:
            p.classes.append('CharShape-%d'%charShapeId)
        self.charShapeId = charShapeId
        p.styles['position'] = 'relative'
        self.p = p
    def fromParagraph(cls, paragraph, stylenames):
        paragraph_stylename = stylenames.get(paragraph.style, None)
        if paragraph_stylename is None:
            logging.warning('paragraph style is missing')
        if paragraph.style.paragraphShapeId != paragraph.paragraphShapeId:
            paraShapeId = paragraph.paragraphShapeId
        else:
            paraShapeId = None
        charShapeId = paragraph.style.characterShapeId
        return cls(paragraph_stylename, paraShapeId, charShapeId)
    fromParagraph = classmethod(fromParagraph)
    def get(self):
        return self.p
    def addComment(self, s):
        self.p.append(ET.Comment(unicode(s)))
    def addText(self, text, charShapeId):
        if self.charShapeId == charShapeId:
            if len(self.p) == 0:
                if self.p.text is None:
                    self.p.text = text
                else:
                    self.p.text += text
            else:
                if self.p[-1].tail is None:
                    self.p[-1].tail = text
                else:
                    self.p[-1].tail += text
        else:
            span = Span()
            span.classes.append('CharShape-'+str(charShapeId))
            span.text = text
            self.p.append(span)
        if self.debug:
            self.addComment(repr(text))
    def addControlChar(self, e):
        if e.ch == e.LINE_BREAK:
            br = ET.Element('br')
            self.p.append(br)
        elif e.ch == e.PARAGRAPH_BREAK:
            # TODO: split htmlP
            cmt = ET.Comment('PARAGRAPH BREAK')
            self.p.append(cmt)
        elif e.ch in [e.NONBREAK_SPACE, e.FIXWIDTH_SPACE]:
            self.addText(u'\xa0', e.charShapeId) # unicode "&nbsp;"
        else:
            self.addText(e.ch, e.charShapeId)
    def addInlineControl(self, e):
        if e.ch == e.TAB:
            self.addText(e.ch, e.charShapeId)
        else:
            cmt = ET.Comment(str(e))
            self.p.append(cmt)
    def addImage(self, gso, img):
        styles = CssDecls()
        styles['width'] = mm(gso.width)
        wrapdiv = None
        if not gso.flags.inline:
            styles['display'] = 'block'
            if gso.flags.flow == gso.flags.FLOW_FLOAT: # 본문과의 배치: 어울림
                # float
                if gso.flags.textSide == gso.flags.TEXTSIDE_LEFT:
                    styles['float'] = 'right'
                    if gso.flags.horzAlign == gso.flags.HORZ_ALIGN_RIGHT:
                        styles['margin-right'] = mm(gso.offsetX)
                    elif gso.flags.horzAlign == gso.flags.HORZ_ALIGN_LEFT:
                        #TODO styles['margin-right'] = mm(doc.SHWPUNIT( page_width - gso.width - gso.offsetX ))
                        pass
                elif gso.flags.textSide == gso.flags.TEXTSIDE_RIGHT:
                    styles['float'] = 'left'
                    if gso.flags.horzAlign == gso.flags.HORZ_ALIGN_LEFT:
                        styles['margin-left'] = mm(gso.offsetX)
                    elif gso.flags.horzAlign == gso.flags.HORZ_ALIGN_RIGHT:
                        #TODO styles['margin-left'] = mm(doc.SHWPUNIT( page_width - gso.width - gso.offsetX ))
                        pass
                elif gso.flags.textSide == gso.flags.TEXTSIDE_BOTH:
                    logging.warning('unsupported <본문 위치>: 양쪽')
                    styles['position'] = 'absolute'
                    if gso.flags.horzAlign == gso.flags.HORZ_ALIGN_LEFT:
                        styles['left'] = mm(gso.offsetX)
                    elif gso.flags.horzAlign == gso.flags.HORZ_ALIGN_CENTER:
                        styles['left'] = mm(gso.offsetX) # TODO: + (50% of container)
                    elif gso.flags.horzAlign == gso.flags.HORZ_ALIGN_RIGHT:
                        styles['right'] = mm(gso.offsetX)
                elif gso.flags.textSide == gso.flags.TEXTSIDE_LARGER:
                    logging.warning('unsupported <본문 위치>: 큰 쪽')
                    pass
            elif gso.flags.flow == gso.flags.FLOW_BLOCK: # 본문과의 배치: 자리차지
                styles['position'] = 'relative'
                if gso.flags.horzAlign == gso.flags.HORZ_ALIGN_LEFT:
                    styles['left'] = mm(gso.offsetX)
                elif gso.flags.horzAlign == gso.flags.HORZ_ALIGN_CENTER:
                    styles['margin'] = 'auto'
                    styles['left'] = mm(gso.offsetX)
                elif gso.flags.horzAlign == gso.flags.HORZ_ALIGN_RIGHT:
                    styles['right'] = mm(gso.offsetX)
                    styles['position'] = 'absolute'
                    wrapdiv = ET.Element('div', {'style':'height:'+mm(gso.height)})
            elif gso.flags.flow == gso.flags.FLOW_BACK: # 본문과의 배치: 글 뒤로
                pass
            elif gso.flags.flow == gso.flags.FLOW_FRONT: # 본문과의 배치: 글 앞으로
                pass
        img.attrib['style'] = unicode(styles)
        if wrapdiv is not None:
            wrapdiv.append(img)
            img = wrapdiv
            wrapdiv = None
        self.p.append(img)

def makeCssPropsFromCharShape(doc, charShape):
    fonts = doc.docinfo.mappings[doc.FaceName]
    props = {}
    props['color'] = str(charShape.textColor)
    props['font-family'] = ', '.join([ fonts[face_id].fontName for face_id in charShape.langFontFace ])
    props['font-size'] = pt(doc.HWPUNIT(charShape.basesize))
    if charShape.attr & charShape.BOLD:
        props['font-weight'] = 'bold'
    else:
        props['font-weight'] = 'normal'
    if charShape.attr & charShape.ITALIC:
        props['font-style'] = 'italic'
    else:
        props['font-style'] = 'normal'

    SHWPUNIT = doc.SHWPUNIT
    letterSpacing = 0.0

    widthExp = (charShape.langLetterWidthExpansion[0] - 100) / 100.0
    letterSpacing = letterSpacing + charShape.basesize * widthExp
    letterSpacePercent = charShape.langLetterSpacing[0]
    letterSpacing = letterSpacing + charShape.basesize * (letterSpacePercent / 100.0)
    props['letter-spacing'] = pt(SHWPUNIT(letterSpacing))
    return props

def makeCssPropsFromParaShape(doc, paraShape):
    props = {}
    margin = [doc.SHWPUNIT(x/2) for x in [paraShape.marginTop, paraShape.marginRight, paraShape.marginBottom, paraShape.marginLeft]]
    props['margin'] = compact_cssdir([pt(x) for x in margin])

    alignments = {
            paraShape.ALIGN_BOTH:'justify',
            paraShape.ALIGN_LEFT:'left',
            paraShape.ALIGN_RIGHT:'right',
            paraShape.ALIGN_CENTER:'center',
            paraShape.ALIGN_DISTRIBUTE:'justify',
        }
    props['text-align'] = alignments.get(paraShape.align, 'justify')
    return props

def makeCssPropsFromParaShape_Indent(doc, paraShape):
    props = {}

    props['text-indent'] = pt(doc.SHWPUNIT(paraShape.indent/2))
    margin = [doc.SHWPUNIT(x/2) for x in [paraShape.marginTop, paraShape.marginRight, paraShape.marginBottom, paraShape.marginLeft]]
    # NOTE: difference between hwp indent and css text-indent
    # when indent value is less than 0,
    #   - paraShape.indent is applied to following lines, not beginning line
    #   - css text-indent is applied to beginning line
    if paraShape.indent.pt < 0:
        margin[-1] = doc.SHWPUNIT(margin[-1] - (paraShape.indent / 2))
    props['margin'] = compact_cssdir([pt(x) for x in margin])

    alignments = {
            paraShape.ALIGN_BOTH:'justify',
            paraShape.ALIGN_LEFT:'left',
            paraShape.ALIGN_RIGHT:'right',
            paraShape.ALIGN_CENTER:'center',
            paraShape.ALIGN_DISTRIBUTE:'justify',
        }
    props['text-align'] = alignments.get(paraShape.align, 'justify')
    return props

def makeCssBorder(borders):
    style = {}

    borderStyles = [
            'none',
            'solid',
            'dashed',
            'dotted',
            'dashed',
            'dashed',
            'dashed',
            'dotted',
            'double',
            'double',
            'double',
            'double',
            # ... TODO
            ]
    borderWidths = [
            '1px', #'0.01cm',
            '1px', #'0.012cm',
            '1px', #'0.015cm',
            '1px', #'0.02cm'
            '1px', #'0.025cm',
            '1px', #'0,03cm',
            '2px', #'0.04cm',
            '2px', #'0.05cm',
            '2px', #'0.06cm',
            '3px', #'0.07cm',
            '0.1cm',
            '0.15cm',
            '0.2cm',
            '0.3cm',
            '0.4cm',
            '0.5cm',
            ]

    borders = cssdir(borders)
    colors = [str(x.color) for x in borders]
    style['border-color'] = compact_cssdir(colors)
    widths = [borderWidths[x.width] for x in borders]
    style['border-width'] = compact_cssdir(widths)
    stys = [borderStyles[x.style] for x in borders]
    style['border-style'] = compact_cssdir(stys)
    return style

def makeCssBackground(doc, fill):
    style = {}
    if isinstance(fill, doc.FillColorPattern):
        style['background-color'] = str(fill.backgroundColor)
    return style

class View(object):
    def __init__(self, doc, model, **kwargs):
        self.doc = doc
        self.model = model
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        self.init()
    def init(self):
        pass
    def etree(self):
        raise NotImplemented

class OffsetView(View):
    line_position = 'absolute'
    def __init__(self, *args, **kwargs):
        View.__init__(self, *args, **kwargs)
        self.offsetY = 0
    def addParagraph(self, paragraph):
        for html in paragraph.etree():
            self.html.append(html)

    def addParagraphs(self, paragraphs):
        for paragraph, paragraph_lines in paragraphs:
            paragraph = Paragraph(self.doc, paragraph, offset=self)
            for line, line_elements in paragraph_lines:
                line = Line(self.doc, line, paragraph=paragraph)
                for element in line_elements:
                    line.addElement(element)
                paragraph.addLine(line)
            self.addParagraph(paragraph)

class Document:
    def __init__(self, model, **kwargs):
        self.model = model
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        self.init()
    def init(self):
        self.html = html = ET.Element('html')
        html.attrib['xmlns'] = 'http://www.w3.org/1999/xhtml'
        self.head = head = ET.SubElement(html, 'head')
        meta = ET.SubElement(head, 'meta', {'http-equiv':'Content-Type', 'content':'application/xhtml+xml; charset=utf-8'})
        meta = ET.SubElement(head, 'meta', {'name' : 'HWP File Format Version' , 'content':'.'.join([str(x) for x in self.model.header.version]) })
        self.style = style = ET.SubElement(head, 'style', {'type':'text/css'})
        style.text = ''
        self.stylenames, cssrules = self.makeStyles(self.model)
        style.text += ''.join([unicode(cssrule) for cssrule in cssrules])
        for charShape in self.model.docinfo.mappings[self.model.CharShape]:
            cssrule = CssRule()
            cssrule.selectors.append( '.CharShape-%d'%charShape.id )
            cssrule.props.update( makeCssPropsFromCharShape( self.model, charShape ) )
            style.text += unicode(cssrule)
        for paraShape in self.model.docinfo.mappings[self.model.ParaShape]:
            cssrule = CssRule()
            cssrule.selectors.append( '.ParaShape-%d'%paraShape.id )
            cssrule.props.update( makeCssPropsFromParaShape( self.model, paraShape ) )
            style.text += unicode(cssrule)
        style.text += unicode(CssRule('.Paper', {'page-break-after':'always', 'background-color':'white'}))
        style.text += unicode(CssRule('.Page', {'position':'relative', 'background-color':'#eee'}))
        style.text += unicode(CssRule('.Line', {'position':'absolute'}))
        style.text += unicode(CssRule('body', { 'background-color':'#ccc'}))

        self.body = body = ET.SubElement(html, 'body')

    def makeStyles(cls, doc):
        styles = {}
        cssrules = []
        for s in doc.docinfo.mappings[doc.Style]:
            if s.name != '':
                s_name = s.name
            else:
                s_name = 'Style %d'%s.id
            s_name = s_name.replace(' ', '-')
            styles[s] = s_name
            cssrule = CssRule()
            cssrule.props.update( makeCssPropsFromParaShape( doc, doc.docinfo.mappings[doc.ParaShape][s.paragraphShapeId] ) )
            cssrule.props.update( makeCssPropsFromCharShape( doc, doc.docinfo.mappings[doc.CharShape][s.characterShapeId] ) )
            cssrule.selectors.append( '.%s'%(s_name) )
            cssrules.append(cssrule)
        return styles, cssrules

    def etree(self):
        return ET.ElementTree( self.html )

class Section(View):
    def init(self):
        self.html = ET.Element('div', {'class':'Section'})

    def etree(self):
        yield ET.Comment(repr(self.model))
        yield self.html

    def addPage(self, page):
        for html in page.etree():
            self.html.append(html)

class Paper(View):
    def init(self):
        self.html = html = ET.Element('div', {'class':'Paper'})
        html.styles['margin'] = '0 auto'
        page_offset = list(self.model.offset)
        page_offset[2] = self.doc.model.HWPUNIT(page_offset[2] + self.model.headerOffset)
        page_offset[3] = self.doc.model.HWPUNIT(page_offset[3] + self.model.footerOffset)
        if self.model.attr.landscape:
            # TODO
            pass
        else:
            html.styles['width'] = mm( self.doc.model.HWPUNIT(self.model.width - page_offset[0] - page_offset[1]))
            html.styles['min-height'] = str(self.doc.model.HWPUNIT(self.model.height - page_offset[2] - page_offset[3]).mm)+'mm'
        page_offset[2] = page_offset[2]
        page_offset[3] = page_offset[3]
        html.styles['padding'] = compact_cssdir(cssdir( [mm(x) for x in page_offset] ))
        html.styles['border'] = '1px solid black'
    def etree(self):
        yield self.html

class Page(OffsetView):
    def init(self):
        self.paper = Paper(self.doc, self.model)
        self.html = ET.SubElement(self.paper.html, 'div', {'class':'Page'})
        self.offsetY = 0

    def etree(self):
        if len(self.html) == 0 and (self.html.text == None or len(self.html.text) == 0):
            self.html.text = u'\xa0'
        return self.paper.etree()

class Paragraph(View):
    def init(self):
        self.offsetY = self.offset.offsetY + self.model.lineSegs[0].offsetY

        self.html = ET.Element('div', {'class':'Paragraph'})
        html = self.html

        paragraph_stylename = self.doc.stylenames.get(self.model.style, None)
        if paragraph_stylename is None:
            logging.warning('self.model style is missing')
        else:
            html.classes.append(paragraph_stylename)
        if self.model.style.paragraphShapeId != self.model.paragraphShapeId:
            html.classes.append('ParaShape-%d'%self.model.paragraphShapeId)
        html.classes.append('CharShape-%d'%self.model.style.characterShapeId)

        SHWPUNIT = self.doc.model.SHWPUNIT
        paraShapeId = self.model.paragraphShapeId
        paraShape = self.doc.model.docinfo.mappings[self.doc.model.ParaShape][paraShapeId]
        self.left = SHWPUNIT(paraShape.marginLeft/2)
        self.text_indent = SHWPUNIT(paraShape.indent/2)

    def etree(self):
        if len(self.html) == 0 and (self.html.text == None or len(self.html.text) == 0):
            self.html.text = u'\xa0'
        yield ET.Comment('Record #%d'%self.model.record.seqno)
        yield ET.Comment(repr(self.model))
        yield ET.Comment('left-margin: %s, text-indent: %s'%(pt(self.left), pt(self.text_indent)))
        yield self.html

    def addLine(self, line):
        line.onAddToParagraph(self)
        for html in line.etree():
            self.html.append(html)

    def buildTableTree(self, table):
        table = Table(self.doc, table)
        if table.model.caption is not None:
            caption = TableCaption(self.doc, table.model.caption)
            for paragraphs in hwp50.getPagedParagraphs(caption.model.paragraphs):
                caption.addParagraphs(paragraphs)
            table.addCaption(caption)
        for row_number, row_cells in table.model.getRows():
            tr = TableRow(self.doc, row_number)
            for cell in row_cells:
                cell = TableCell(self.doc, cell)
                for paragraphs in hwp50.getPagedParagraphs(cell.model.paragraphs):
                    cell.addParagraphs(paragraphs)
                tr.addCell(cell)
            table.addRow(tr)
        return table

    def addControl(self, control, viewobj):
        SHWPUNIT = self.doc.model.SHWPUNIT
        styles = CssDecls()
        styles['width'] = mm(control.width)
        styles['height'] = mm(control.height)
        wrapdiv = None
        assert(not control.flags.inline)
        styles['display'] = 'block'
        if control.flags.flow == control.flags.FLOW_FLOAT: # 본문과의 배치: 어울림
            # float
            if control.flags.textSide == control.flags.TEXTSIDE_LEFT:
                styles['float'] = 'right'
                if control.flags.horzAlign == control.flags.HORZ_ALIGN_RIGHT:
                    styles['margin-right'] = mm(control.offsetX)
                elif control.flags.horzAlign == control.flags.HORZ_ALIGN_LEFT:
                    #TODO styles['margin-right'] = mm(doc.SHWPUNIT( page_width - control.width - control.offsetX ))
                    pass
            elif control.flags.textSide == control.flags.TEXTSIDE_RIGHT:
                styles['float'] = 'left'
                if control.flags.horzAlign == control.flags.HORZ_ALIGN_LEFT:
                    styles['margin-left'] = mm(control.offsetX)
                elif control.flags.horzAlign == control.flags.HORZ_ALIGN_RIGHT:
                    #TODO styles['margin-left'] = mm(doc.SHWPUNIT( page_width - control.width - control.offsetX ))
                    pass
            elif control.flags.textSide == control.flags.TEXTSIDE_BOTH:
                logging.warning('unsupported <본문 위치>: 양쪽')
                styles['position'] = 'absolute'
                if control.flags.horzAlign == control.flags.HORZ_ALIGN_LEFT:
                    styles['left'] = mm(control.offsetX)
                elif control.flags.horzAlign == control.flags.HORZ_ALIGN_CENTER:
                    styles['left'] = mm(control.offsetX) # TODO: + (50% of container)
                elif control.flags.horzAlign == control.flags.HORZ_ALIGN_RIGHT:
                    styles['right'] = mm(control.offsetX)
            elif control.flags.textSide == control.flags.TEXTSIDE_LARGER:
                logging.warning('unsupported <본문 위치>: 큰 쪽')
                pass
        elif control.flags.flow == control.flags.FLOW_BLOCK: # 본문과의 배치: 자리차지
            styles['position'] = 'absolute'

            SHWPUNIT = self.doc.model.SHWPUNIT
            if control.flags.horzRelTo == control.flags.HORZ_RELTO_PAPER:
                x = 0 # TODO
            elif control.flags.horzRelTo == control.flags.HORZ_RELTO_PAGE:
                x = 0
            elif control.flags.horzRelTo == control.flags.HORZ_RELTO_COLUMN:
                x = 0 # TODO
            elif control.flags.horzRelTo == control.flags.HORZ_RELTO_PARAGRAPH:
                x = self.left

            if control.flags.horzAlign == control.flags.HORZ_ALIGN_LEFT:
                styles['left'] = mm(SHWPUNIT(x + control.margin[control.MARGIN_LEFT] + control.offsetX))
            elif control.flags.horzAlign == control.flags.HORZ_ALIGN_CENTER:
                styles['left'] = mm(control.offsetX) # TODO
            elif control.flags.horzAlign == control.flags.HORZ_ALIGN_RIGHT:
                styles['right'] = mm(control.offsetX) # TODO
            
            if control.flags.vertRelTo == control.flags.VERT_RELTO_PAPER:
                styles['top'] = mm(SHWPUNIT(control.offsetY)) # TODO: minus page offset
            elif control.flags.vertRelTo == control.flags.VERT_RELTO_PAGE:
                styles['top'] = mm(control.offsetY)
            elif control.flags.vertRelTo == control.flags.VERT_RELTO_PARAGRAPH:
                y = SHWPUNIT(self.offsetY + control.offsetY + control.margin[control.MARGIN_TOP] - control.height)
                styles['top'] = mm(y)

            # TODO: VERT_ALIGN

        elif control.flags.flow == control.flags.FLOW_BACK: # 본문과의 배치: 글 뒤로
            logging.warning('unsupported: FLOW_BACK')
        elif control.flags.flow == control.flags.FLOW_FRONT: # 본문과의 배치: 글 앞으로
            logging.warning('unsupported: FLOW_FRONT')
        viewobj.html.attrib['style'] = unicode(styles)
        if wrapdiv is not None:
            for html in viewobj.etree():
                wrapdiv.append(html)
            self.html.append(wrapdiv)
        else:
            for html in viewobj.etree():
                self.html.append(html)

class Line(View):
    def init(self):
        self.html = ET.Element('div', {'class':'Line'})
        html = self.html
        html.styles['top'] = mm(self.model.offsetY)

        SHWPUNIT = self.doc.model.SHWPUNIT

        self.x = self.paragraph.left
        if self.paragraph.text_indent >= 0:
            if self.model.number_in_paragraph == 0:
                self.x += self.paragraph.text_indent
        else:
            if self.model.number_in_paragraph != 0:
                self.x -= self.paragraph.text_indent
        self.x = SHWPUNIT(self.x)

        html.styles['left'] = pt(self.x)
        html.styles['width'] = mm(self.model.a5[0])
        html.styles['height'] = pt(self.model.a2[1])
        #html.styles['margin-top'] = mm(self.model.a3[1])
    def onAddToParagraph(self, paragraph):
        self.html.styles['position'] = paragraph.offset.line_position
    def etree(self):
        if len(self.html) == 0 and (self.html.text == None or len(self.html.text) == 0):
            self.html.text = u'\xa0'
        yield ET.Comment(repr(self.model))
        yield ET.Comment('#%s line, x = %s' % (self.model.number_in_paragraph, pt(self.x)))
        yield self.html
    def addElement(self, elem):
        if isinstance(elem, self.doc.model.Text):
            self.addText(unicode(elem).replace(u' ', u'\xa0'), elem.charShapeId)
        elif isinstance(elem, self.doc.model.ControlChar):
            if elem.kinds == elem.char:
                self.addControlChar(elem)
            elif elem.kinds == elem.inline:
                self.addInlineChar(elem)
            else:
                self.addExtendedControl(elem)
        else:
            self.addComment(repr(elem))
    def addText(self, text, charShapeId):
        if self.paragraph.model.style.characterShapeId == charShapeId:
            if len(self.html) == 0:
                if self.html.text is None:
                    self.html.text = text
                else:
                    self.html.text += text
            else:
                if self.html[-1].tail is None:
                    self.html[-1].tail = text
                else:
                    self.html[-1].tail += text
        else:
            span = ET.SubElement(self.html, 'span')
            span.classes.append('CharShape-'+str(charShapeId))
            span.text = text
    def addComment(self, cmt):
        self.html.append(ET.Comment(repr(cmt)))
    def addControlChar(self, e):
        if e.ch == e.LINE_BREAK:
            br = ET.Element('br')
            self.html.append(br)
        elif e.ch == e.PARAGRAPH_BREAK:
            # TODO: split htmlP
            self.addComment('PARAGRAPH BREAK')
        elif e.ch in [e.NONBREAK_SPACE, e.FIXWIDTH_SPACE]:
            self.addText(u'\xa0', e.charShapeId) # unicode "&nbsp;"
        else:
            self.addText(e.ch, e.charShapeId)
    def addInlineChar(self, e):
        if e.ch == e.TAB:
            self.addText(e.ch, e.charShapeId)
        else:
            self.addComment(e)
    def addExtendedControl(self, e):
        if isinstance(e.control, self.doc.model.Table):
            table = e.control
            tableobj = self.paragraph.buildTableTree(table)
            if table.flags.inline:
                for html in tableobj.etree():
                    self.html.append(html)
            else:
                self.paragraph.addControl(table, tableobj)
        elif isinstance(e.control, self.doc.model.AutoNumber):
            #addText(span, str(e.control))
            pass
        elif isinstance(e.control, self.doc.model.FieldStart):
            pass
        elif isinstance(e.control, self.doc.model.GShapeObject) and isinstance(e.control.shapecomponent, self.doc.model.ShapeComponent) and isinstance(e.control.shapecomponent.shape, self.doc.model.ShapePicture):
            gso = e.control
            img = Image(self.doc, gso.shapecomponent.shape)
            if gso.flags.inline:
                for html in img.etree():
                    self.html.append(html)
            else:
                self.paragraph.addControl(gso, img)
        elif isinstance(e.control, self.doc.model.GShapeObject):
            pass
#                    style = CssDecls()
#                    style['position'] = 'relative'
#                    #style['top'] = mm(e.control.offsetY);
#                    style['left'] = mm(e.control.offsetX);
#                    divgso = ET.Element('div', {'class':'GShapeObject', 'style':unicode(style)})
#                    divgso.append(ET.Comment(str(e.control)))
#                    x = self.handle_shapecomponent(e.control, e.control.shapecomponent)
#                    divgso.append(x)
#
#                    if len(p[-1]) == 0 and (p[-1].text is None or len(p[-1].text) == 0):
#                        del p[-1]
#                    self.l.append(divgso)
        else:
            self.addComment(e)

class Image(View):
    def init(self):
        self.html = html = ET.Element('img')
        bindata = self.model.pictureInfo.binData
        if bindata.type == self.doc.model.BinEmbedded:
            if self.doc.destination is not None:
                html.attrib['src'] = self.doc.destination.addAttachment(str(bindata.name), bindata.datastream.read())
    def etree(self):
        yield ET.Comment(repr(self.model))
        yield self.html

class TableCaption(OffsetView):
    def init(self):
        self.html = html = ET.Element('caption')
        self.html.styles['position'] = 'absolute'
        self.html.styles['width'] = mm(self.model.width)
        if self.model.captflags.position == self.model.POS_BOTTOM:
            pass#self.
    def etree(self):
        yield ET.Comment(repr(self.model))
        yield self.html

class TableRow(View):
    def init(self):
        self.html = ET.Element('tr')
    def addCell(self, cell):
        for html in cell.etree():
            self.html.append(html)
    def etree(self):
        yield self.html

class TableCell(OffsetView):
    line_position = 'static'
    def init(self):
        self.html = html = ET.Element('td')

        if self.model.colspan > 1:
            self.html.attrib['colspan'] = str(self.model.colspan)
        if self.model.rowspan > 1:
            self.html.attrib['rowspan'] = str(self.model.rowspan)

        valign = {
                self.model.VALIGN_TOP:'top',
                self.model.VALIGN_MIDDLE:'middle',
                self.model.VALIGN_BOTTOM:'bottom'
                }.get(self.model.listflags & self.model.VALIGN_MASK, None)
        if valign is not None:
            self.html.attrib['valign'] = valign

        style = makeCssBorder(self.model.borderFill.border)
        style.update(makeCssBackground(self.doc.model, self.model.borderFill.fill))
        self.html.attrib['style'] = unicode(CssDecls(style))

        self.html.styles['padding'] = compact_cssdir(
                cssdir([mm(x) for x in self.model.padding]))

        self.html.styles['width'] = mm(self.model.width)
        self.html.styles['height'] = pt(self.model.height)
    def etree(self):
        if len(self.html) == 0 and (self.html.text is None or len(self.html.text)):
            self.html.text = u'\xa0'
        yield ET.Comment(repr(self.model))
        yield self.html

class Table(View):
    def init(self):
        self.html = html = ET.Element('table')
        html.attrib['cellspacing'] = unicode(self.model.body.cellspacing.px)
        html.append(ET.Comment(' '))

        style = {}
        style.update( makeCssBorder(self.model.borderFill.border) )
        if self.model.body.cellspacing == 0:
            style['border-collapse'] = 'collapse'
        style['width'] = mm(self.model.width)
        style['height'] = mm(self.model.height)
        style['margin'] = compact_cssdir(cssdir([mm(x) for x in self.model.margin]))
        html.attrib['style'] = '; '.join(['%s:%s'%(k,v) for k, v in style.iteritems()])

    def addCaption(self, caption):
        for html in caption.etree():
            self.html.append(html)
    def addRow(self, row):
        for html in row.etree():
            self.html.append(html)
    def etree(self):
        yield ET.Comment(repr(self.model))
        yield self.html

class HtmlConverter:
    destination = None
    def __init__(self):
        self.styles = {}
    def makeP_old(self, doc, paragraph):
        clss = []
        clss.append(self.styles[paragraph.style])
        if paragraph.style.paragraphShapeId != paragraph.paragraphShapeId:
            clss.append('ParaShape-%d'%paragraph.paragraphShapeId)

        linespacing = paragraph.paragraphShape.lineSpacingBefore2007
        cssrule = CssRule()
        # TODO
        linespctype = paragraph.paragraphShape.attr1.lineSpacingType
        if linespctype == 0:
            cssrule.props['line-height'] = str(linespacing)+'%'
        elif linespctype == 1:
            cssrule.props['line-height'] = mm(linespacing)

        p = ET.Element('div', {'class':' '.join(clss), 'style':'position:relative'})
        for shapedText in paragraph.shapedTexts:
            def newSpan():
                clss = []
                #if shapedText.characterShapeId != paragraph.style.characterShapeId:
                clss.append('CharShape-'+str(shapedText.characterShapeId))
                attrs = {}
                if len(clss) > 0:
                    attrs['class'] = ' '.join(clss)
                if linespctype == 2:
                    #print 'lineSpace type: %d, %d+%d'%(paragraph.paragraphShape.attr1.lineSpacingType, shapedText.characterShape.basesize, paragraph.paragraphShape.lineSpacingBefore2007)
                    fontsize = self.doc.HWPUNIT(shapedText.characterShape.basesize)
                    lineheight = self.doc.SHWPUNIT(fontsize + linespacing)
                    cssrule.props['line-height'] = pt(lineheight)
                attrs['style'] = cssrule.getdecls()
                return ET.SubElement(p, 'span', attrs)
            def addText(span, text):
                if len(span) > 0:
                    if span[-1].tail is None:
                        span[-1].tail = ''
                    span[-1].tail += text
                else:
                    if span.text is None:
                        span.text = ''
                    span.text += text
            span = newSpan()
            for e in shapedText.elements:
                if isinstance(e, unicode):
                    addText(span, e)
                elif isinstance(e, doc.ControlChar):
                    if e.kind == e.extended:
                        if isinstance(e.control, doc.Table):
                            tbl = self.makeTable(doc, e.control)
                            # TODO: layout
                            if e.control.flags.inline:
                                pass
                            p.append(tbl)
                            cmt = ET.Comment(str(e.control))
                            p.append(cmt)
                            span = newSpan()
                            continue
                        elif isinstance(e.control, doc.AutoNumber):
                            addText(span, str(e.control))
                            continue
                        elif isinstance(e.control, doc.FieldStart):
                            pass
                        elif isinstance(e.control, doc.GShapeObject) and isinstance(e.control.shapecomponent, doc.ShapeComponent) and isinstance(e.control.shapecomponent.shape, doc.ShapePicture):
                            gso = e.control
                            cssdecls = CssDecls()
                            cssdecls['width'] = mm(gso.width)
                            wrapdiv = None
                            if not gso.flags.inline:
                                cssdecls['display'] = 'block'
                                if gso.flags.flow == gso.flags.FLOW_FLOAT: # 본문과의 배치: 어울림
                                    # float
                                    if gso.flags.textSide == gso.flags.TEXTSIDE_LEFT:
                                        cssdecls['float'] = 'right'
                                        if gso.flags.horzAlign == gso.flags.HORZ_ALIGN_RIGHT:
                                            cssdecls['margin-right'] = mm(gso.offsetX)
                                        elif gso.flags.horzAlign == gso.flags.HORZ_ALIGN_LEFT:
                                            #TODO cssdecls['margin-right'] = mm(doc.SHWPUNIT( page_width - gso.width - gso.offsetX ))
                                            pass
                                    elif gso.flags.textSide == gso.flags.TEXTSIDE_RIGHT:
                                        cssdecls['float'] = 'left'
                                        if gso.flags.horzAlign == gso.flags.HORZ_ALIGN_LEFT:
                                            cssdecls['margin-left'] = mm(gso.offsetX)
                                        elif gso.flags.horzAlign == gso.flags.HORZ_ALIGN_RIGHT:
                                            #TODO cssdecls['margin-left'] = mm(doc.SHWPUNIT( page_width - gso.width - gso.offsetX ))
                                            pass
                                    elif gso.flags.textSide == gso.flags.TEXTSIDE_BOTH:
                                        logging.warning('unsupported <본문 위치>: 양쪽')
                                        cssdecls['position'] = 'absolute'
                                        if gso.flags.horzAlign == gso.flags.HORZ_ALIGN_LEFT:
                                            cssdecls['left'] = mm(gso.offsetX)
                                        elif gso.flags.horzAlign == gso.flags.HORZ_ALIGN_CENTER:
                                            cssdecls['left'] = mm(gso.offsetX) # TODO: + (50% of container)
                                        elif gso.flags.horzAlign == gso.flags.HORZ_ALIGN_RIGHT:
                                            cssdecls['right'] = mm(gso.offsetX)
                                    elif gso.flags.textSide == gso.flags.TEXTSIDE_LARGER:
                                        logging.warning('unsupported <본문 위치>: 큰 쪽')
                                        pass
                                elif gso.flags.flow == gso.flags.FLOW_BLOCK: # 본문과의 배치: 자리차지
                                    cssdecls['position'] = 'relative'
                                    if gso.flags.horzAlign == gso.flags.HORZ_ALIGN_LEFT:
                                        cssdecls['left'] = mm(gso.offsetX)
                                    elif gso.flags.horzAlign == gso.flags.HORZ_ALIGN_CENTER:
                                        cssdecls['margin'] = 'auto'
                                        cssdecls['left'] = mm(gso.offsetX)
                                    elif gso.flags.horzAlign == gso.flags.HORZ_ALIGN_RIGHT:
                                        cssdecls['right'] = mm(gso.offsetX)
                                        cssdecls['position'] = 'absolute'
                                        wrapdiv = ET.Element('div', {'style':'height:'+mm(gso.height)})
                                elif gso.flags.flow == gso.flags.FLOW_BACK: # 본문과의 배치: 글 뒤로
                                    pass
                                elif gso.flags.flow == gso.flags.FLOW_FRONT: # 본문과의 배치: 글 앞으로
                                    pass
                            img = self.makeImg(doc, e.control.shapecomponent.shape, cssdecls)
                            if wrapdiv is not None:
                                wrapdiv.append(img)
                                img = wrapdiv
                                wrapdiv = None
                            p.append(img)
                            cmt = ET.Comment(str(e.control))
                            p.append(cmt)
                            span = newSpan()
                            continue
                        elif isinstance(e.control, doc.GShapeObject):
                            style = CssDecls()
                            style['position'] = 'relative'
                            #style['top'] = mm(e.control.offsetY);
                            style['left'] = mm(e.control.offsetX);
                            divgso = ET.Element('div', {'class':'GShapeObject', 'style':unicode(style)})
                            divgso.append(ET.Comment(str(e.control)))
                            x = self.handle_shapecomponent(e.control, e.control.shapecomponent)
                            divgso.append(x)

                            if len(p[-1]) == 0 and (p[-1].text is None or len(p[-1].text) == 0):
                                del p[-1]
                            p.append(divgso)
                            span = newSpan()
                            continue
                        else:
                            cmt = str(e)+'\n'+str(e.control)
                            if isinstance(e.control, doc.GShapeObject):
                                cmt += '\n'+str(e.control.shapecomponent)
                            cmt = ET.Comment(cmt)
                            span.append(cmt)
                            continue
                        cmt = str(e)
                        cmt += ' '
                        cmt += str(e.control)
                        cmt = ET.Comment(cmt)
                        span.append(cmt)
                    elif e.kind == e.inline:
                        if e.ch == e.TAB:
                            addText(span, e.ch)
                        else:
                            cmt = str(e)
                            if e.kind == e.extended:
                                cmt += ' '
                                cmt += str(e.control)
                            cmt = ET.Comment(cmt)
                            span.append(cmt)
                    elif e.kind == e.char:
                        if e.ch == e.LINE_BREAK:
                            br = ET.Element('br')
                            span.append(br)
                        elif e.ch == e.PARAGRAPH_BREAK:
                            cmt = ET.Comment('PARAGRAPH BREAK')
                            span.append(cmt)
                            span.append(e.ch)
                        else:
                            addText(span, e.ch)
                else:
                    addText(span, str(e))
            if len(span) == 0 and span.text in [None, '', u'']:
                span.text = u'\xa0'
        if len(p) == 0:
            p.text = u'\xa0' # unicode nbsp
        return p
    def handle_shapecomponent(self, gso, shapecomponent):
        doc = self.doc
        if shapecomponent.chid == hwp50.CHID.CONTAINER:
        #if isinstance(shapecomponent, doc.ShapeContainer):
            #print 'controls', shapecomponent.controls
            style = CssDecls()
            # TODO
            style['position'] = 'absolute'
            #style['left'] = mm(shapecomponent.xoffsetInGroup)
            #style['top'] = mm(shapecomponent.yoffsetInGroup)
            style['width'] = mm(shapecomponent.width)
            style['height'] = mm(shapecomponent.height)
            div = ET.Element('div', {'class':'ShapeContainer', 'style':unicode(style)})
            cmt = ET.Comment(repr(shapecomponent))
            div.append(cmt)
            div.text = ' '
            for shp in shapecomponent.subshapes:
                k = self.handle_shapecomponent(gso, shp)
                if k is not None:
                    div.append(k)
            return div
        else:
            if isinstance(shapecomponent.shape, doc.ShapePicture):
                return self.makeImg(doc, shapecomponent.shape)
            else:
                div = ET.Element('div', {'class':'ShapeComponent-%s'%shapecomponent.chid})
                if isinstance(shapecomponent.shape, doc.ShapeRectangle):
                    cssdecls = CssDecls()
                    cssdecls['border'] = '1px solid gray'
                    cssdecls['position'] = 'absolute'

                    offset = (shapecomponent.xoffsetInGroup, shapecomponent.yoffsetInGroup)
                    for mat in list(reversed(shapecomponent.matScaleRotation))[1:]:
                        offset = mat.scaler.scale(offset)

                    dimens = (shapecomponent.initialWidth, shapecomponent.initialHeight)
                    for mat in reversed(shapecomponent.matScaleRotation):
                        dimens = mat.scaler.scale(dimens)

                    cssdecls['left'] = mm(doc.SHWPUNIT(offset[0]))
                    cssdecls['top'] = mm(doc.SHWPUNIT(offset[1]))
                    cssdecls['width'] = mm(doc.SHWPUNIT(dimens[0]))
                    cssdecls['height'] = mm(doc.SHWPUNIT(dimens[1]))

                    div.set('style', unicode(cssdecls))
                    cmt = ET.Comment(repr(shapecomponent))
                    div.append(cmt)
                    cmt = ET.Comment(repr(shapecomponent.shape))
                    div.append(cmt)
                div.text = ' '
                for paragraph in shapecomponent.paragraphs:
                    p = self.makeP(doc, paragraph)
                    div.append(p)
                return div

    def makeTree(self, doc):
        doc = Document(doc, destination=self.destination)
        for section in doc.model.sections:
            section = Section(doc, section)
            for page_paragraphs in hwp50.getPagedParagraphs(section.model.paragraphs):
                page = Page(doc, section.model.sectionDef.pages[0])
                page.addParagraphs(page_paragraphs)
                section.addPage(page)
            for html in section.etree():
                doc.body.append(html)
        return doc.etree()

    def convert(self, doc, destination=LocalDestination):
        self.destination = destination

        tree = self.makeTree(doc)
        indent_xml(tree.getroot(), 0)
        # TODO: use xhtml and remove dummy \xa0 characters
        self.destination.htmlfile.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
        tree.write(self.destination.htmlfile, 'utf-8')
        self.destination.close()

def main():
    import os.path
    hwpfilename = sys.argv[1].decode(sys.getfilesystemencoding())
    doc = hwp50.Document(hwpfilename)
    logging.info(doc.header.version)
    import os.path
    rootname = os.path.splitext(os.path.basename(hwpfilename))[0]

    cvt = HtmlConverter()
    cvt.convert(doc, LocalDestination(rootname))
if __name__ == '__main__':
    main()
