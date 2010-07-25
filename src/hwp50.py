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
import OleFileIO_PL as olefileio
import zlib
import os.path
import StringIO

import dataio
from dataio import *
import logging

selfref = dataio.ctx_based

# DIFFSPEC : Difference with the specification

def decode_rechdr(f):
    try:
        # TagID, Level, Size
        rechdr = UINT32.decode(f)
        tagid = rechdr & 0x3ff
        level = (rechdr >> 10) & 0x3ff
        size = (rechdr >> 20) & 0xfff
        if size == 0xfff:
            size = UINT32.decode(f)
        return (tagid, level, size)
    except Eof:
        return None

class Record:
    def decode(cls, f):
        rechdr = decode_rechdr(f)
        if rechdr is None:
            return None
        rec = cls()
        rec.rechdr = rechdr
        rec.tagid, rec.level, rec.size = rechdr
        rec.data = dataio.readn(f, rec.size)
        return rec
    decode = classmethod(decode)

    def __getattr__(self, name):
        if name == 'datastream':
            return StringIO.StringIO(self.data)
        raise AttributeError(name)

    def __repr__(self):
        import base64
        data = base64.b16encode(self.data)
        return '<Record tagid="0x%x" level="%d" size="%d">%s</Record>'%(self.tagid, self.level, self.size, data)

def getRecords(f):
    i = 0
    while True:
        rec = Record.decode(f)
        if rec is None:
            return
        rec.seqno = i
        yield rec
        i = i + 1

STARTREC = 0
CONTENT = 1
ENDREC = 2
def pullparse(f):
    stack = []
    while True:
        rechdr = decode_rechdr(f)
        if rechdr is None:
            break
        tagid, level, size = rechdr
        data = dataio.readn(f, size)

        while level < len(stack):
            yield ENDREC, stack.pop()
        while len(stack) < level:
            stack.append((None, None))
            yield STARTREC, (None, None)
        assert(len(stack) == level)

        stack.append((tagid, data))
        yield STARTREC, (tagid, data)

    while 0 < len(stack):
        yield ENDREC, stack.pop()

def pullparse_lighter(f):
    stack = []
    while True:
        rechdr = decode_rechdr(f)
        if rechdr is None:
            break
        tagid, level, size = rechdr

        while level < len(stack):
            yield ENDREC, stack.pop()
        while len(stack) < level:
            stack.append(None)
            yield STARTREC, None
        assert(len(stack) == level)

        stack.append(tagid)
        yield STARTREC, tagid
        yield CONTENT, dataio.readn(f, size)

    while 0 < len(stack):
        yield ENDREC, stack.pop()

def pullparseRecord(records):
    stack = []
    for rec in records:
        while rec.level < len(stack):
            yield ENDREC, stack.pop()
        while len(stack) < rec.level:
            dummyrec = Record()
            dummyrec.level = len(stack)
            dummyrec.data = ''
            stack.append(dummyrec)
            yield STARTREC, dummyrec
        assert(len(stack) == rec.level)
        stack.append(rec)
        yield STARTREC, rec
    while 0 < len(stack):
        yield ENDREC, stack.pop()

HWPTAG_BEGIN = 0x010
# DocInfo Records
tagnames = {
    HWPTAG_BEGIN + 0 : 'HWPTAG_DOCUMENT_PROPERTIES',
    HWPTAG_BEGIN + 1 : 'HWPTAG_ID_MAPPINGS',
    HWPTAG_BEGIN + 2 : 'HWPTAG_BIN_DATA',
    HWPTAG_BEGIN + 3 : 'HWPTAG_FACE_NAME',
    HWPTAG_BEGIN + 4 : 'HWPTAG_BORDER_FILL',
    HWPTAG_BEGIN + 5 : 'HWPTAG_CHAR_SHAPE',
    HWPTAG_BEGIN + 6 : 'HWPTAG_TAB_DEF',
    HWPTAG_BEGIN + 7 : 'HWPTAG_NUMBERING',
    HWPTAG_BEGIN + 8 : 'HWPTAG_BULLET',
    HWPTAG_BEGIN + 9 : 'HWPTAG_PARA_SHAPE',
    HWPTAG_BEGIN + 10 : 'HWPTAG_STYLE',
    HWPTAG_BEGIN + 11 : 'HWPTAG_DOC_DATA',
    HWPTAG_BEGIN + 12 : 'HWPTAG_DISTRIBUTE_DOC_DATA',
    # HWPTAG_BEGIN + 13 : RESERVED,
    HWPTAG_BEGIN + 14 : 'HWPTAG_COMPATIBILITY_DOCUMENT',
    HWPTAG_BEGIN + 15 : 'HWPTAG_LAYOUT_COMPATIBILITY',
    # Section Records
    HWPTAG_BEGIN + 50 : 'HWPTAG_PARA_HEADER',
    HWPTAG_BEGIN + 51 : 'HWPTAG_PARA_TEXT',
    HWPTAG_BEGIN + 52 : 'HWPTAG_PARA_CHAR_SHAPE',
    HWPTAG_BEGIN + 53 : 'HWPTAG_PARA_LINE_SEG',
    HWPTAG_BEGIN + 54 : 'HWPTAG_PARA_RANGE_TAG',
    HWPTAG_BEGIN + 55 : 'HWPTAG_CTRL_HEADER',
    HWPTAG_BEGIN + 56 : 'HWPTAG_LIST_HEADER',
    HWPTAG_BEGIN + 57 : 'HWPTAG_PAGE_DEF',
    HWPTAG_BEGIN + 58 : 'HWPTAG_FOONOTE_SHAPE',
    HWPTAG_BEGIN + 59 : 'HWPTAG_PAGE_BORDER_FILL',
    HWPTAG_BEGIN + 60 : 'HWPTAG_SHAPE_COMPONENT',
    HWPTAG_BEGIN + 61 : 'HWPTAG_TABLE',
    HWPTAG_BEGIN + 62 : 'HWPTAG_SHAPE_COMPONENT_LINE',
    HWPTAG_BEGIN + 63 : 'HWPTAG_SHAPE_COMPONENT_RECTANGLE',
    HWPTAG_BEGIN + 64 : 'HWPTAG_SHAPE_COMPONENT_ELLIPSE',
    HWPTAG_BEGIN + 65 : 'HWPTAG_SHAPE_COMPONENT_ARC',
    HWPTAG_BEGIN + 66 : 'HWPTAG_SHAPE_COMPONENT_POLYGON',
    HWPTAG_BEGIN + 67 : 'HWPTAG_SHAPE_COMPONENT_CURVE',
    HWPTAG_BEGIN + 68 : 'HWPTAG_SHAPE_COMPONENT_OLE',
    HWPTAG_BEGIN + 69 : 'HWPTAG_SHAPE_COMPONENT_PICTURE',
    HWPTAG_BEGIN + 70 : 'HWPTAG_SHAPE_COMPONENT_CONTAINER',
    HWPTAG_BEGIN + 71 : 'HWPTAB_CTRL_DATA',
    HWPTAG_BEGIN + 72 : 'HWPTAB_CTRL_EQEDIT',
    # HWPTAG_BEGIN + 73 : RESERVED
    # ...
    HWPTAG_BEGIN + 78 : 'HWPTAG_FORBIDDEN_CHAR',
}
for k, v in tagnames.iteritems():
    globals()[v] = k
del k, v

class DummyContext:
    def __init__(self, tagid):
        self.tagid = tagid
    def getSubModeler(self, tagid):
        pass
def buildModelTree(root, records):
    stack = []
    for evt, rec in pullparseRecord(records):
        if evt == STARTREC:
            getSubModeler = getattr(root, 'getSubModeler', None)
            if getSubModeler is not None:
                modeler = getSubModeler(rec.tagid)
            else:
                modeler = None
            if modeler is not None:
                decoder, setter = modeler
                try:
                    model = dataio.decodeModel(decoder, rec.datastream)
                except:
                    logging.error( 'failed to decode a Record(#%d): %s'%(rec.seqno, str(decoder)) + ':\n' + '\t'+dataio.hexdump(rec.data).replace('\n', '\n\t') + '\n')
                    #raise
                if not isinstance(model, unicode) and not isinstance(model, str) and not isinstance(model, dict) and not isinstance(model, list):
                    model.recidx = rec.seqno
            else:
                sss = ['']
                k = 0
                for r, s in stack:
                    sss.append('....'*k + str(r.__class__))
                    k += 1
                if isinstance(root, DummyContext):
                    rc = 'Dummy( %s %x +%d )'%(tagnames.get(root.tagid, ''), root.tagid, root.tagid - HWPTAG_BEGIN)
                else:
                    rc = str(root.__class__)
                sss.append('....'*k + rc)
                sss = '\n'.join(sss)
                logging.warning('%s: ignoring unrecognized tagid: %s 0x%x (+%d)'%(sss, tagnames.get(rec.tagid, ''), rec.tagid, rec.tagid - HWPTAG_BEGIN))
                model = DummyContext(rec.tagid)
                setter = None

            stack.append((root, setter))
            root = model
        elif evt == ENDREC:
            model = root
            root, setter = stack.pop()
            if setter is not None:
                if isinstance(setter, basestring):
                    setattr(root, setter, model)
                else:
                    setter(model)

class FileHeader:
    class Flags:
        def __init__(self, flags):
            self.flags = int(flags)
        def __getattr__(self, name):
            if name == 'compressed':
                return self.flags & 0x1 != 0
            elif name == 'password':
                return self.flags & 0x2 != 0
            elif name == 'distributable':
                return self.flags & 0x4 != 0
            elif name == 'script':
                return self.flags & 0x8 != 0
            elif name == 'drm':
                return self.flags & 0x10 != 0
            elif name == 'xmltemplate_storage':
                return self.flags & 0x20 != 0
            elif name == 'history':
                return self.flags & 0x40 != 0
            elif name == 'cert_signed':
                return self.flags & 0x80 != 0
            elif name == 'cert_encrypted':
                return self.flags & 0x100 != 0
            elif name == 'cert_signature_extra':
                return self.flags & 0x200 != 0
            elif name == 'cert_drm':
                return self.flags & 0x400 != 0
            elif name == 'ccl':
                return self.flags & 0x800 != 0
            raise AttributeError(name)
    
    def decode(cls, f):
        o = cls()
        o.signature = dataio.readn(f, 32)
        version = dataio.readn(f, 4)
        o.version = (ord(version[3]), ord(version[2]), ord(version[1]), ord(version[0]))
        o.flags = FileHeader.Flags(dataio.UINT32.decode(f))
        reserved = dataio.readn(f, 216)
        return o
    decode = classmethod(decode)

def defineModels(doc):
    inch2mm = lambda x: float(int(x * 25.4 * 100 + 0.5)) / 100
    inch2px = lambda x: int(x * doc.dpi + 0.5)
    hwp2inch = lambda x: x * getattr(doc, 'inch_scale', 1) / 7200.0
    hwp2mm = lambda x: inch2mm(hwp2inch(x))
    hwp2px = lambda x: inch2px(hwp2inch(x))
    hwp2pt = lambda x: int( (x/100.0)*10 + 0.5)/10.0
    class HWPUNIT(UINT32):
        def __getattr__(self, name):
            if name == 'inch': return hwp2inch(self)
            if name == 'mm': return hwp2mm(self)
            if name == 'px': return hwp2px(self)
            if name == 'pt': return hwp2pt(self)
            raise AttributeError(name)

    class SHWPUNIT(INT32):
        def __getattr__(self, name):
            if name == 'inch': return hwp2inch(self)
            if name == 'mm': return hwp2mm(self)
            if name == 'px': return hwp2px(self)
            if name == 'pt': return hwp2pt(self)
            raise AttributeError(name)
    class HWPUNIT16(INT16):
        def __getattr__(self, name):
            if name == 'inch': return hwp2inch(self)
            if name == 'mm': return hwp2mm(self)
            if name == 'px': return hwp2px(self)
            if name == 'pt': return hwp2pt(self)
            raise AttributeError(name)

    class BlobRecord:
        def decode(cls, f):
            o = cls()
            o.data = f.read()
            return o
        decode = classmethod(decode)

        def __repr__(self):
            s = []
            data = self.data
            while len(data) > 16:
                s.append( ' '.join(['%02x'%ord(ch) for ch in data[0:16]]) )
                data = data[16:]
            s.append( ' '.join(['%02x'%ord(ch) for ch in data]) )
            return '\n'.join(s)

    class Panose1:
        fields = (
                BYTE, 'familyKind',
                BYTE, 'serifStyle',
                BYTE, 'weight',
                BYTE, 'proportion',
                BYTE, 'contrast',
                BYTE, 'strokeVariation',
                BYTE, 'armStyle',
                BYTE, 'letterform',
                BYTE, 'midline',
                BYTE, 'xheight',
                )
        __repr__ = dataio.repr

    class Flags:
        def decode(cls, f):
            o = cls()
            flag = dataio.decodeModel(cls.basetype, f)
            for (l, h), name in dataio.extract_pairs(cls.bits):
                w = h - l
                setattr(o, name, int(flag >> l) & int((2 ** (h-l)) - 1))
            return o
        __repr__ = dataio.repr
        decode = classmethod(decode)
    def defineFlags(_basetype, _bits):
        class _Flags(_basetype):
            def decode(cls, f):
                flags = cls(dataio.decodeModel(_basetype, f))
                for (l, h), name in dataio.extract_pairs(_bits):
                    w = h - l
                    setattr(flags, name, int(flags >> l) & int((2 ** (h-l)) - 1))
                return flags
            decode = classmethod(decode)
            __repr__ = dataio.repr
        return _Flags
    class DocumentProperties:
        __repr__ = dataio.repr
        fields = (
                UINT16, 'sectionCount',
                UINT16, 'pageStart',
                UINT16, 'footCommentStart',
                UINT16, 'tailCommentStart',
                UINT16, 'pictureStart',
                UINT16, 'tableStart',
                UINT16, 'mathStart',
                UINT32, 'listId',
                UINT32, 'paragraphId',
                UINT32, 'characterUnitLocInParagraph',
                #UINT32, 'flags',   # DIFFSPEC
                )

    class DocData(BlobRecord):
        def getSubModeler(self, tagid):
            if tagid == HWPTAG_FORBIDDEN_CHAR:
                return ForbiddenChar, 'forbiddenChar'

    class Border:
        fields = (
                UINT8, 'style',
                UINT8, 'width',
                COLORREF, 'color',
                )
        __repr__ = dataio.repr

    class FillColorPattern:
        fields = (
                COLORREF, 'backgroundColor',
                COLORREF, 'patternColor',
                UINT32, 'patternType',
                UINT32, 'unknown',
                )
        __repr__ = dataio.repr

    class FillGradation:
        fields = (
                BYTE,   'type',
                UINT32, 'shear',
                UINT32, 'centerX',
                UINT32, 'centerY',
                UINT32, 'blur',
                UINT32, 'nColors',
                selfref(lambda self: ARRAY(COLORREF, self.nColors)),    'colors',
                UINT32, 'shape',
                BYTE,   'blurCenter',
                )
        __repr__ = dataio.repr

    class BorderFill:
        FILL_NONE = 0
        FILL_COLOR_PATTERN = 1
        FILL_GRADATION = 4
        def decode(cls, f):
            o = cls()
            o.attr = UINT16.decode(f)
            o.border = ARRAY(Border, 4).decode(f)   # DIFFSPEC
            o.slash = dataio.decodeModel(Border, f)
            o.fillType = UINT32.decode(f)
            if o.fillType == cls.FILL_NONE:
                o.fill = None
                o.unknown = UINT32.decode(f)
            elif o.fillType == cls.FILL_COLOR_PATTERN:
                # color/pattern
                o.fill = dataio.decodeModel(FillColorPattern, f)
            elif o.fillType == cls.FILL_GRADATION:
                o.fill = dataio.decodeModel(FillGradation, f)
            return o
        decode = classmethod(decode)
        __repr__ = dataio.repr

    class FaceName:
        ATTR_ALTERNATE_FONT_EXISTS = 0x80
        ATTR_METRIC_EXISTS = 0x40
        ATTR_DEFAULT_EXISTS = 0x20
        def decode(cls, f):
            o = cls()
            attr = BYTE.decode(f)
            o.fontName = BSTR.decode(f)
            if attr & cls.ATTR_ALTERNATE_FONT_EXISTS != 0:
                o.alterFontKind = BYTE.decode(f)
                o.alterFontName = BSTR.decode(f)
            else:
                o.alterFontKind = None
                o.alterFontName = None
            if attr & cls.ATTR_METRIC_EXISTS != 0:
                o.panose1 = dataio.decodeModel(Panose1, f)
            else:
                o.panose1 = None
            if attr & cls.ATTR_DEFAULT_EXISTS != 0:
                o.defaultFontName = BSTR.decode(f)
            else:
                o.defaultFontName = None
            return o
        decode = classmethod(decode)
        __repr__ = dataio.repr

    class CHID:
        TABLE = 'tbl '
        LINE = '$lin'
        RECT = '$rec'
        ELLI = '$ell'
        ARC = '$arc'
        POLY = '$pol'
        CURV = '$cur'
        EQED = 'eqed'
        PICT = '$pic'
        OLE = '$ole'
        CONT = '$con'
        def decode(cls, f):
            return cls.parse( dataio.readn(f,4) )
        decode = classmethod(decode)
        def parse(cls, data):
            return data[3] + data[2] + data[1] + data[0]
        parse = classmethod(parse)

    class ControlChar:
        names = {
                0x02 : 'SectionColumnDef',
                0x03 : 'FieldStart',
                0x04 : 'FieldEnd',
                0x08 : 'TitleMark',
                0x09 : 'Tab',
                0x0a : 'LineBreak',
                0x0b : 'DrawingTable',
                0x0d : 'ParagraphBreak',
                0x0f : 'HiddenExplanation',
                0x10 : 'HeaderFooter',
                0x11 : 'FootEndNote',
                0x12 : 'AutoNumber',
                0x15 : 'PageControl',
                0x16 : 'Bookmark',
                #
                0x18 : 'Hyphen',
                0x1e : 'NonbreakSpace',
                0x1f : 'FixedWidthSpace',
        }

        section_column_def = u'\x02'
        field_start = u'\x03'
        field_end = u'\x04'
        title_mark = u'\x08'
        tab = u'\x09'
        line_break = u'\x0a'
        drawing_table_object = u'\x0b'
        paragraph_break = u'\x0d'
        hidden_explanation = u'\x0f'
        header_footer = u'\x10'
        foot_end_note = u'\x11'
        auto_number = u'\x12'
        page_control = u'\x15'
        bookmark = u'\x16'
        # ??? = '\x17'
        hyphen = u'\x18'
        nbspace = u'\x1e'
        fwspace = u'\x1f'

        class char:
            size = 1
        class inline:
            size = 8
        class extended:
            size = 8
        types = {
                u'\x00' : char,
                u'\x01' : extended,
                section_column_def : extended,
                field_start : extended,
                field_end : inline,
                u'\x05' : inline,
                u'\x06' : inline,
                u'\x07' : inline,
                title_mark : inline,
                tab : inline,
                line_break : char,
                drawing_table_object : extended,
                u'\x0c' : extended,
                paragraph_break : char,
                u'\x0e' : extended,
                hidden_explanation : extended,
                header_footer : extended,
                foot_end_note :extended,
                auto_number : extended,
                u'\x13' : inline,
                u'\x14' : inline,
                page_control : extended,
                bookmark : extended,
                u'\x17' : extended,
                hyphen : char,
                u'\x19' : char,
                u'\x1a' : char,
                u'\x1b' : char,
                u'\x1c' : char,
                u'\x1d' : char,
                nbspace : char,
                fwspace : char,
                }

        def find(cls, data, start_idx):
            data_len = len(data)
            i = start_idx
            while i < data_len:
                if (0 <= ord(data[i]) <= 31) and (data[i+1] == '\x00'):
                    ctlch = cls()
                    ctlch.ch = data[i:i+2].decode('utf-16le')
                    size = cls.types[ctlch.ch].size
                    return (i, i+size*2)
                i = i + 2
            return (data_len, data_len)
        find = classmethod(find)

        def parse(cls, data):
            o = cls()

            o.ch = data[0:2].decode('utf-16le')
            o.code = ord(o.ch)
            o.type = cls.types[o.ch]
            if o.type.size == 8:
                o.data = data[2:2+12]
                o.chid = CHID.parse(o.data[0:4])
                o.param = o.data[4:12]
            else:
                o.data = None
            return o
        parse = classmethod(parse)

        def __repr__(self):
            name = self.names.get(self.code)
            if name is None:
                name = '0x%02x'%self.code
            chid = getattr(self, 'chid', '')
            param = getattr(self, 'param', None)
            if param is not None:
                param = ' '.join(['%02x'%ord(x) for x in param])
            else:
                param = ''
            return 'ControlChar(%s, %s, %s)'%(name, chid, param)

    class ParaText:
        fields = (
                BYTESTREAM, 'data'
                )
        def subdata(self, startpos, endpos):
            if endpos is not None:
                return self.data[startpos*2:endpos*2]
            else:
                return self.data[startpos*2:]

    class ParaShape:
        __repr__ = dataio.repr
        attr1bits = (
                (0, 2), 'lineSpacingType',
                (2, 5), 'textAlign',
                # TODO
                )
        fields = (
                defineFlags(UINT32, attr1bits), 'attr1',
                INT32,  'marginLeft',   # 1/7200 * 2 # DIFFSPEC
                INT32,  'marginRight',  # 1/7200 * 2
                SHWPUNIT,  'indent',
                INT32,  'marginTop',    # 1/7200 * 2
                INT32,  'marginBottom', # 1/7200 * 2
                SHWPUNIT,  'lineSpacingBefore2007',
                UINT16, 'tabDefId',
                UINT16, 'numberingBulletId',
                UINT16, 'borderFillId',
                HWPUNIT16,  'borderLeft',
                HWPUNIT16,  'borderRight',
                HWPUNIT16,  'borderTop',
                HWPUNIT16,  'borderBottom',
                )
        if doc.header.version > (5, 0, 1, 6):
            fields += (
                UINT32, 'attr2',       # above 5016
                #UINT32, 'attr3',       # DIFFSPEC
                #UINT32, 'lineSpacing', # DIFFSPEC
                    )
        LINEHEIGHT_BITS = (0,1)
        LINEHEIGHT_BYFONT       = 0x0
        LINEHEIGHT_FIXED        = 0x1
        LINEHEIGHT_SPACEONLY    = 0x2
        ALIGN_BITS = (2,4)
        ALIGN_BOTH = 0
        ALIGN_LEFT = 1
        ALIGN_RIGHT = 2
        ALIGN_CENTER = 3
        ALIGN_DISTRIBUTE = 4
        ALIGN_DIVISION = 5
        def __getattr__(self, name):
            if name == 'align':
                shifts = self.ALIGN_BITS[0]
                mask = ((2 ** (self.ALIGN_BITS[1] - self.ALIGN_BITS[0] + 1)) - 1) << shifts
                return (self.attr1 & mask) >> shifts
            raise AttributeError(name)

    class ParaCharShape:
        def decode(cls, f):
            charShapes = {}
            try:
                while True:
                    pos = UINT32.decode(f)
                    id = UINT32.decode(f)
                    charShapes[pos] = id
            except dataio.Eof:
                pass
            return charShapes
        decode = classmethod(decode)

    class CharShape:
        __repr__ = dataio.repr
        fields = (
                ARRAY(WORD, 7), 'langFontFace',
                ARRAY(UINT8, 7), 'langLetterWidthExpansion',
                ARRAY(INT8, 7), 'langLetterSpacing',
                ARRAY(UINT8, 7), 'langRelativeSize',
                ARRAY(INT8, 7), 'langPosition',
                INT32, 'basesize',
                UINT32, 'attr',
                INT8, 'shadowSpace1',
                INT8, 'shadowSpace2',
                COLORREF, 'textColor',
                COLORREF, 'underlineColor',
                COLORREF, 'shadeColor',
                COLORREF, 'shadowColor',
                #UINT16, 'borderFillId',        # DIFFSPEC
                #COLORREF, 'strikeoutColor',    # DIFFSPEC
                )
        ITALIC  = 0x00000001
        BOLD    = 0x00000002
        UNDERLINE_MASK  = 0x0000000C
        UNDERLINE_NONE  = 0x00000000
        UNDERLINE       = 0x00000004
        UPPERLINE       = 0x0000000C
        UNDERLINE_LINESTYLE_MASK    = 0x000000F0
        OUTLINE_MASK    = 0x000000700
        SHADOW_MASK     = 0x000003800

    class TabDef:
        __repr__ = dataio.repr
        fields = (
                UINT32, 'attr',
                INT16, 'count',
                HWPUNIT, 'pos',
                UINT8, 'kind',
                UINT8, 'fillType',
                UINT16, 'reserved',
                )

    class TabDef(BlobRecord):
        pass

    class Style:
        __repr__ = dataio.repr
        fields = (
                BSTR, 'localName',
                BSTR, 'name',
                BYTE, 'attr',
                BYTE, 'nextStyleId',
                INT16, 'langId',
                UINT16, 'paragraphShapeId',
                UINT16, 'characterShapeId',
                )

    class IdMapping(list):
        def __init__(self, type):
            self.type = type
        def __getitem__(self, idx):
            item = list.__getitem__(self, idx)
            setattr(item, 'id', idx)
            return item
        def __iter__(self):
            class Iterator:
                def __init__(itr):
                    itr.itr = list.__iter__(self)
                    itr.idx = 0
                def next(itr):
                    item = itr.itr.next()
                    setattr(item, 'id', itr.idx)
                    itr.idx += 1
                    return item
            return Iterator()

    class BinLink: pass
    class BinEmbedded: pass
    class BinStorage: pass
    class BinData:
        def decode(cls, f):
            o = cls()
            o.flags = UINT16.decode(f)
            o.type = [BinLink, BinEmbedded, BinStorage][o.flags & 3]
            if o.type == BinLink:
                o.abspath = BSTR.decode(f)
                o.relpath = BSTR.decode(f)
            if o.type in [BinEmbedded, BinStorage]:
                o.storageId = UINT16.decode(f)
            if o.type == BinEmbedded:
                o.ext = BSTR.decode(f)
            return o
        decode = classmethod(decode)
        __repr__ = dataio.repr
        def __getattr__(self, name):
            if name == 'name':
                if self.type == doc.BinEmbedded:
                    return 'BIN%04X.%s'%(self.storageId, self.ext) # DIFFSPEC
            elif name == 'datastream':
                return doc.streams.bindata[self.name]
            raise AttributeError(name)

    class IdMappings(dict):
        fields = (
                UINT16, 'nBinData',
                UINT16, 'nKoreanFonts',
                UINT16, 'nEnglishFonts',
                UINT16, 'nHanjaFonts',
                UINT16, 'nJapaneseFonts',
                UINT16, 'nOtherFonts',
                UINT16, 'nSymbolFonts',
                UINT16, 'nUserFonts',
                UINT16, 'nBorderFills',
                UINT16, 'nCharShapes',
                UINT16, 'nTabDefs',
                UINT16, 'nNumberings',
                UINT16, 'nBullets',
                UINT16, 'nParaShapes',
                UINT16, 'nStyles',
                UINT16, 'nMemoShapes',
                )
        __repr__ = dataio.repr

        def getSubModeler(self, tagid):
            record_type = {
                        HWPTAG_BIN_DATA:BinData,
                        HWPTAG_FACE_NAME:FaceName,
                        HWPTAG_BORDER_FILL:BorderFill,
                        HWPTAG_CHAR_SHAPE:CharShape,
                        HWPTAG_TAB_DEF:TabDef,
                        HWPTAG_NUMBERING:Numbering,
                        HWPTAG_BULLET:Bullet,
                        HWPTAG_PARA_SHAPE:ParaShape,
                        HWPTAG_STYLE:Style,
                        HWPTAG_FORBIDDEN_CHAR:ForbiddenChar
                    }.get(tagid, None)
            if record_type is not None:
                return record_type, self.setdefault(record_type, IdMapping(record_type)).append

    class Numbering(BlobRecord):
        pass

    class Bullet(BlobRecord):
        pass

    class LineSeg:
        fields = (
                INT32, 'chpos',
                SHWPUNIT, 'a1',
                ARRAY(SHWPUNIT, 2), 'a2',
                ARRAY(SHWPUNIT, 2), 'a3',
                INT32, 'a4',
                ARRAY(SHWPUNIT, 2), 'a5',
                )
        __repr__ = dataio.repr
    #ParaLineSeg = OBJECTSTREAM(LineSeg)
    class ParaLineSeg(BlobRecord): pass

    class ParaRangeTag(BlobRecord):
        pass

    class ListHeader(BlobRecord):
        pass

    class PageDef:
        fields = (
                HWPUNIT, 'width',
                HWPUNIT, 'height',
                ARRAY(HWPUNIT, 4), 'offset',
                HWPUNIT, 'headerOffset',
                HWPUNIT, 'footerOffset',
                HWPUNIT, 'jebonOffset',
                defineFlags(UINT32, (
                        (0, 1), 'landscape',
                        (1, 3), 'bookcompilingStyle',
                        )), 'attr',
                #UINT32, 'attr',
                )
        PORTRAIT = 0
        LANDSCAPE = 1
        __repr__ = dataio.repr

    class FootnoteShape(BlobRecord): pass
    class PageBorderFill(BlobRecord): pass
    class ForbiddenChar(BlobRecord): pass

    class ShapeLine(BlobRecord): pass
    class ShapeOLE(BlobRecord): pass
    class ShapeRectangle:
        fields = (
                BYTE, 'round',
                ARRAY(ARRAY(SHWPUNIT, 2), 4), 'coords',
                )
        def getSubModeler(self, tagid):
            pass
        __repr__ = dataio.repr

    class PictureInfo:
        fields = (
                INT8, 'brightness',
                INT8, 'contrast',
                BYTE, 'effect',
                UINT16, 'binId',
                )
        __repr__ = dataio.repr
        def __getattr__(self, name):
            if name == 'binData':
                return doc.docinfo.mappings[doc.BinData][self.binId - 1]
            raise AttributeError(name)
    class ShapePicture:
        fields = (
                COLORREF, 'borderColor',
                INT32, 'borderWidth',
                UINT32, 'borderAttr',
                ARRAY(ARRAY(INT32,2), 4), 'rect',
                ARRAY(INT32, 4), 'crop',
                ARRAY(UINT16, 4), 'padding',
                PictureInfo, 'pictureInfo',
                # DIFFSPEC
                    # BYTE, 'transparency',
                    # UINT32, 'instanceId',
                    # PictureEffect, 'effect',
                )
        __repr__ = dataio.repr

    class Matrix:
        def decode(cls, f):
            return ARRAY(ARRAY(DOUBLE, 3), 2).decode(f) + [[0.0, 0.0, 1.0]]
        decode = classmethod(decode)

    class ShapeContainer:
        fields = (
                N_ARRAY(WORD, UINT32), 'controls',
                )
        def __init__(self):
            self.subshapes = []
        def getSubModeler(self, tagid):
            if tagid == HWPTAG_SHAPE_COMPONENT:
                return ShapeComponent, self.subshapes.append
        __repr__ = dataio.repr

    class ShapeComponent:
        fields = (
                #CHID, 'chid1',      # DIFFSPEC
                #CHID, 'chid2',      # DIFFSPEC
                UINT32, 'xoffsetInGroup',
                UINT32, 'yoffsetInGroup',
                WORD, 'groupingLevel',
                WORD, 'localVersion',
                UINT32, 'initialWidth',
                UINT32, 'initialHeight',
                UINT32, 'width',
                UINT32, 'height',
                UINT32, 'attr',
                WORD, 'angle',
                UINT32, 'rotationCenterX',
                UINT32, 'rotationCenterY',
                WORD, 'nMatrices',
                Matrix, 'matTranslation',
                selfref(lambda self: ARRAY(Matrix, self.nMatrices*2)), 'matScaleRotation',
                )
        shape = None
        def __init__(self):
            self.paragraphs = []
        def decode(cls, f):
            chid1 = CHID.decode(f)
            chid2 = CHID.decode(f)
            if chid1 == '$con':
                model = ShapeContainer()
            else:
                model = ShapeComponent()
            model.chid1 = chid1
            model.chid2 = chid2
            dataio.decode_fields_in(model, ShapeComponent.fields, f)
            if chid1 == '$con':
                dataio.decode_fields_in(model, ShapeContainer.fields, f)
                pass
            return model
        decode = classmethod(decode)
        def getSubModeler(self, tagid):
            if tagid == HWPTAG_SHAPE_COMPONENT_PICTURE:
                return ShapePicture, 'shape'
            elif tagid == HWPTAG_SHAPE_COMPONENT_LINE:
                return ShapeLine, 'shape'
            elif tagid == HWPTAG_SHAPE_COMPONENT_RECTANGLE:
                return ShapeRectangle, 'shape'
            elif tagid == HWPTAG_SHAPE_COMPONENT_OLE:
                return ShapeOLE, 'shape'
            elif tagid == HWPTAG_LIST_HEADER:
                self.paragraphs = []
                return ListHeader, 'listheader'
            elif tagid == HWPTAG_PARA_HEADER:
                return Paragraph, self.paragraphs.append
        __repr__ = dataio.repr

    class SectionDef:
        fields = (
                UINT32, 'attr',
                HWPUNIT16, 'intercolumnSpacing',
                HWPUNIT16, 'verticalAlignment',
                HWPUNIT16, 'horizontalAlignment',
                HWPUNIT, 'defaultTabStops',
                UINT16, 'numberingShapeId',
                UINT16, 'startingPageNumber',
                UINT16, 'startingPictureNumber',
                UINT16, 'startingTableNumber',
                UINT16, 'startingEquationNumber',
                )
        if doc.header.version > (5, 0, 1, 6):
            fields += (
                    UINT32, 'unknown1', # above 5016
                    #UINT32, 'unknown2',
                    )
        __repr__ = dataio.repr

        def __init__(self):
            self.pages = []
            self.footnoteShapes = []
            self.pageBorderFills = []

        def getSubModeler(self, tagid):
            submodelers = {
                    HWPTAG_PAGE_DEF:(PageDef, self.pages.append),
                    HWPTAG_FOONOTE_SHAPE:(FootnoteShape, self.footnoteShapes.append),
                    HWPTAG_PAGE_BORDER_FILL:(PageBorderFill, self.pageBorderFills.append),
                    }
            return submodelers.get(tagid, None)

    class ColumnsDef:
        def decode(cls, f):
            o = cls()
            o.attr = UINT16.decode(f)
            o.kind = o.attr & 0x03
            o.count = (o.attr >> 2) & 0xff
            o.direction = (o.attr >> 10) & 0x3
            o.sameWidths = (o.attr & 4096) != 0
            o.spacing = HWPUNIT16.decode(f)
            if not o.sameWidths:
                o.widths = ARRAY(WORD, o.count).decode(f)
            o.attr2 = UINT16.decode(f)
            o.splitterType = UINT8.decode(f)
            o.splitterWidth = UINT8.decode(f)
            o.splitterColor = COLORREF.decode(f)
            return o
        decode = classmethod(decode)
        __repr__ = dataio.repr

    listheaderbits = (
            (0, 3), 'textdirection',
            (3, 5), 'linebreak',
            (5, 7), 'vertAlign',
            )
    class TableCell:
        VALIGN_MASK     = 0x60
        VALIGN_TOP      = 0x00
        VALIGN_MIDDLE   = 0x20
        VALIGN_BOTTOM   = 0x40
        fields = (
                UINT16, 'nParagraphs',
                UINT16, 'unknown1',
                defineFlags(UINT32, listheaderbits), 'listflags',

                UINT16, 'col',
                UINT16, 'row',
                UINT16, 'colspan',
                UINT16, 'rowspan',
                HWPUNIT, 'width',
                HWPUNIT, 'height',
                ARRAY(HWPUNIT16, 4), 'padding',
                UINT16, 'borderFillId',
                )
        def __init__(self):
            self.paragraphs = []
        __repr__ = dataio.repr
        def __getattr__(cell, name):
            if name == 'borderFill':
                return doc.docinfo.mappings[doc.BorderFill][cell.borderFillId - 1] # TODO: is this right?
            raise AttributeError(name)

    class TableCaption:
        fields = (
                UINT16, 'nParagraphs',
                UINT16, 'unknown1',
                UINT32, 'listflags',

                UINT32, 'captflags',
                HWPUNIT, 'width',
                HWPUNIT16, 'offset',
                HWPUNIT, 'maxsize',
                )
        def __init__(self):
            self.paragraphs = []

    class TableBody:
        class TableFlags(Flags):
            basetype = UINT32
            bits = (
                    (0, 2), 'splitPage',
                    (2, 3), 'repeatHeaderRow',
                    )
        ZoneInfo = ARRAY(UINT16, 5)
        fields = (
                TableFlags, 'attr',
                UINT16, 'nRows',
                UINT16, 'nCols',
                HWPUNIT16, 'cellspacing',
                ARRAY(HWPUNIT16, 4), 'padding',
                selfref(lambda self: ARRAY(UINT16, self.nRows)), 'rowSizes',
                UINT16, 'borderFillId',
                )
        if doc.header.version > (5, 0, 0, 6):
            fields += (
                N_ARRAY(UINT16, ZoneInfo), 'validZones' # above 5006
                )
        __repr__ = dataio.repr
        def __init__(self):
            self.cells = []

    class CommonControlFlags(Flags):
        basetype = UINT32
        bits = (
                (0, 1), 'inline',
                (2, 3), 'affectsLineSpacing',
                (3, 5), 'vertRelTo',
                (5, 8), 'vertAlign',
                (8, 10), 'horzRelTo',
                (10, 13), 'horzAlign',
                (13, 14), 'restrictedInBody',
                (14, 15), 'overwrap',
                (15, 18), 'widthRelTo',
                (18, 20), 'heightRelTo',
                (20, 21), 'protectedSize',
                (21, 24), 'flow',
                (24, 26), 'textSide',
                (26, 28), 'numberCategory'
                )

        FLOW_FLOAT  = 0
        FLOW_BLOCK  = 1
        FLOW_BACK   = 2
        FLOW_FRONT  = 3

        TEXTSIDE_BOTH = 0
        TEXTSIDE_LEFT = 1
        TEXTSIDE_RIGHT = 2
        TEXTSIDE_LARGER = 3

        HORZ_ALIGN_LEFT = 0
        HORZ_ALIGN_CENTER = 1
        HORZ_ALIGN_RIGHT = 2
        HORZ_ALIGN_INSIDE = 3
        HORZ_ALIGN_OUTSIDE = 4

        HORZ_RELTO_PAPER = 0
        HORZ_RELTO_PAGE = 1
        HORZ_RELTO_COLUMN = 2
        HORZ_RELTO_PARAGRAPH = 3

    class CommonControl:
        fields = (
                    CommonControlFlags, 'flags',
                    SHWPUNIT, 'offsetY',    # DIFFSPEC
                    SHWPUNIT, 'offsetX',    # DIFFSPEC
                    HWPUNIT, 'width',
                    HWPUNIT, 'height',
                    INT16, 'zOrder',
                    INT16, 'unknown1',
                    ARRAY(HWPUNIT16, 4), 'margin',
                    UINT32, 'instanceId',
                    )
        if doc.header.version > (5, 0, 0, 0):
            fields += (
                    INT16, 'unknown2',
                    BSTR, 'description'
                    )
        FLOW_FLOAT  = 0
        FLOW_NORMAL = 1
        FLOW_BACK   = 2
        FLOW_FRONT  = 3
    class Table(CommonControl):
        caption = None
        body = None
        def getSubModeler(self, tagid):
            if tagid == HWPTAG_TABLE:
                return TableBody, 'body'
            elif tagid == HWPTAG_LIST_HEADER:
                if self.body is None:
                    return TableCaption, 'caption'
                else:
                    return TableCell, self.body.cells.append
            elif tagid == HWPTAG_PARA_HEADER:
                if self.body is not None:
                    setter = self.appendCellParagraph
                elif self.caption is not None:
                    setter = self.caption.paragraphs.append
                else:
                    return None
                return Paragraph, setter
        def __getattr__(tbl, name):
            if name == 'borderFill':
                return doc.docinfo.mappings[doc.BorderFill][tbl.body.borderFillId - 1] # TODO: is this right?
            raise AttributeError(name)
        __repr__ = dataio.repr
        def appendCellParagraph(self, paragraph):
            self.body.cells[-1].paragraphs.append(paragraph)


    class AutoNumber:
        fields = (
                UINT32, 'flags',
                UINT16, 'number',
                WCHAR, 'usersymbol',
                WCHAR, 'prefix',
                WCHAR, 'suffix',
                )
        def __str__(self):
            return str(self.number)
        __repr__ = dataio.repr

    class GShapeObject(CommonControl):
        def getSubModeler(self, tagid):
            if tagid == HWPTAG_SHAPE_COMPONENT:
                return ShapeComponent, 'shapecomponent'
        __repr__ = dataio.repr

    class FootNote(BlobRecord):
        def getSubModeler(self, tagid):
            if tagid == HWPTAG_LIST_HEADER:
                self.paragraphs = []
                return ListHeader, 'listhead'
            if tagid == HWPTAG_PARA_HEADER:
                return Paragraph, self.paragraphs.append
        repr == dataio.repr

    class Control:
        control_types = {
            'secd' : SectionDef,
            'cold' : ColumnsDef,
            'tbl ' : Table,
            'atno' : AutoNumber,
            'gso ' : GShapeObject,
            'fn  ' : FootNote,
        }

        def decode(cls, f):
            chid = CHID.decode(f)
            ctlhdr_type = cls.control_types.get(chid)
            if ctlhdr_type is not None:
                o = dataio.decodeModel(ctlhdr_type, f)
                o.chid = chid
            else:
                o = cls()
                o.chid = chid
                o.data = chid[::-1] + f.read() # reversed chid
            return o
        decode = classmethod(decode)
        def __repr__(self):
            s = ''
            s += '%s'%self.chid
            d = []
            data = self.data
            while len(data) > 16:
                d.append( ' '.join(['%02x'%ord(ch) for ch in data[0:16]]) )
                data = data[16:]
            d.append( ' '.join(['%02x'%ord(ch) for ch in data]) )
            s += '\n'.join(d)
            return s
        def getSubModeler(self, tagid):
            if tagid == HWPTAG_LIST_HEADER:
                self.paragraphs = []
                return ListHeader, 'listhead'
            if tagid == HWPTAG_PARA_HEADER:
                return Paragraph, self.paragraphs.append

    class SplitFlags(Flags):
        basetype = BYTE
        bits = (
                (0, 1), 'section',
                (1, 2), 'multicolumn',
                (2, 3), 'page',
                (3, 4), 'column',
                )

    class Paragraph:
        def __init__(self):
            self.data = None
            self.charShapes = None
            self.controls = {}
            self.sectionDef = None

        __repr__ = dataio.repr
        fields = (
                UINT32, 'text',
                UINT32, 'controlMask',
                UINT16, 'paragraphShapeId',
                BYTE, 'styleId',
                SplitFlags, 'split',
                UINT16, 'characterShapeCount',
                UINT16, 'rangeTagCount',
                UINT16, 'nLineSegs',
                UINT32, 'instanceId',
                )
        def getSubModeler(self, tagid):
            if tagid == HWPTAG_PARA_TEXT:
                return BYTESTREAM, 'data'
            if tagid == HWPTAG_PARA_CHAR_SHAPE:
                return ParaCharShape, 'charShapes'
            if tagid == HWPTAG_CTRL_HEADER:
                return Control, self.addControl
            if tagid == HWPTAG_PARA_LINE_SEG:
                ParaLineSeg = ARRAY(LineSeg, self.nLineSegs)
                return ParaLineSeg, 'lineSegs'

        def subdata(self, startpos, endpos):
            if self.data is None:
                return ''
            if endpos is not None:
                return self.data[startpos*2:endpos*2]
            else:
                return self.data[startpos*2:]
        def datalen(self):
            if self.data is None:
                return 0
            else:
                return len(self.data)/2

        def defineShapedText2(paragraph):
            ShapedText2 = getattr(paragraph, 'ShapedText2', None)
            if ShapedText2 is None:
                class ShapedText2:
                    def __init__(shapedtext, charShapeId, start, end, ctrl_idx):
                        shapedtext.characterShapeId = charShapeId
                        shapedtext.start = start
                        shapedtext.end = end
                        shapedtext.ctrl_idx = ctrl_idx
                    def _iterItems(shapedtext):
                        data = paragraph.subdata(shapedtext.start, shapedtext.end)
                        ctrl_idx = shapedtext.ctrl_idx

                        idx = 0
                        while idx < len(data):
                            ctrlpos, ctrlpos_end = ControlChar.find(data, idx)
                            if idx < ctrlpos:
                                yield data[idx:ctrlpos].decode('utf-16le')
                            if ctrlpos < ctrlpos_end:
                                ctrlch = ControlChar.parse(data[ctrlpos:ctrlpos_end])
                                if ctrlch.type == ControlChar.extended:
                                    idx = ctrl_idx.get(ctrlch.chid, 0)
                                    ctrl_idx[ctrlch.chid] = idx + 1
                                    try:
                                        ctrlch.control = paragraph.controls[ctrlch.chid][idx]
                                    except:
                                        logging.warning('control not found for %s[%d]'%(ctrlch.chid, idx))
                                        ctrlch.control = None
                                yield ctrlch
                            idx = ctrlpos_end
                    def __iter__(shapedtext):
                        prev = None
                        for item in shapedtext._iterItems():
                            if prev is not None:
                                yield prev
                            prev = item
                        if prev is not None:
                            if isinstance(prev, ControlChar) and prev.ch == ControlChar.paragraph_break:
                                return
                            yield prev
                    def __getattr__(shapedtext, name):
                        if name == 'elements':
                            elements = [x for x in shapedtext]
                            shapedtext.__dict__[name] = elements
                            return elements
                        elif name == 'characterShape':
                            return doc.docinfo.mappings[CharShape][shapedtext.characterShapeId]
                        raise AttributeError(name)
                paragraph.ShapedText2 = ShapedText2
            return ShapedText2

        def iterCharShapes(paragraph):
            keys = paragraph.charShapes.keys()
            keys.sort()

            prev = None
            for pos in keys:
                if prev is not None:
                    yield (prev, pos, paragraph.charShapes[prev])
                prev = pos
            if prev is not None:
                yield (prev, paragraph.datalen(), paragraph.charShapes[prev])

        def iterLines(paragraph):
            ctrl_idx = {}
            ShapedText2 = paragraph.defineShapedText2()
            class Line:
                def __init__(line, seg, end):
                    line.seg = seg
                    line.start = seg.chpos
                    line.end = end
                def data(line):
                    return paragraph.subdata(line.start, line.end)
                def __iter__(line):
                    for start, end, charShapeId in paragraph.iterCharShapes():
                        if end <= line.start:
                            continue
                        if line.end <= start:
                            break
                        if start <= line.start:
                            start = line.start
                        if line.end <= end:
                            end = line.end
                        yield ShapedText2(charShapeId, start, end, ctrl_idx)

            prevSeg = None
            for lineSeg in paragraph.lineSegs:
                if prevSeg is not None:
                    yield Line(prevSeg, lineSeg.chpos)
                prevSeg = lineSeg
            if prevSeg is not None:
                yield Line(prevSeg, paragraph.datalen())

        def iterShapedTexts(paragraph):
            ShapedText2 = paragraph.defineShapedText2()
            ctrl_idx = {}
            for start, end, charShapeId in paragraph.iterCharShapes():
                yield ShapedText2(charShapeId, start, end, ctrl_idx)

        def addControl(self, ctrl):
            chid = getattr(ctrl, 'chid', None)
            if chid is not None:
                self.controls.setdefault(ctrl.chid, []).append(ctrl)

        def __getattr__(paragraph, name):
            if name == 'shapedTexts':
                shapedTexts = [t for t in paragraph.iterShapedTexts()]
                paragraph.__dict__['shapedTexts'] = shapedTexts
                return shapedTexts
            elif name == 'style':
                style = doc.docinfo.mappings[doc.Style][paragraph.styleId]
                style.paragraphShape = doc.docinfo.mappings[doc.ParaShape][style.paragraphShapeId]
                style.characterShape = doc.docinfo.mappings[doc.CharShape][style.characterShapeId]
                return style
            elif name == 'paragraphShape':
                return doc.docinfo.mappings[doc.ParaShape][paragraph.paragraphShapeId]
            raise AttributeError(name)

    class Page:
        def __init__(self):
            self.paragraphs = []

    class Section:
        def __init__(self):
            self.pages = [Page()]
        def getSubModeler(self, tagid):
            if tagid == HWPTAG_PARA_HEADER:
                return Paragraph, self.appendParagraph
        def appendParagraph(self, paragraph):
            if paragraph.split.page:
                self.pages.append(Page())

            # this is the first paragraph of current section
            if len(self.pages) == 1 and len(self.pages[0].paragraphs) == 0:
                for e in paragraph.shapedTexts[0].elements:
                    if isinstance(e, ControlChar) and e.ch == ControlChar.section_column_def:
                        if isinstance(e.control, SectionDef):
                            self.sectionDef = e.control
                        elif isinstance(e.control, ColumnsDef):
                            self.columnsDef = e.control

            self.pages[-1].paragraphs.append(paragraph)

    class DocInfo:
        def getSubModeler(self, tagid):
            if tagid == HWPTAG_ID_MAPPINGS:
                return IdMappings, 'mappings'
            elif tagid == HWPTAG_DOCUMENT_PROPERTIES:
                return DocumentProperties, 'documentProperties'
            elif tagid == HWPTAG_DOC_DATA:
                return DocData, 'docData'

    record_types = {
            HWPTAG_DOCUMENT_PROPERTIES:DocumentProperties,
            HWPTAG_ID_MAPPINGS:IdMappings,
            HWPTAG_BIN_DATA:BinData,
            HWPTAG_FACE_NAME:FaceName,
            HWPTAG_BORDER_FILL:BorderFill,
            HWPTAG_CHAR_SHAPE:CharShape,
            #HWPTAG_TAB_DEF:TabDef,
            #HWPTAG_NUMBERING:Numbering,
            #HWPTAG_BULLET:Bullet,
            HWPTAG_PARA_SHAPE:ParaShape,
            HWPTAG_STYLE:Style,
            HWPTAG_PARA_HEADER:Paragraph,
            HWPTAG_PARA_TEXT:ParaText,
            HWPTAG_PARA_CHAR_SHAPE:ParaCharShape,
            HWPTAG_PARA_LINE_SEG:ParaLineSeg,
            HWPTAG_PARA_RANGE_TAG:ParaRangeTag,
            HWPTAG_CTRL_HEADER:Control,
            #HWPTAG_LIST_HEADER:ListHeader,
            HWPTAG_PAGE_DEF:PageDef,
            #HWPTAG_FOONOTE_SHAPE:FootnoteShape,
            #HWPTAG_PAGE_BORDER_FILL:PageBorderFill,
            HWPTAG_SHAPE_COMPONENT:ShapeComponent,
            HWPTAG_TABLE:TableBody,
            #HWPTAG_SHAPE_COMPONENT_LINE:ShapeLine,
            HWPTAG_SHAPE_COMPONENT_RECTANGLE:ShapeRectangle,
            #HWPTAG_SHAPE_COMPONENT_OLE:ShapeOLE,
            HWPTAG_SHAPE_COMPONENT_PICTURE:ShapePicture,
            #HWPTAG_FORBIDDEN_CHAR:ForbiddenChar,
            }

    return locals()

class Document(olefileio.OleFileIO):
    dpi = 96
    inch_scale = 1
    modelsDefined = False
    def __getattr__(self, name):
        if not self.modelsDefined:
            self.modelsDefined = True
            models = defineModels(self)
            self.__dict__.update(models)
            if name in models:
                return models[name]

        if name == 'streams':
            class Streams:
                def __getattr__(streams, name):
                    if name == 'fileheader':
                        return self.openstream('FileHeader')
                    elif name == 'docinfo':
                        strm = self.openstream('DocInfo')
                        if self.header.flags.compressed:
                            strm = StringIO.StringIO(zlib.decompress(strm.read(), -15)) # without gzip header
                        return strm
                    elif name == 'section':
                        class SectionStreams:
                            def __getitem__(sectionstreams, idx):
                                try:
                                    sec = self.openstream('BodyText/Section'+str(idx))
                                    if self.header.flags.compressed:
                                        sec = StringIO.StringIO(zlib.decompress(sec.read(), -15))
                                    return sec
                                except IOError:
                                    raise IndexError(idx)
                        return SectionStreams()
                    elif name == 'bindata':
                        class BinDataStreams:
                            def __getitem__(streams, name):
                                try:
                                    strm = self.openstream('BinData/%s'%name)
                                    if self.header.flags.compressed:
                                        strm = StringIO.StringIO(zlib.decompress(strm.read(), -15))
                                    return strm
                                except IOError:
                                    raise KeyError(name)
                        return BinDataStreams()
                    elif name == 'previewText':
                        return self.openstream('PrvText')
                    elif name == 'previewImage':
                        return self.openstream('PrvImage')
                    elif name == 'summaryinfo':
                        return self.openstream('\005HwpSummaryInformation')
                    raise AttributeError(name)
            return Streams()
        elif name == 'header':
            header = FileHeader.decode(self.streams.fileheader)
            self.__dict__[name] = header
            return header
        elif name == 'docinfo':
            docinfo = self.DocInfo()
            buildModelTree(docinfo, getRecords(self.streams.docinfo))
            self.__dict__[name] = docinfo
            return docinfo
        elif name == 'sections':
            sections = self._sections()
            self.__dict__[name] = sections
            return sections
        elif name == 'bindatas':
            bindatas = self._bindatas()
            self.__dict__[name] = bindatas
            return bindatas
        elif name == 'previewText':
            return self.streams.previewText.read().decode('utf-16')
        elif name == 'previewImage':
            return self.streams.previewImage.read()
        elif name == 'summaryinfo':
            return self.streams.summaryinfo.read()
        raise AttributeError(name)

    def _sections(self):
        class Sections:
            def __getitem__(sections, idx):
                sect = self.Section()
                buildModelTree(sect, getRecords(self.streams.section[idx]))
                return sect
            def __iter__(sections):
                idxs = []
                for e in self.listdir():
                    if e[0] == 'BodyText' and e[1][0:7] == 'Section':
                        idxs.append(int(e[1][7:]))
                idxs.sort()
                for k in idxs:
                    yield sections[k]
        return Sections()

    def _bindatas(self):
        class BinDatas:
            def __getitem__(sections, name):
                return self.streams.bindata[name]
            def __iter__(bindatas):
                names = []
                for e in self.listdir():
                    if e[0] == 'BinData':
                        names.append(e)
                names.sort()
                for k in names:
                    yield k, bindatas[k].read()
        return BinDatas()

    def streamNames(self):
        for e in self.listdir():
            yield os.path.join(*e)

try:
    sample5017 = Document('sample2005.hwp')
    sample5024 = Document('sample-5-0-2-4.hwp')
    sample = sample5017
except IOError:
    pass

if __name__=='__main__':
    import sys
    if sys.argv[1] == 'version':
        doc = Document(sys.argv[2])
        print doc.header.version
    if sys.argv[1] == 'streams':
        doc = Document(sys.argv[2])
        for name in doc.streamNames():
            print name

#    print sample.header.signature, sample.header.version
#    for sn in sample.streams():
#        print sn
#    assert(sample.header.attr.compressed)
#    print sample.previewText
