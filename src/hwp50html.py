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
        p.tail = '\n' + indent*level

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
        import zipfile, StringIO
        self._zf = zipfile.ZipFile(rootname+'.zip', 'w', zipfile.ZIP_DEFLATED)
        self.htmlfile = StringIO.StringIO()
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
    def parse(cls, s):
        decls = s.split(';')
        decls = []
        for decl in s.split(';'):
            decl = decl.strip()
            decl = decl.split(':', 1)
            if len(decl) == 2:
                decls.append(decl)
        return cls(decls)
    parse = classmethod(parse)

class CssRule:
    def __init__(self):
        self.selectors = []
        self.props = CssDecls()
    def getdecls(self):
        return unicode(self.props)

    def __unicode__(self):
        return (u', '.join(self.selectors) + ' { \n'+self.getdecls().replace('; ', ';\n')+'\n}\n')

class HtmlConverter:
    destination = None
    def __init__(self):
        self.styles = {}
    def makeCssPropsFromCharShape(self, charShape):
        fonts = self.doc.docinfo.mappings[self.doc.FaceName]
        props = {}
        props['color'] = str(charShape.textColor)
        props['font-family'] = ', '.join([ fonts[face_id].fontName for face_id in charShape.langFontFace ])
        props['font-size'] = pt(self.doc.HWPUNIT(charShape.basesize))
        if charShape.attr & charShape.BOLD:
            props['font-weight'] = 'bold'
        else:
            props['font-weight'] = 'normal'
        if charShape.attr & charShape.ITALIC:
            props['font-style'] = 'italic'
        else:
            props['font-style'] = 'normal'

        SHWPUNIT = self.doc.SHWPUNIT
        letterSpacing = 0.0

        widthExp = (charShape.langLetterWidthExpansion[0] - 100) / 100.0
        letterSpacing = letterSpacing + charShape.basesize * widthExp
        letterSpacePercent = charShape.langLetterSpacing[0]
        letterSpacing = letterSpacing + charShape.basesize * (letterSpacePercent / 100.0)
        props['letter-spacing'] = pt(SHWPUNIT(letterSpacing))
        return props

    def makeCssPropsFromParaShape(self, paraShape):
        props = {}

        props['text-indent'] = pt(self.doc.SHWPUNIT(paraShape.indent/2))
        margin = [self.doc.SHWPUNIT(x/2) for x in [paraShape.marginTop, paraShape.marginRight, paraShape.marginBottom, paraShape.marginLeft]]
        # NOTE: difference between hwp indent and css text-indent
        # when indent value is less than 0,
        #   - paraShape.indent is applied to following lines, not beginning line
        #   - css text-indent is applied to beginning line
        if paraShape.indent.pt < 0:
            margin[-1] = self.doc.SHWPUNIT(margin[-1] - (paraShape.indent / 2))
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

    def makeCssBorder(self, borders):
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

    def makeCssBackground(self, doc, fill):
        style = {}
        if isinstance(fill, doc.FillColorPattern):
            style['background-color'] = str(fill.backgroundColor)
        return style

    def makeTD(self, doc, cell):
        attrs = {}
        if cell.colspan > 1:
            attrs['colspan'] = str(cell.colspan)
        if cell.rowspan > 1:
            attrs['rowspan'] = str(cell.rowspan)
        valign = {cell.VALIGN_TOP:'top', cell.VALIGN_MIDDLE:'middle', cell.VALIGN_BOTTOM:'bottom'}.get(cell.listflags & cell.VALIGN_MASK, None)
        if valign is not None:
            attrs['valign'] = valign
        style = self.makeCssBorder(cell.borderFill.border)
        style.update(self.makeCssBackground(doc, cell.borderFill.fill))
        style['padding'] = compact_cssdir(cssdir([mm(x) for x in cell.padding]))
        style['width'] = mm(cell.width)
        style['height'] = mm(cell.height)
        attrs['style'] = '; '.join(['%s:%s'%(k,v) for k, v in style.iteritems()])

        return ET.Element('td', attrs)

    def makeTable(self, doc, table):
        attrs = {}
        attrs['cellspacing'] = px(table.body.cellspacing)

        style = {}
        style.update( self.makeCssBorder(table.borderFill.border) )
        if table.body.cellspacing == 0:
            style['border-collapse'] = 'collapse'
        style['width'] = mm(table.width)
        style['height'] = mm(table.height)
        style['margin'] = compact_cssdir(cssdir([mm(x) for x in table.margin]))
        attrs['style'] = '; '.join(['%s:%s'%(k,v) for k, v in style.iteritems()])

        tbl = ET.Element('table', attrs)
        if table.caption is not None:
            caption = ET.SubElement(tbl, 'caption')
            for paragraph in table.caption.paragraphs:
                p = self.makeP(doc, paragraph)
                caption.append(p)
        row = -1
        for cell in table.body.cells:
            if cell.row > row:
                row = cell.row
                tr = ET.SubElement(tbl, 'tr')
            td = self.makeTD(doc, cell)
            tr.append(td)
            #print 'cell %d,%d'%(cell.row, cell.col)
            for paragraph in cell.paragraphs:
                #print '\tparagraph'
                p = self.makeP(doc, paragraph)
                td.append(p)
        return tbl

    def makeImg(self, doc, pic, cssdecls = CssDecls()):

        bindata = pic.pictureInfo.binData
        if self.destination is not None:
            src = self.destination.addAttachment(str(bindata.name), bindata.datastream.read())
        else:
            src = None

        attrs = {}
        if src is not None:
            attrs['src'] = src
        attrs['style'] = unicode(cssdecls)
        img = ET.Element('img', attrs)
        return img

    def makeP(self, doc, paragraph):
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
                    if e.type == e.extended:
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
                            x = self.handle_shapecomponent(e.control, e.control.shapecomponent)
                            p.append(x)
                            span = newSpan()
                            continue
                        else:
                            cmt = str(e)+'\n'+str(e.control)
                            if isinstance(e.control, doc.GShapeObject):
                                cmt += '\n'+str(e.control.shapecomponent)
                            cmt = ET.Comment(cmt)
                            span.append(cmt)
                            continue
                    if e.ch == '\t':
                        addText(span, e.ch)
                    else:
                        cmt = str(e)
                        if e.type == e.extended:
                            cmt += ' '
                            cmt += str(e.control)
                        cmt = ET.Comment(cmt)
                        span.append(cmt)
                else:
                    addText(span, str(e))
            if len(span) == 0 and span.text in [None, '', u'']:
                span.text = u'\xa0'
        if len(p) == 0:
            p.text = u'\xa0' # unicode nbsp
        return p
    def handle_shapecomponent(self, gso, shapecomponent):
        doc = self.doc
        if isinstance(shapecomponent, doc.ShapeContainer):
            #print 'controls', shapecomponent.controls
            div = ET.Element('div', {'class':'ShapeContainer', 'style':'position:relative'})
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
#                    cssdecls['position'] = 'absolute'
#                    cssdecls['top'] = mm(doc.SHWPUNIT(shapecomponent.shape.coords[0][1]))
#                    cssdecls['left'] = mm(doc.SHWPUNIT(shapecomponent.shape.coords[0][0]))
#                    cssdecls['width'] = mm(doc.SHWPUNIT(shapecomponent.shape.coords[1][0] - shapecomponent.shape.coords[0][0]))
#                    cssdecls['height'] = mm(doc.SHWPUNIT(shapecomponent.shape.coords[2][1] - shapecomponent.shape.coords[1][1]))
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
        self.doc = doc
        html = ET.Element('html')
        head = ET.SubElement(html, 'head')
        meta = ET.SubElement(head, 'meta', {'http-equiv':'Content-Type', 'content':'application/xhtml+xml; charset=utf-8'})
        meta = ET.SubElement(head, 'meta', {'name' : 'HWP File Format Version' , 'content':'.'.join([str(x) for x in doc.header.version]) })
        style = ET.SubElement(head, 'style', {'type':'text/css'})
        style.text = ''
        for s in doc.docinfo.mappings[doc.Style]:
            cssrule = CssRule()
            cssrule.props.update( self.makeCssPropsFromParaShape( doc.docinfo.mappings[doc.ParaShape][s.paragraphShapeId] ) )
            cssrule.props.update( self.makeCssPropsFromCharShape( doc.docinfo.mappings[doc.CharShape][s.characterShapeId] ) )
            if s.name != '':
                s_name = s.name
            else:
                s_name = 'Style %d'%s.id
            s_name = s_name.replace(' ', '-')
            self.styles[s] = s_name
            cssrule.selectors.append( '.%s'%(s_name) )
            style.text += unicode(cssrule)
        for charShape in doc.docinfo.mappings[doc.CharShape]:
            cssrule = CssRule()
            cssrule.selectors.append( '.CharShape-%d'%charShape.id )
            cssrule.props.update( self.makeCssPropsFromCharShape( charShape ) )
            style.text += unicode(cssrule)
        for paraShape in doc.docinfo.mappings[doc.ParaShape]:
            cssrule = CssRule()
            cssrule.selectors.append( '.ParaShape-%d'%paraShape.id )
            cssrule.props.update( self.makeCssPropsFromParaShape( paraShape ) )
            style.text += unicode(cssrule)
        style.text += '.Page { page-break-after: always; }'

        body = ET.SubElement(html, 'body', {'style':'background-color:#ccc'})
        for section in doc.sections:
            clss = ['Section']
            attrs = {'class':' '.join(clss)}

            pagedef = section.sectionDef.pages[0]
            divsect = ET.SubElement(body, 'div', attrs)
            divpage = None
            for page in section.pages:
                style = {}
                style['margin'] = '0 auto'
                page_offset = list(pagedef.offset)
                page_offset[2] = doc.HWPUNIT(page_offset[2] + pagedef.headerOffset)
                page_offset[3] = doc.HWPUNIT(page_offset[3] + pagedef.footerOffset)
                if pagedef.attr.landscape:
                    # TODO
                    pass
                else:
                    style['width'] = mm( doc.HWPUNIT(pagedef.width - page_offset[0] - page_offset[1]))
                    style['min-height'] = str(doc.HWPUNIT(pagedef.height - page_offset[2] - page_offset[3]).mm)+'mm'
                page_offset[2] = page_offset[2]
                page_offset[3] = page_offset[3]
                style['padding'] = compact_cssdir(cssdir( [mm(x) for x in page_offset] ))
                style['border'] = '1px solid black'
                style['background-color'] = 'white'

                attrs = {}
                attrs['class'] = 'Page'
                attrs['style'] = '; '.join( ['%s:%s'%(k,v) for k,v in style.iteritems()] )

                #if divpage is None:
                divpage = ET.SubElement(divsect, 'div', attrs)
                divpage.text = ' '
                for paragraph in page.paragraphs:
                    p = self.makeP(doc, paragraph)
                    divpage.append(p)
        return ET.ElementTree(html)
    def convert(self, doc, destination=LocalDestination):
        self.destination = destination

        tree = self.makeTree(doc)
        indent_xml(tree.getroot(), 0)
        self.destination.htmlfile.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
        tree.write(self.destination.htmlfile, 'utf-8')
        self.destination.close()

if __name__ == '__main__':
    import os.path
    hwpfilename = sys.argv[1].decode(sys.getfilesystemencoding())
    doc = hwp50.Document(hwpfilename)
    print doc.header.version
    import os.path
    rootname = os.path.splitext(os.path.basename(hwpfilename))[0]

    cvt = HtmlConverter()
    cvt.convert(doc, LocalDestination(rootname))
