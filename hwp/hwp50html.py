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
    margin = [doc.SHWPUNIT(x) for x in [paraShape.marginTop, paraShape.marginRight, paraShape.marginBottom, paraShape.marginLeft]]
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
    margin = [doc.SHWPUNIT(x) for x in [paraShape.marginTop, paraShape.marginRight, paraShape.marginBottom, paraShape.marginLeft]]
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
    def etree(self, *args, **kwargs):
        raise NotImplemented
    def __getattr__(self, name):
        return getattr(self.model, name)

class OffsetView(View):
    line_position = 'absolute'
    def __init__(self, *args, **kwargs):
        View.__init__(self, *args, **kwargs)
        self.offsetY = 0
        self.prev_line = None
    def addParagraph(self, paragraph):
        for html in paragraph.etree():
            self.html.append(html)

    def appendParagraph(self, paragraph, paragraph_lines):
        paragraph = Paragraph(self.doc, paragraph, offset=self, page=self.getPage())
        for line_number, (line, line_elements) in enumerate(paragraph_lines):
            if self.prev_line is not None:
                self.prev_line.enableLineSpacing()
            line = Line(self.doc, line, number_in_view=line_number, paragraph=paragraph, position=self.line_position)
            for element in line_elements:
                line.addElement(element)
            paragraph.addLine(line)
            self.prev_line = line
        self.addParagraph(paragraph)

    def addParagraphs(self, paragraphs):
        for paragraph, paragraph_lines in paragraphs:
            self.appendParagraph(paragraph, paragraph_lines)

    def getPage(self):
        return self.page

class Document:
    debug = False
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
        meta = ET.SubElement(head, 'meta', {'name' : 'HWP File Format Version' , 'content':'.'.join([str(x) for x in self.header.version]) })
        self.stylenames, cssrules = self.makeStyles(self.model)
        style_text = '@charset "utf-8"\n'
        style_text += ''.join([unicode(cssrule) for cssrule in cssrules])
        for charShape in self.docinfo.mappings[self.CharShape]:
            style_text += unicode(CssRule('.CharShape-%d'%charShape.id, makeCssPropsFromCharShape( self.model, charShape )))
        for paraShape in self.docinfo.mappings[self.ParaShape]:
            style_text += unicode(CssRule('.ParaShape-%d'%paraShape.id, makeCssPropsFromParaShape( self.model, paraShape )))
        style_text += unicode(CssRule('.Paper', {'page-break-after':'always', 'background-color':'white', 'overflow':'hidden'}))
        style_text += unicode(CssRule('.Page', {'position':'relative', 'background':'url(page-background.png) repeat'}))
        style_text += unicode(CssRule('.Line', {'position':'absolute', 'white-space':'nowrap'}))
        style_text += unicode(CssRule('.FootNoteRef', { 'vertical-align':'super' }))
        style_text += unicode(CssRule('body', { 'background-color':'#ccc'}))
        style = ET.SubElement(head, 'link', {'rel':'stylesheet', 'type':'text/css'})
        src = self.destination.addAttachment('styles.css', style_text.encode('utf-8'))
        style.attrib['href'] = src
        style.append(ET.Comment(' '))

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

    def __getattr__(self, name):
        return getattr(self.model, name)

class Section(View):
    def init(self):
        self.html = ET.Element('div', {'class':'Section'})

    def etree(self):
        if self.doc.debug: yield ET.Comment(repr(self.model))
        yield self.html

    def addPage(self, page):
        for html in page.etree():
            self.html.append(html)

class Paper(View):
    def init(self):
        self.html = html = ET.Element('div', {'class':'Paper'})
        html.styles['margin'] = '10pt auto'
        html.styles['width'] = mm( self.width )
        html.styles['min-height'] = mm ( self.height )
        page_offset = [ self.doc.HWPUNIT(self.offsetTop + self.offsetHeader), self.offsetRight, self.doc.HWPUNIT(self.offsetBottom + self.offsetFooter), self.offsetLeft ]
        html.styles['padding'] = compact_cssdir( [mm(x) for x in page_offset] )
        html.styles['border'] = '1px solid black'
    def etree(self):
        yield self.html

class Page(OffsetView):
    def init(self):
        self.paper = Paper(self.doc, self.model)
        self.html = ET.SubElement(self.paper.html, 'div', {'class':'Page'})
        self.html.styles['width'] = mm ( self.width )
        self.html.styles['min-height'] = mm( self.height )
        self.footnotes = []
        self.footnotes_view = None

    def getPage(self):
        return self

    def etree(self):
        if len(self.footnotes) > 0:
            if self.footnotes_view is None:
                self.footnotes_view = FootNotes(self.doc, None, page=self)
                for html in self.footnotes_view.etree():
                    self.html.append(html)
            for fn in self.footnotes:
                for fn_paragraphs in hwp50.getPagedParagraphs(fn.listhead.paragraphs):
                    self.footnotes_view.addParagraphs(fn_paragraphs)
            self.footnotes = []

        if len(self.html) == 0 and (self.html.text == None or len(self.html.text) == 0):
            self.html.text = u'\xa0'
        return self.paper.etree()

    def addFootNote(self, fn):
        self.footnotes.append(fn)

class Paragraph(View):
    def init(self):
        self.childviews = []
        SHWPUNIT = self.doc.SHWPUNIT
        paraShapeId = self.paragraphShapeId
        self.shape = self.doc.docinfo.mappings[self.doc.ParaShape][paraShapeId]
        self.text_indent = SHWPUNIT(self.shape.indent/2)

    def etree(self):
        self.html = ET.Element('div', {'class':'Paragraph'})

        paragraph_stylename = self.doc.stylenames.get(self.style, None)
        if paragraph_stylename is None:
            logging.warning('self.model style is missing')
            self.html.classes.append('ParaShape-%d'%self.style.paragraphShapeId)
            self.html.classes.append('CharShape-%d'%self.style.characterShapeId)
        else:
            self.html.classes.append(paragraph_stylename)
        if self.style.paragraphShapeId != self.paragraphShapeId:
            self.html.classes.append('ParaShape-%d'%self.paragraphShapeId)

        for child in self.childviews:
            for html in child.etree():
                self.html.append(html)

        if len(self.html) == 0 and (self.html.text == None or len(self.html.text) == 0):
            self.html.text = u'\xa0'
        if self.doc.debug: yield ET.Comment('Record #%d'%self.record.seqno)
        if self.doc.debug: yield ET.Comment(repr(self.model))
        if self.doc.debug: yield ET.Comment('left-margin: %s, text-indent: %s'%(pt(self.shape.marginLeft), pt(self.text_indent)))
        yield self.html

    def addLine(self, line):
        self.childviews.append(line)

    def buildTableTree(self, table):
        table = Table(self.doc, table)
        if table.caption is not None:
            caption = TableCaption(self.doc, table.caption, page=self.page)
            for paragraphs in hwp50.getPagedParagraphs(caption.paragraphs):
                caption.addParagraphs(paragraphs)
            table.addCaption(caption)
        for row_number, row_cells in table.getRows():
            tr = TableRow(self.doc, row_number)
            for cell in row_cells:
                cell = TableCell(self.doc, cell, page=self.page)
                for paragraphs in hwp50.getPagedParagraphs(cell.paragraphs):
                    cell.addParagraphs(paragraphs)
                tr.addCell(cell)
            table.addRow(tr)
        return table

    def addControl(self, line, control, viewobj):
        SHWPUNIT = self.doc.SHWPUNIT
        styles = CssDecls()
        styles['width'] = mm(control.width)
        styles['height'] = mm(control.height)
        assert(not control.flags.inline)
        styles['display'] = 'block'
        if control.flags.flow == control.Flow.FLOAT: # 본문과의 배치: 어울림
            # float
            if control.flags.textSide == control.TextSide.LEFT:
                styles['float'] = 'right'
                if control.flags.horzAlign == control.HorzAlign.RIGHT:
                    styles['margin-right'] = mm(control.offsetX)
                elif control.flags.horzAlign == control.HorzAlign.LEFT:
                    #TODO styles['margin-right'] = mm(doc.SHWPUNIT( page_width - control.width - control.offsetX ))
                    pass
            elif control.flags.textSide == control.TextSide.RIGHT:
                styles['float'] = 'left'
                if control.flags.horzAlign == control.HorzAlign.LEFT:
                    styles['margin-left'] = mm(control.offsetX)
                elif control.flags.horzAlign == control.HorzAlign.RIGHT:
                    #TODO styles['margin-left'] = mm(doc.SHWPUNIT( page_width - control.width - control.offsetX ))
                    pass
            elif control.flags.textSide == control.TextSide.BOTH:
                logging.warning('unsupported <본문 위치>: 양쪽')
                styles['position'] = 'absolute'
                if control.flags.horzAlign == control.HorzAlign.LEFT:
                    styles['left'] = mm(control.offsetX)
                elif control.flags.horzAlign == control.HorzAlign.CENTER:
                    styles['left'] = mm(control.offsetX) # TODO: + (50% of container)
                elif control.flags.horzAlign == control.HorzAlign.RIGHT:
                    styles['right'] = mm(control.offsetX)
            elif control.flags.textSide == control.TextSide.LARGER:
                logging.warning('unsupported <본문 위치>: 큰 쪽')
                pass
        elif control.flags.flow == control.Flow.BLOCK: # 본문과의 배치: 자리차지
            styles['position'] = 'absolute'

            if control.flags.horzAlign == control.HorzAlign.LEFT:
                if control.flags.horzRelTo == control.HorzRelTo.PAPER:
                    control_offset = control.offsetX - (self.page.offsetLeft)
                elif control.flags.horzRelTo == control.HorzRelTo.PAGE:
                    control_offset = control.offsetX
                elif control.flags.horzRelTo == control.HorzRelTo.PARAGRAPH:
                    control_offset = control.offsetX + self.shape.marginLeft
                else:
                    # TODO: COLUMN
                    control_offset = control.offsetX
                styles['left'] = mm(SHWPUNIT(control.margin[control.MARGIN_LEFT] + control_offset))
            elif control.flags.horzAlign == control.HorzAlign.RIGHT:
                if control.flags.horzRelTo == control.HorzRelTo.PAPER:
                    control_offset = control.offsetX - (self.page.offsetRight)
                elif control.flags.horzRelTo == control.HorzRelTo.PAGE:
                    control_offset = control.offsetX
                elif control.flags.horzRelTo == control.HorzRelTo.PARAGRAPH:
                    control_offset = control.offsetX + self.shape.marginRight
                else:
                    # TODO: COLUMN
                    control_offset = control.offsetX
                styles['right'] = mm(SHWPUNIT(control.margin[control.MARGIN_RIGHT] + control_offset))
            elif control.flags.horzAlign == control.HorzAlign.CENTER:
                x = SHWPUNIT((self.page.width - control.width)/2 + control.offsetX)
                # TODO: margin
                styles['left'] = mm(x)
            else:
                logging.warning('TODO: handle horzAlign: %d'%control.flags.horzAlign)
                styles['left'] = '0'
            
            if control.flags.vertRelTo == control.VertRelTo.PARAGRAPH:
                # hwp 2005(5.0.1.7) forces VERT_ALIGN to TOP when VERT_RELTO_PARAGRAPH
                y = line.offsetY + control.offsetY + control.margin[control.MARGIN_TOP]
                if y + control.height > self.page.height and control.flags.restrictedInPage:
                    y -= control.height
                styles['top'] = mm(SHWPUNIT(y))
            else:
                # VERT_RELTO_PAPER, VERT_RELTO_PAGE
                if control.flags.vertAlign == control.VertAlign.TOP:
                    if control.flags.vertRelTo == control.VertRelTo.PAPER:
                        control_offset = control.offsetY - (self.page.offsetTop + self.page.offsetHeader)
                    else:
                        control_offset = control.offsetY
                    styles['top'] = mm(SHWPUNIT(control_offset + control.margin[control.MARGIN_TOP]))
                elif control.flags.vertAlign == control.VertAlign.BOTTOM:
                    if control.flags.vertRelTo == control.VertRelTo.PAPER:
                        control_offset = control.offsetY - (self.page.offsetBottom + self.page.offsetFooter)
                    else:
                        control_offset = control.offsetY
                    styles['bottom'] = mm(SHWPUNIT(control_offset + control.margin[control.MARGIN_BOTTOM]))
                elif control.flags.vertAlign == control.VertAlign.CENTER:
                    y = (self.page.height - control.height)/2 + control.offsetY
                    # TODO: margin
                    styles['top'] = mm(SHWPUNIT(y))
                else:
                    logging.warning('TODO: handle vertAlign: %d'%control.flags.vertAlign)
                    styles['top'] = '0'

        elif control.flags.flow == control.Flow.BACK: # 본문과의 배치: 글 뒤로
            logging.warning('TODO: handle flow: FLOW_BACK')
        elif control.flags.flow == control.Flow.FRONT: # 본문과의 배치: 글 앞으로
            logging.warning('TODO: handle flow: FLOW_FRONT')
        viewobj.html.attrib['style'] = unicode(styles)
        self.childviews.append(viewobj)

class ElementContainerView(View):
    def addText(self, text, charShapeId):
        if self.paragraph.style.characterShapeId == charShapeId:
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
    def addHtml(self, html):
        self.html.append(html)
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
    def addField(self, field):
        for html in field.etree():
            self.html.append(html)
    def addFootNoteRef(self, fn):
        atno = fn.getAutoNumber()
        html = ET.Element('span', {'class':'FootNoteRef'})
        html.text = unicode(atno)
        self.addHtml(html)

class Line(ElementContainerView):
    def init(self):
        self.stack = [self]
        self.html = ET.Element('div', {'class':'Line'})
        html = self.html

        styles = CssDecls()
        styles['position'] = self.position
        if self.position == 'absolute':
            self.x = self.paragraph.shape.marginLeft
            if self.paragraph.text_indent >= 0:
                if self.number_in_paragraph == 0:
                    self.x += self.paragraph.text_indent
            else:
                if self.number_in_paragraph != 0:
                    self.x -= self.paragraph.text_indent
            self.x = self.doc.SHWPUNIT(self.x)

            styles['top'] = mm(self.offsetY)
            styles['left'] = pt(self.x)
            styles['width'] = mm(self.doc.HWPUNIT(self.a5[0]))
            styles['height'] = pt(self.height)
        elif self.position == 'static':
            self.x = 0
            if self.paragraph.text_indent >= 0:
                if self.number_in_paragraph == 0:
                    self.x += self.paragraph.text_indent
            else:
                if self.number_in_paragraph != 0:
                    self.x -= self.paragraph.text_indent
            self.x = self.doc.SHWPUNIT(self.x)
            styles['margin-left'] = mm(self.x)
        styles['line-height'] = pt(self.height)
        html.attrib['style'] = unicode(styles)
    def enableLineSpacing(self):
        self.html.styles['margin-bottom'] = pt(self.marginBottom)
    def etree(self):
        if len(self.html) == 0 and (self.html.text == None or len(self.html.text) == 0):
            self.html.text = u'\xa0'
        if self.doc.debug: yield ET.Comment(repr(self.model))
        if self.doc.debug: yield ET.Comment('#%s in paragraph, #%s in view, x = %s' % (self.number_in_paragraph, self.number_in_view, pt(self.x)))
        yield self.html
    def addElement(self, elem):
        if isinstance(elem, self.doc.Text):
            self.stack[-1].addText(unicode(elem).replace(u' ', u'\xa0'), elem.charShapeId)
        elif isinstance(elem, self.doc.ControlChar):
            if elem.kind == elem.char:
                self.stack[-1].addControlChar(elem)
            elif elem.kind == elem.inline:
                self.addInlineChar(elem)
            else:
                self.addExtendedControl(elem)
        else:
            assert(False)
            self.addComment(elem)
    def addInlineChar(self, e):
        if e.ch == e.TAB:
            self.stack[-1].addText(e.ch, e.charShapeId)
        elif e.ch == e.FIELD_END:
            field = self.stack.pop()
            self.stack[-1].addField(field)
        else:
            self.addComment(e)
    def addExtendedControl(self, e):
        if isinstance(e.control, self.doc.Table):
            table = e.control
            tableobj = self.paragraph.buildTableTree(table)
            if table.flags.inline:
                for html in tableobj.etree():
                    self.stack[-1].addHtml(html)
            else:
                self.paragraph.addControl(self, table, tableobj)
        elif isinstance(e.control, self.doc.AutoNumbering):
            self.stack[-1].addComment(e.control)
            self.stack[-1].addText(unicode(e.control), e.charShapeId)
        elif e.ch == e.FIELD_START:
            if isinstance(e.control, self.doc.FieldHyperLink):
                field = FieldHyperLink(self.doc, e.control, paragraph=self.paragraph)
                self.stack.append(field)
            else:
                field = Field(self.doc, e.control, paragraph=self.paragraph)
                self.stack.append(field)
        elif e.ch == e.BOOKMARK:
            bookmark = ET.Element('a')
            bookmark.attrib['name'] = e.control.data.name
            self.stack[-1].addHtml(bookmark)
        elif e.ch == e.FOOT_END_NOTE:
            if isinstance(e.control, self.doc.FootNote):
                fn = e.control
                self.stack[-1].addFootNoteRef(fn)
                self.paragraph.page.addFootNote(fn)
            else:
                self.stack[-1].addComment(e)
        elif isinstance(e.control, self.doc.GShapeObject)\
                and isinstance(e.control.shapecomponent, self.doc.ShapeComponent)\
                and isinstance(e.control.shapecomponent.shape, self.doc.ShapePicture):
            gso = e.control
            img = Image(self.doc, gso.shapecomponent.shape)
            if gso.flags.inline:
                for html in img.etree():
                    self.stack[-1].addHtml(html)
            else:
                self.paragraph.addControl(self, gso, img)
        elif isinstance(e.control, self.doc.GShapeObject):
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

class Field(ElementContainerView):
    def init(self):
        self.html = ET.Element('span', {'class':'Field'})
    def etree(self):
        yield ET.Comment(repr(self.model))
        yield self.html

class FieldHyperLink(Field):
    def init(self):
        self.html = ET.Element('a')
        url = self.geturl()
        if len(url) == 0:
            url = '#'
        if url[0] == '?':
            url = '#' + url[1:]
        self.html.attrib['href'] = url

class Image(View):
    def init(self):
        self.html = html = ET.Element('img')
        bindata = self.pictureInfo.binData
        if bindata.type == self.doc.BinEmbedded:
            if self.doc.destination is not None:
                html.attrib['src'] = self.doc.destination.addAttachment(str(bindata.name), bindata.datastream.read())
    def etree(self):
        if self.doc.debug: yield ET.Comment(repr(self.model))
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

        if self.colspan > 1:
            self.html.attrib['colspan'] = str(self.colspan)
        if self.rowspan > 1:
            self.html.attrib['rowspan'] = str(self.rowspan)

        valign = {
                self.VALIGN_TOP:'top',
                self.VALIGN_MIDDLE:'middle',
                self.VALIGN_BOTTOM:'bottom'
                }.get(self.listflags & self.VALIGN_MASK, None)
        if valign is not None:
            self.html.attrib['valign'] = valign

        style = makeCssBorder(self.borderFill.border)
        style.update(makeCssBackground(self.doc.model, self.borderFill.fill))
        self.html.attrib['style'] = unicode(CssDecls(style))

        self.html.styles['padding'] = compact_cssdir(
                cssdir([mm(x) for x in self.padding]))

        self.html.styles['width'] = mm(self.width)
        self.html.styles['height'] = pt(self.height)
    def etree(self):
        if len(self.html) == 0 and (self.html.text is None or len(self.html.text)):
            self.html.text = u'\xa0'
        if self.doc.debug: yield ET.Comment(repr(self.model))
        yield self.html

class TableCaption(OffsetView):
    line_position = 'static'
    def init(self):
        self.html = ET.Element('div', {'class':'TableCaption'})
        self.html.styles['width'] = mm(self.width)
        if self.captflags.position == self.POS_BOTTOM:
            self.html.styles['margin-top'] = mm(self.offset)
        elif self.captflags.position == self.POS_TOP:
            self.html.styles['margin-bottom'] = mm(self.offset)
        else:
            logging.warning('TODO: implement TableCaption position: POS_LEFT / POS_RIGHT')
    def etree(self):
        if self.doc.debug: yield ET.Comment(repr(self.model))
        yield self.html

class Table(View):
    def init(self):
        self.html = ET.Element('div')

        self.table_html = ET.SubElement(self.html, 'table')
        self.table_html.attrib['cellspacing'] = unicode(self.body.cellspacing.px)
        self.table_html.append(ET.Comment(' '))

        style = {}
        style.update( makeCssBorder(self.borderFill.border) )
        if self.body.cellspacing == 0:
            style['border-collapse'] = 'collapse'
        #style['width'] = mm(self.width)
        #style['height'] = mm(self.height)
        #style['margin'] = compact_cssdir(cssdir([mm(x) for x in self.margin]))
        self.table_html.attrib['style'] = unicode(CssDecls(style))

    def addCaption(self, caption):
        if caption.captflags.position == self.caption.POS_TOP:
            for i, html in enumerate(caption.etree()):
                self.html.insert(i, html)
        else:
            for html in caption.etree():
                self.html.append(html)
    def addRow(self, row):
        for html in row.etree():
            self.table_html.append(html)
    def etree(self):
        if self.doc.debug: yield ET.Comment(repr(self.model))
        yield self.html

class FootNotes(OffsetView):
    line_position = 'static'
    def init(self):
        self.html = html = ET.Element('div', {'class':'FootNotes'})
        html.styles['position'] = 'absolute'
        html.styles['bottom'] = '0'
        html.styles['border-top'] = '1px solid black'
        html.styles['padding-top'] = '.5em'
    def etree(self):
        if len(self.html) == 0 and (self.html.text is None or len(self.html.text)):
            self.html.text = u'\xa0'
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
                        elif isinstance(e.control, doc.AutoNumbering):
                            addText(span, str(e.control))
                            continue
                        elif isinstance(e.control, doc.FieldHyperlink):
                            pass
                        elif isinstance(e.control, doc.GShapeObject) and isinstance(e.control.shapecomponent, doc.ShapeComponent) and isinstance(e.control.shapecomponent.shape, doc.ShapePicture):
                            gso = e.control
                            cssdecls = CssDecls()
                            cssdecls['width'] = mm(gso.width)
                            wrapdiv = None
                            if not gso.flags.inline:
                                cssdecls['display'] = 'block'
                                if gso.flags.flow == gso.Flow.FLOAT: # 본문과의 배치: 어울림
                                    # float
                                    if gso.flags.textSide == gso.TextSide.LEFT:
                                        cssdecls['float'] = 'right'
                                        if gso.flags.horzAlign == gso.HorzAlign.RIGHT:
                                            cssdecls['margin-right'] = mm(gso.offsetX)
                                        elif gso.flags.horzAlign == gso.HorzAlign.LEFT:
                                            #TODO cssdecls['margin-right'] = mm(doc.SHWPUNIT( page_width - gso.width - gso.offsetX ))
                                            pass
                                    elif gso.flags.textSide == gso.TextSide.RIGHT:
                                        cssdecls['float'] = 'left'
                                        if gso.flags.horzAlign == gso.HorzAlign.LEFT:
                                            cssdecls['margin-left'] = mm(gso.offsetX)
                                        elif gso.flags.horzAlign == gso.HorzAlign.RIGHT:
                                            #TODO cssdecls['margin-left'] = mm(doc.SHWPUNIT( page_width - gso.width - gso.offsetX ))
                                            pass
                                    elif gso.flags.textSide == gso.TextSide.BOTH:
                                        logging.warning('unsupported <본문 위치>: 양쪽')
                                        cssdecls['position'] = 'absolute'
                                        if gso.flags.horzAlign == gso.HorzAlign.LEFT:
                                            cssdecls['left'] = mm(gso.offsetX)
                                        elif gso.flags.horzAlign == gso.HorzAlign.CENTER:
                                            cssdecls['left'] = mm(gso.offsetX) # TODO: + (50% of container)
                                        elif gso.flags.horzAlign == gso.HorzAlign.RIGHT:
                                            cssdecls['right'] = mm(gso.offsetX)
                                    elif gso.flags.textSide == gso.TextSide.LARGER:
                                        logging.warning('unsupported <본문 위치>: 큰 쪽')
                                        pass
                                elif gso.flags.flow == gso.Flow.BLOCK: # 본문과의 배치: 자리차지
                                    cssdecls['position'] = 'relative'
                                    if gso.flags.horzAlign == gso.HorzAlign.LEFT:
                                        cssdecls['left'] = mm(gso.offsetX)
                                    elif gso.flags.horzAlign == gso.HorzAlign.CENTER:
                                        cssdecls['margin'] = 'auto'
                                        cssdecls['left'] = mm(gso.offsetX)
                                    elif gso.flags.horzAlign == gso.HorzAlign.RIGHT:
                                        cssdecls['right'] = mm(gso.offsetX)
                                        cssdecls['position'] = 'absolute'
                                        wrapdiv = ET.Element('div', {'style':'height:'+mm(gso.height)})
                                elif gso.flags.flow == gso.Flow.BACK: # 본문과의 배치: 글 뒤로
                                    pass
                                elif gso.flags.flow == gso.Flow.FRONT: # 본문과의 배치: 글 앞으로
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
        for section in doc.sections:
            section = Section(doc, section)
            for page_paragraphs in hwp50.getPagedParagraphs(section.paragraphs):
                page = Page(doc, section.sectionDef.pages[0])
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

    Document.debug = True
    cvt = HtmlConverter()
    cvt.convert(doc, LocalDestination(rootname))
if __name__ == '__main__':
    main()
