# -*- coding: utf-8 -*-
#
#                    GNU AFFERO GENERAL PUBLIC LICENSE
#                       Version 3, 19 November 2007
#
#    pyhwp : hwp file format parser in python
#    Copyright (C) 2010 yoosung <mete0r@sarangbang.or.kr>
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
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

import dataio
from dataio import *
import logging
import itertools

# DIFFSPEC : Difference with the specification

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
    HWPTAG_BEGIN + 58 : 'HWPTAG_FOOTNOTE_SHAPE',
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
    HWPTAG_BEGIN + 71 : 'HWPTAG_CTRL_DATA',
    HWPTAG_BEGIN + 72 : 'HWPTAG_CTRL_EQEDIT',
    # HWPTAG_BEGIN + 73 : RESERVED
    HWPTAG_BEGIN + 74 : 'HWPTAG_SHAPE_COMPONENT_TEXTART',
    # ...
    HWPTAG_BEGIN + 78 : 'HWPTAG_FORBIDDEN_CHAR',
}
for k, v in tagnames.iteritems():
    globals()[v] = k
del k, v

def decode_rechdr(f):
    try:
        # TagID, Level, Size
        rechdr = UINT32.parse(f)
        tagid = rechdr & 0x3ff
        level = (rechdr >> 10) & 0x3ff
        size = (rechdr >> 20) & 0xfff
        if size == 0xfff:
            size = UINT32.parse(f)
        return (tagid, level, size)
    except Eof:
        return None

class RecordsContainer(object):
    def __init__(self):
        self.records = []

class Record:
    def __init__(self, seqno, tagid, level, bytes):
        self.seqno = seqno
        self.tagid = tagid
        self.level = level
        self.bytes = bytes
        self.subrecs = []
        self.model = None
    def __repr__(self):
        return '<Record %d %s level=%d size=%d>'%(
                self.seqno, tagnames.get(self.tagid, 'HWPTAG_BEGIN+%d'%(self.tagid - HWPTAG_BEGIN)),
                self.level, len(self.bytes))
    def bytestream(self):
        return StringIO(self.bytes)


def getRecords(f):
    seqno = 0
    while True:
        rechdr = decode_rechdr(f)
        if rechdr is None:
            return
        tagid, level, size = rechdr
        bytes = dataio.readn(f, size)
        yield Record(seqno, tagid, level, bytes)
        seqno += 1

STARTREC = 0
ENDREC = 2
def pullparseRecords(recordlist, records):
    stack = []
    for rec in records:
        level = rec.level

        while level < len(stack):
            yield ENDREC, stack.pop()
        while len(stack) < level:
            raise Exception('invalid level: Record %d, level %d, expected level=%d'%(rec.seqno, level, len(stack)))
        assert(len(stack) == level)

        if len(stack) > 0:
            stack[-1].subrecs.append(rec)
        stack.append(rec)
        yield STARTREC, rec

    while 0 < len(stack):
        yield ENDREC, stack.pop()

def pullparse(recordlist, f):
    return pullparseRecords(recordlist, getRecords(f))

def buildModelTree(root, bytestream):
    context = root
    context_stack = []
    context_record_stack = []
    for evt, rec in pullparse(root.records, bytestream):
        if evt == STARTREC:
            root.records.append(rec)
            try:
                modeler = context.getSubModeler(rec)
                if modeler is not None:
                    Model, setter = modeler
                    try:
                        model = Model.parse(rec.bytestream())
                    except:
                        logging.error( 'failed to parse a Record(#%d): %s'%(rec.seqno, str(Model)) + ':\n' + '\t'+dataio.hexdump(rec.bytes).replace('\n', '\n\t') + '\n')
                        raise
                else:
                    #logging.debug('record #%d: ignoring unrecognized tagid: %s 0x%x (+%d) at record context %s'%(rec.seqno, tagnames.get(rec.tagid, ''), rec.tagid, rec.tagid - HWPTAG_BEGIN, str(context)))
                    model = None
                    setter = None
            except Exception, e:
                logging.error('record #%d: tagid=%d (%s, HWPTAG_BEGIN + %d) : %s'%(rec.seqno, rec.tagid, tagnames[rec.tagid], rec.tagid-HWPTAG_BEGIN, str(e)))
                raise

            if setter is None:
                addsubrec = getattr(context, 'addsubrec', None)
                if addsubrec is not None:
                    addsubrec(rec)
                context_record_stack.append(rec)
            else:
                rec.model = model
                model.record = rec
                context_stack.append((context, context_record_stack, setter))
                context = model
                context_record_stack = []

        elif evt == ENDREC:
            if len(context_record_stack) > 0:
                context_record_stack.pop()
            else:
                model = context
                context, context_record_stack, setter = context_stack.pop()
                if isinstance(setter, basestring):
                    setattr(context, setter, model)
                else:
                    setter(model)

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
    CONTAINER = '$con'
    def parse(cls, f):
        return cls.decode_bytes( readn(f,4) )
    parse = classmethod(parse)
    def decode_bytes(cls, data):
        return data[3] + data[2] + data[1] + data[0]
    decode_bytes = classmethod(decode_bytes)

class FileHeader:
    Flags = dataio.Flags(UINT32, (
        0, 'compressed',
        1, 'password',
        2, 'distributable',
        3, 'script',
        4, 'drm',
        5, 'xmltemplate_storage',
        6, 'history',
        7, 'cert_signed',
        8, 'cert_encrypted',
        9, 'cert_signature_extra',
        10, 'cert_drm',
        11, 'ccl',
        ))
    def getFields(self):
        yield BYTES(32), 'signature'
        yield VERSION, 'version'
        yield self.Flags, 'flags'
        yield BYTES(216), 'reserved'
fixup_parse(FileHeader)

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
        def __repr__(self):
            return '%.1fpt(%.1fmm, 0x%x)'%(hwp2pt(self), hwp2mm(self), self)

    class SHWPUNIT(INT32):
        def __getattr__(self, name):
            if name == 'inch': return hwp2inch(self)
            if name == 'mm': return hwp2mm(self)
            if name == 'px': return hwp2px(self)
            if name == 'pt': return hwp2pt(self)
            raise AttributeError(name)
        def __repr__(self):
            return '%.1fpt(%.1fmm, 0x%x)'%(hwp2pt(self), hwp2mm(self), self)
    class HWPUNIT16(INT16):
        def __getattr__(self, name):
            if name == 'inch': return hwp2inch(self)
            if name == 'mm': return hwp2mm(self)
            if name == 'px': return hwp2px(self)
            if name == 'pt': return hwp2pt(self)
            raise AttributeError(name)
        def __repr__(self):
            return '%.1fpt(%.1fmm, 0x%x)'%(hwp2pt(self), hwp2mm(self), self)

    class Panose1:
        def getFields(self):
            yield BYTE, 'familyKind',
            yield BYTE, 'serifStyle',
            yield BYTE, 'weight',
            yield BYTE, 'proportion',
            yield BYTE, 'contrast',
            yield BYTE, 'strokeVariation',
            yield BYTE, 'armStyle',
            yield BYTE, 'letterform',
            yield BYTE, 'midline',
            yield BYTE, 'xheight',

    class DocumentProperties:
        def getFields(self):
            yield UINT16, 'sectionCount',
            yield UINT16, 'pageStart',
            yield UINT16, 'footCommentStart',
            yield UINT16, 'tailCommentStart',
            yield UINT16, 'pictureStart',
            yield UINT16, 'tableStart',
            yield UINT16, 'mathStart',
            yield UINT32, 'listId',
            yield UINT32, 'paragraphId',
            yield UINT32, 'characterUnitLocInParagraph',
            #yield UINT32, 'flags',   # DIFFSPEC

    class DocData:
        def getSubModeler(self, rec):
            if rec.tagid == HWPTAG_FORBIDDEN_CHAR:
                return ForbiddenChar, 'forbiddenChar'

    class Border:
        def getFields(self):
            yield UINT8, 'style',
            yield UINT8, 'width',
            yield COLORREF, 'color',

    class FillColorPattern:
        def getFields(self):
            yield COLORREF, 'backgroundColor',
            yield COLORREF, 'patternColor',
            yield UINT32, 'patternType',
            yield UINT32, 'unknown',

    class FillGradation:
        def getFields(self):
            yield BYTE,   'type',
            yield UINT32, 'shear',
            yield UINT32, 'centerX',
            yield UINT32, 'centerY',
            yield UINT32, 'blur',
            yield N_ARRAY(UINT32, COLORREF), 'colors',
            yield UINT32, 'shape',
            yield BYTE,   'blurCenter',

    class BorderFill:
        FILL_NONE = 0
        FILL_COLOR_PATTERN = 1
        FILL_GRADATION = 4
        def getFields(self):
            yield UINT16, 'attr'
            yield ARRAY(Border, 4), 'border' # DIFFSPEC
            yield Border, 'slash'
            yield UINT32, 'fillType'
            if self.fillType == self.FILL_NONE:
                yield None, 'fill'
                yield UINT32, 'unknown'
            elif self.fillType == self.FILL_COLOR_PATTERN:
                # color/pattern
                yield FillColorPattern, 'fill'
            elif self.fillType == self.FILL_GRADATION:
                yield FillGradation, 'fill'
        def __repr__(self):
            return '%s\n'%self.__class__.__name__+'\n'.join([ ' - %s = %s'%(name, repr(getattr(self, name))) for type, name in self.getFields()])

    class AlternateFont:
        def getFields(self):
            yield BYTE, 'kind'
            yield BSTR, 'name'

    class FaceName:
        Flags = dataio.Flags(BYTE, (
            5, 'default',
            6, 'metric',
            7, 'alternate',
            ))
        def getFields(self):
            yield self.Flags, 'attr'
            yield BSTR, 'fontName'
            yield AlternateFont if self.attr.alternate else None, 'alternateFont'
            yield Panose1 if self.attr.metric else None, 'panose1'
            yield BSTR if self.attr.default else None, 'defaultFontName'

    class Control:
        subtypes = {}
        def getsubtype(cls, rec):
            chid = CHID.decode_bytes(rec.bytes)
            return cls.subtypes.get(chid, cls)
        getsubtype = classmethod(getsubtype)
        def addsubtype(cls, type):
            cls.subtypes[type.chid] = type
        addsubtype = classmethod(addsubtype)
        def getFields(self):
            yield CHID, 'chid'
        def getSubModeler(self, rec):
            pass
        def __repr__(self):
            return '%s\n'%(self.__class__.__name__)\
                    + '\n'.join([' - %s : %s'%(name, repr(getattr(self, name))) for type, name in self.getFields()])

    class ControlChar:
        class char:
            size = 1
        class inline:
            size = 8
        class extended:
            size = 8
        chars = {
                0x00 : ('NULL', char),
                0x01 : ('0x01', extended),
                0x02 : ('SECTION_COLUMN_DEF', extended),
                0x03 : ('FIELD_START', extended),
                0x04 : ('FIELD_END', inline),
                0x05 : ('0x05', inline),
                0x06 : ('0x06', inline),
                0x07 : ('0x07', inline),
                0x08 : ('TITLE_MARK', inline),
                0x09 : ('TAB', inline),
                0x0a : ('LINE_BREAK', char),
                0x0b : ('DRAWING_TABLE_OBJECT', extended),
                0x0c : ('0x0C', extended),
                0x0d : ('PARAGRAPH_BREAK', char),
                0x0e : ('0x0E', extended),
                0x0f : ('HIDDEN_EXPLANATION', extended),
                0x10 : ('HEADER_FOOTER', extended),
                0x11 : ('FOOT_END_NOTE', extended),
                0x12 : ('AUTO_NUMBER', extended),
                0x13 : ('0x13', inline),
                0x14 : ('0x14', inline),
                0x15 : ('PAGE_CONTROL', extended),
                0x16 : ('BOOKMARK', extended),
                0x17 : ('0x17', extended),
                0x18 : ('HYPHEN', char),
                0x1e : ('NONBREAK_SPACE', char),
                0x1f : ('FIXWIDTH_SPACE', char),
        }
        names = {}
        kinds = {}
        import re
        regex = re.compile('[\x00-\x1f]\x00')
        def find(cls, data, start_idx):
            while True:
                m = cls.regex.search(data, start_idx)
                if m is not None:
                    i = m.start()
                    if i & 1 == 1:
                        start_idx = i + 1
                        continue
                    char = unichr(ord(data[i]))
                    size = cls.kinds[char].size
                    return i, i+size*2
            data_len = len(data)
            return data_len, data_len
        find = classmethod(find)

        byteoffset = None
        charoffset = None
        charShapeId = None
        chid = None
        control = None
        def __init__(self, char):
            self.ch = char
            self.code = ord(char)
            self.kind = self.kinds[char]
        def decode_bytes(cls, data):
            char = dataio.decode_utf16le_besteffort(data[0:2])
            o = cls(char)
            if o.kind.size == 8:
                o.data = data[2:2+12]
                o.chid = CHID.decode_bytes(o.data[0:4])
                o.param = o.data[4:12]
            else:
                o.data = None
            return o
        decode_bytes = classmethod(decode_bytes)

        def __len__(self):
            return self.kind.size

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
            return '<ControlChar.%s %s %s charShapeId=%s charoffset=%s byteoffset=%s>'%(
                    name, repr(chid), param, self.charShapeId, self.charoffset,
                    ('0x%x'%self.byteoffset) if self.byteoffset is not None else None)
    for (code, (name, kind)) in ControlChar.chars.iteritems():
        setattr(ControlChar, name, unichr(code))
        ControlChar.names[code] = name
        ControlChar.kinds[unichr(code)] = kind
    del code, name, kind

    class Text(unicode):
        byteoffset = None
        charoffset = None
        charShapeId = None
        def __repr__(self):
            return '<Text %s charShapeId=%s (%s,%s) byteoffset=%d>'%(unicode.__repr__(self), self.charShapeId, self.charoffset, self.charoffset+len(self), self.byteoffset)
        def split(self, pos):
            prev, next = Text(self[:pos]), Text(self[pos:])
            prev.byteoffset = self.byteoffset
            prev.charoffset = self.charoffset
            prev.charShapeId = self.charShapeId
            next.charoffset = self.charoffset + pos
            next.byteoffset = next.charoffset * 2
            next.charShapeId = self.charShapeId
            return prev, next

    class ParaText(list):
        def decode(self, bytes):
            for elem in self.parseBytes(bytes):
                self.append(elem)
            return self
        def parseBytes(cls, bytes):
            size = len(bytes)
            idx = 0
            while idx < size:
                ctrlpos, ctrlpos_end = ControlChar.find(bytes, idx)
                if idx < ctrlpos:
                    text = Text(dataio.decode_utf16le_besteffort(bytes[idx:ctrlpos]))
                    text.byteoffset = idx
                    text.charoffset = idx/2
                    text.charShapeId = None
                    yield text
                if ctrlpos < ctrlpos_end:
                    ctlch = ControlChar.decode_bytes(bytes[ctrlpos:ctrlpos_end])
                    ctlch.byteoffset = ctrlpos
                    ctlch.charoffset = ctrlpos/2
                    ctlch.charShapeId = None
                    yield ctlch
                idx = ctrlpos_end
        parseBytes = classmethod(parseBytes)
        def getElements(self):
            return self.parseBytes(self.record.bytes)
        def controlchars_by_chid(self, chid):
            return itertools.ifilter(
                    lambda elem: isinstance(elem, ControlChar) and elem.chid == chid,
                    self)
        def __repr__(self):
            return '\n'.join(['- '+repr(x) for x in self])

    class ParaShape(object):
        Flags = dataio.Flags(UINT32, (
                (0, 1), 'lineSpacingType',
                (2, 4), 'textAlign',
                # TODO
                ))
        def getFields(self):
            yield self.Flags, 'attr1',
            yield INT32,  'doubleMarginLeft',   # 1/7200 * 2 # DIFFSPEC
            yield INT32,  'doubleMarginRight',  # 1/7200 * 2
            yield SHWPUNIT,  'indent',
            yield INT32,  'doubleMarginTop',    # 1/7200 * 2
            yield INT32,  'doubleMarginBottom', # 1/7200 * 2
            yield SHWPUNIT,  'lineSpacingBefore2007',
            yield UINT16, 'tabDefId',
            yield UINT16, 'numberingBulletId',
            yield UINT16, 'borderFillId',
            yield HWPUNIT16,  'borderLeft',
            yield HWPUNIT16,  'borderRight',
            yield HWPUNIT16,  'borderTop',
            yield HWPUNIT16,  'borderBottom',
            if doc.header.version > (5, 0, 1, 6):
                yield UINT32, 'attr2',       # above 5016
                #yield UINT32, 'attr3',       # DIFFSPEC
                #yield UINT32, 'lineSpacing', # DIFFSPEC
        def getMarginLeft(self):
            return SHWPUNIT(self.doubleMarginLeft/2)
        marginLeft = property(getMarginLeft)
        def getMarginRight(self):
            return SHWPUNIT(self.doubleMarginRight/2)
        marginRight = property(getMarginRight)
        def getMarginTop(self):
            return SHWPUNIT(self.doubleMarginTop/2)
        marginTop = property(getMarginTop)
        def getMarginBottom(self):
            return SHWPUNIT(self.doubleMarginBottom/2)
        marginBottom = property(getMarginBottom)

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

    class CharShape:
        def getFields(self):
            yield ARRAY(WORD, 7), 'langFontFace',
            yield ARRAY(UINT8, 7), 'langLetterWidthExpansion',
            yield ARRAY(INT8, 7), 'langLetterSpacing',
            yield ARRAY(UINT8, 7), 'langRelativeSize',
            yield ARRAY(INT8, 7), 'langPosition',
            yield INT32, 'basesize',
            yield UINT32, 'attr',
            yield INT8, 'shadowSpace1',
            yield INT8, 'shadowSpace2',
            yield COLORREF, 'textColor',
            yield COLORREF, 'underlineColor',
            yield COLORREF, 'shadeColor',
            yield COLORREF, 'shadowColor',
            #yield UINT16, 'borderFillId',        # DIFFSPEC
            #yield COLORREF, 'strikeoutColor',    # DIFFSPEC
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
        def getFields(self):
            yield UINT32, 'attr',
            yield INT16, 'count',
            yield HWPUNIT, 'pos',
            yield UINT8, 'kind',
            yield UINT8, 'fillType',
            yield UINT16, 'reserved',

    class TabDef:
        pass

    class Style:
        def getFields(self):
            yield BSTR, 'localName',
            yield BSTR, 'name',
            yield BYTE, 'attr',
            yield BYTE, 'nextStyleId',
            yield INT16, 'langId',
            yield UINT16, 'paragraphShapeId',
            yield UINT16, 'characterShapeId',

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
        def getFields(self):
            yield UINT16, 'flags'
            if self.type == BinLink:
                yield BSTR, 'abspath'
                yield BSTR, 'relpath'
            if self.type == BinEmbedded:
                yield UINT16, 'storageId'
                yield BSTR, 'ext'
            if self.type == BinStorage:
                yield UINT16, 'storageId'
        def __getattr__(self, name):
            if name == 'type':
                type = [BinLink, BinEmbedded, BinStorage][self.flags & 3]
                self.type = type
                return type
            elif name == 'name':
                if self.type == BinEmbedded:
                    return 'BIN%04X.%s'%(self.storageId, self.ext) # DIFFSPEC
            elif name == 'datastream':
                return doc.streams.bindata[self.name]
            raise AttributeError(name)

    class IdMappings(dict):
        def getFields(self):
            yield UINT16, 'nBinData',
            yield UINT16, 'nKoreanFonts',
            yield UINT16, 'nEnglishFonts',
            yield UINT16, 'nHanjaFonts',
            yield UINT16, 'nJapaneseFonts',
            yield UINT16, 'nOtherFonts',
            yield UINT16, 'nSymbolFonts',
            yield UINT16, 'nUserFonts',
            yield UINT16, 'nBorderFills',
            yield UINT16, 'nCharShapes',
            yield UINT16, 'nTabDefs',
            yield UINT16, 'nNumberings',
            yield UINT16, 'nBullets',
            yield UINT16, 'nParaShapes',
            yield UINT16, 'nStyles',
            yield UINT16, 'nMemoShapes',

        def getSubModeler(self, rec):
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
                    }.get(rec.tagid, None)
            if record_type is not None:
                return record_type, self.setdefault(record_type, IdMapping(record_type)).append

    class Numbering:
        pass

    class Bullet:
        pass

    class LineSeg:
        def getFields(self):
            yield INT32, 'chpos',
            yield SHWPUNIT, 'offsetY',
            yield SHWPUNIT, 'a2',
            yield SHWPUNIT, 'height',
            yield SHWPUNIT, 'a3',
            yield SHWPUNIT, 'marginBottom',
            yield INT32, 'a4',
            yield ARRAY(SHWPUNIT, 2), 'a5',
        def __repr__(self):
            return repr(dict([(name, getattr(self,name)) for (type, name) in self.getFields()]))

    class ParaRangeTag:
        pass

    class ListHeader(object):
        Flags = dataio.Flags(UINT32, (
            (0, 2), 'textdirection',
            (3, 4), 'linebreak',
            (5, 6), 'vertAlign',
            ))
        VALIGN_MASK     = 0x60
        VALIGN_TOP      = 0x00
        VALIGN_MIDDLE   = 0x20
        VALIGN_BOTTOM   = 0x40
        def getFields(self):
            yield UINT16, 'nParagraphs',
            yield UINT16, 'unknown1',
            yield self.Flags, 'listflags',
        def __init__(self):
            self.paragraphs = []
        def __repr__(self):
            return '%s\n'%self.__class__.__name__+'\n'.join([ ' - %s = %s'%(name, repr(getattr(self, name))) for type, name in self.getFields()])

    class PageDef(object):
        Flags = dataio.Flags(UINT32, (
                        0, 'landscape',
                        (1, 2), 'bookcompilingStyle',
                        ))
        def getFields(self):
            yield HWPUNIT, 'paper_width',
            yield HWPUNIT, 'paper_height',
            yield HWPUNIT, 'offsetLeft',
            yield HWPUNIT, 'offsetRight',
            yield HWPUNIT, 'offsetTop',
            yield HWPUNIT, 'offsetBottom',
            yield HWPUNIT, 'offsetHeader',
            yield HWPUNIT, 'offsetFooter',
            yield HWPUNIT, 'jebonOffset',
            yield self.Flags, 'attr',
            #yield UINT32, 'attr',
        def __repr__(self):
            return ('%s\n'%self.__class__.__name__)+'\n'.join([ ' - %s = %s'%(name, repr(getattr(self, name))) for type, name in self.getFields()])
        PORTRAIT = 0
        LANDSCAPE = 1

        OFFSET_LEFT = 0
        OFFSET_RIGHT = 1
        OFFSET_TOP = 2
        OFFSET_BOTTOM = 3
        def getDimension(self):
            width = HWPUNIT( self.paper_width - self.offsetLeft - self.offsetRight )
            height = HWPUNIT( self.paper_height - (self.offsetTop + self.offsetHeader) - (self.offsetBottom + self.offsetFooter))
            if self.attr.landscape:
                return (height, width)
            else:
                return (width, height)
        dimension = property(getDimension)
        def getHeight(self):
            if self.attr.landscape:
                width = HWPUNIT( self.paper_width - self.offsetLeft - self.offsetRight )
                return width
            else:
                height = HWPUNIT( self.paper_height - (self.offsetTop + self.offsetHeader) - (self.offsetBottom + self.offsetFooter))
                return height
        height = property(getHeight)
        def getWidth(self):
            if self.attr.landscape:
                height = HWPUNIT( self.paper_height - (self.offsetTop + self.offsetHeader) - (self.offsetBottom + self.offsetFooter))
                return height
            else:
                width = HWPUNIT( self.paper_width - self.offsetLeft - self.offsetRight )
                return width
        width = property(getWidth)

    class FootnoteShape:
        Flags = dataio.Flags(UINT32, (
            ))
        def getFields(self):
            yield self.Flags, 'flags'
            yield WCHAR, 'usersymbol'
            yield WCHAR, 'prefix'
            yield WCHAR, 'suffix'
            yield UINT16, 'starting_number'
            yield HWPUNIT16, 'splitterLength'
            yield HWPUNIT16, 'splitterMarginTop'
            yield HWPUNIT16, 'splitterMarginBottom'
            yield HWPUNIT16, 'notesSpacing'
            yield Border, 'splitterStyle'
        def __repr__(self):
            return '%s\n'%self.__class__.__name__+'\n'.join([ ' - %s = %s'%(name, repr(getattr(self, name))) for type, name in self.getFields()])

    class PageBorderFill: pass
    class ForbiddenChar: pass

    class ShapeLine: pass
    class ShapePolygon: pass
    class ShapeEllipse: pass
    class ShapeTextArt: pass
    class ShapeOLE: pass
    class Coord:
        def getFields(self):
            yield SHWPUNIT, 'x',
            yield SHWPUNIT, 'y',
    class ShapeRectangle:
        def getFields(self):
            yield BYTE, 'round',
            yield ARRAY(Coord, 4), 'coords',

    class PictureInfo:
        def getFields(self):
            yield INT8, 'brightness',
            yield INT8, 'contrast',
            yield BYTE, 'effect',
            yield UINT16, 'binId',
        def __getattr__(self, name):
            if name == 'binData':
                return doc.docinfo.mappings[doc.BinData][self.binId - 1]
            raise AttributeError(name)
    class ShapePicture:
        def getFields(self):
            yield COLORREF, 'borderColor',
            yield INT32, 'borderWidth',
            yield UINT32, 'borderAttr',
            yield ARRAY(ARRAY(INT32,2), 4), 'rect',
            yield ARRAY(INT32, 4), 'crop',
            yield ARRAY(UINT16, 4), 'padding',
            yield PictureInfo, 'pictureInfo',
            # DIFFSPEC
                # BYTE, 'transparency',
                # UINT32, 'instanceId',
                # PictureEffect, 'effect',

    class ScaleRotationMatrix:
        def getFields(self):
            yield Matrix, 'scaler',
            yield Matrix, 'rotator',

    class ShapeComponent:
        Flags = dataio.Flags(UINT32, (
                0, 'flip')
            )
        def getFields(self):
            yield CHID, 'chid'
            yield SHWPUNIT, 'xoffsetInGroup'
            yield SHWPUNIT, 'yoffsetInGroup'
            yield WORD, 'groupingLevel'
            yield WORD, 'localVersion'
            yield SHWPUNIT, 'initialWidth'
            yield SHWPUNIT, 'initialHeight'
            yield SHWPUNIT, 'width'
            yield SHWPUNIT, 'height'
            yield self.Flags, 'attr'
            yield WORD, 'angle'
            yield SHWPUNIT, 'rotationCenterX'
            yield SHWPUNIT, 'rotationCenterY'
            yield WORD, 'nMatrices'
            yield Matrix, 'matTranslation'
            yield ARRAY(ScaleRotationMatrix, self.nMatrices), 'matScaleRotation'
            if self.chid == CHID.CONTAINER:
                yield N_ARRAY(WORD, CHID), 'controls',

        def __init__(self):
            shape = None
            listheader = None
            self.subshapes = []
        def getSubModeler(self, rec):
            tagid = rec.tagid
            if tagid == HWPTAG_SHAPE_COMPONENT_PICTURE:
                return ShapePicture, 'shape'
            elif tagid == HWPTAG_SHAPE_COMPONENT_LINE:
                return ShapeLine, 'shape'
            elif tagid == HWPTAG_SHAPE_COMPONENT_RECTANGLE:
                return ShapeRectangle, 'shape'
            elif tagid == HWPTAG_SHAPE_COMPONENT_POLYGON:
                return ShapePolygon, 'shape'
            elif tagid == HWPTAG_SHAPE_COMPONENT_ELLIPSE:
                return ShapeEllipse, 'shape'
            elif tagid == HWPTAG_SHAPE_COMPONENT_OLE:
                return ShapeOLE, 'shape'
            elif tagid == HWPTAG_SHAPE_COMPONENT_TEXTART:
                return ShapeTextArt, 'shape'
            elif tagid == HWPTAG_LIST_HEADER:
                return ListHeader, 'listheader'
            elif tagid == HWPTAG_PARA_HEADER:
                return Paragraph, self.listheader.paragraphs.append
            elif tagid == HWPTAG_SHAPE_COMPONENT:
                return ShapeComponent, self.subshapes.append
        def __repr__(self):
            return '%s\n'%self.__class__.__name__+'\n'.join([ ' - %s = %s'%(name, repr(getattr(self, name))) for type, name in self.getFields()])

    class PrimaryShapeComponent(ShapeComponent):
        def getFields(self):
            yield CHID, 'unknownchid'
            for x in ShapeComponent.getFields(self):
                yield x

    class TableCell(ListHeader):
        def getFields(self):
            for x in ListHeader.getFields(self):
                yield x
            yield UINT16, 'col',
            yield UINT16, 'row',
            yield UINT16, 'colspan',
            yield UINT16, 'rowspan',
            yield HWPUNIT, 'width',
            yield HWPUNIT, 'height',
            yield ARRAY(HWPUNIT16, 4), 'padding',
            yield UINT16, 'borderFillId',
            yield HWPUNIT, 'unknown_width',
        def __repr__(self):
            return 'TableCell\n'+'\n'.join([ ' - %s = %s'%(name, repr(getattr(self, name))) for type, name in self.getFields()])
        def getBorderFill(cell):
            return doc.docinfo.mappings[doc.BorderFill][cell.borderFillId - 1] # TODO: is this right?
        borderFill = property(getBorderFill)

        def getPages(self):
            for paragraphs in getPagedParagraphs(self.paragraphs):
                yield paragraphs

    class TableCaption(ListHeader):
        CaptionFlags = dataio.Flags(
                UINT32, (
                    (0, 1), 'position',
                    2, 'include_margin',
                    )
                )
        POS_LEFT = 0
        POS_RIGHT = 1
        POS_TOP = 2
        POS_BOTTOM = 3
        def getFields(self):
            for x in ListHeader.getFields(self):
                yield x
            yield self.CaptionFlags, 'captflags',
            yield HWPUNIT, 'width',
            yield HWPUNIT16, 'offset', # 캡션과 틀 사이 간격
            yield HWPUNIT, 'maxsize',
        def __repr__(self):
            return 'TableCaption\n'+'\n'.join([ ' - %s = %s'%(name, repr(getattr(self, name))) for type, name in self.getFields()])

    class TableBody:
        Split = dataio.Enum(
                NONE = 0,
                BY_CELL = 1,
                SPLIT = 2,
                )
        TableFlags = dataio.Flags(
                UINT32, (
                    (0, 1, Split), 'splitPage',
                    2, 'repeatHeaderRow',
                    ))
        ZoneInfo = ARRAY(UINT16, 5)
        def getFields(self):
            yield self.TableFlags, 'attr'
            yield UINT16, 'nRows'
            yield UINT16, 'nCols'
            yield HWPUNIT16, 'cellspacing'
            yield ARRAY(HWPUNIT16, 4), 'padding'
            yield ARRAY(UINT16, self.nRows), 'rowSizes'
            yield UINT16, 'borderFillId'
            if doc.header.version > (5, 0, 0, 6):
                yield N_ARRAY(UINT16, self.ZoneInfo), 'validZones' # above 5006
        def __repr__(self):
            return 'TableBody\n'+'\n'.join([ ' - %s = %s'%(name, repr(getattr(self, name))) for type, name in self.getFields()])

        def __init__(self):
            self.cells = []

    class CommonControl(Control):
        Flow = dataio.Enum(
            FLOAT  = 0,
            BLOCK  = 1,
            BACK   = 2,
            FRONT  = 3,
            )

        TextSide = dataio.Enum(
            BOTH = 0,
            LEFT = 1,
            RIGHT = 2,
            LARGER = 3,
            )

        HorzAlign = dataio.Enum(
            LEFT = 0,
            CENTER = 1,
            RIGHT = 2,
            INSIDE = 3,
            OUTSIDE = 4,
            )

        HorzRelTo = dataio.Enum(
            PAPER = 0,
            PAGE = 1,
            COLUMN = 2,
            PARAGRAPH = 3,
            )

        VertRelTo = dataio.Enum(
            PAPER = 0,
            PAGE = 1,
            PARAGRAPH = 2,
            )

        VertAlign = dataio.Enum(
            TOP = 0,
            CENTER = 1,
            BOTTOM = 2,
            INSIDE = 3,
            OUTSIDE = 4,
            )

        WidthRelTo = dataio.Enum(
                PAPER = 0,
                PAGE = 1,
                COLUMN = 2,
                PARAGRAPH = 3,
                ABSOLUTE = 4)

        HeightRelTo = dataio.Enum(
                PAPER = 0,
                PAGE = 1,
                ABSOLUTE = 2,
                )

        NumberCategory = dataio.Enum(
                NONE = 0,
                FIGURE = 1,
                TABLE = 2,
                EQUATION = 3,
                )

        CommonControlFlags = dataio.Flags(UINT32, (
                0, 'inline',
                2, 'affectsLineSpacing',
                (3, 4, VertRelTo), 'vertRelTo',
                (5, 7, VertAlign), 'vertAlign',
                (8, 9, HorzRelTo), 'horzRelTo',
                (10, 12, HorzAlign), 'horzAlign',
                13, 'restrictedInPage',
                14, 'overwrapWithOtherObjects',
                (15, 17, WidthRelTo), 'widthRelTo',
                (18, 19, HeightRelTo), 'heightRelTo',
                20, 'protectedSizeWhenVertRelToParagraph',
                (21, 23, Flow), 'flow',
                (24, 25, TextSide), 'textSide',
                (26, 27, NumberCategory), 'numberCategory'
                ))

        MARGIN_LEFT = 0
        MARGIN_RIGHT = 1
        MARGIN_TOP = 2
        MARGIN_BOTTOM = 3
        def getFields(self):
            for x in Control.getFields(self):
                yield x
            yield self.CommonControlFlags, 'flags',
            yield SHWPUNIT, 'offsetY',    # DIFFSPEC
            yield SHWPUNIT, 'offsetX',    # DIFFSPEC
            yield HWPUNIT, 'width',
            yield HWPUNIT, 'height',
            yield INT16, 'zOrder',
            yield INT16, 'unknown1',
            yield ARRAY(HWPUNIT16, 4), 'margin',
            yield UINT32, 'instanceId',
            if doc.header.version > (5, 0, 0, 4):
                yield INT16, 'unknown2',
                yield BSTR, 'description'
        def __repr__(self):
            return ('%s\n'%self.__class__.__name__)+'\n'.join([ ' - %s = %s'%(name, repr(getattr(self, name))) for type, name in self.getFields()])

    class Table(CommonControl):
        chid = 'tbl '
        caption = None
        body = None
        def getSubModeler(self, rec):
            tagid = rec.tagid
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
        def appendCellParagraph(self, paragraph):
            self.body.cells[-1].paragraphs.append(paragraph)

        def getRows(self):
            return itertools.groupby(self.body.cells,
                    lambda x: x.row)

        def getCell(self, r, c):
            for cell in self.body.cells:
                if cell.row <= r and r < cell.row + cell.rowspan:
                    if cell.col <= c and c < cell.col + cell.colspan:
                        return cell

        def getPagedRows(self):
            for row, row_cells in self.getRows():
                paged_row = []
                for cell in row_cells:
                    for paragraphs in cell.getPages():
                        paged_row.append(paragraphs)
                yield paged_row

    Control.addsubtype(Table)

    class GShapeObject(CommonControl):
        chid = 'gso '
        def getSubModeler(self, rec):
            tagid = rec.tagid
            if tagid == HWPTAG_SHAPE_COMPONENT:
                # GShapeObject의 직할 ShapeComponent는 일반 ShapeComponent과 디코딩 방법이 다름
                return PrimaryShapeComponent, 'shapecomponent'
    Control.addsubtype(GShapeObject)

    class SectionDef(Control):
        chid = 'secd'
        def getFields(self):
            for x in Control.getFields(self):
                yield x
            yield UINT32, 'attr',
            yield HWPUNIT16, 'intercolumnSpacing',
            yield HWPUNIT16, 'verticalAlignment',
            yield HWPUNIT16, 'horizontalAlignment',
            yield HWPUNIT, 'defaultTabStops',
            yield UINT16, 'numberingShapeId',
            yield UINT16, 'startingPageNumber',
            yield UINT16, 'startingPictureNumber',
            yield UINT16, 'startingTableNumber',
            yield UINT16, 'startingEquationNumber',
            if doc.header.version > (5, 0, 1, 6):
                yield UINT32, 'unknown1', # above 5016
                #yield UINT32, 'unknown2',

        def __init__(self):
            self.pages = []
            self.footnoteShapes = []
            self.pageBorderFills = []

        def getSubModeler(self, rec):
            if rec.tagid == HWPTAG_PAGE_DEF:
                return PageDef, self.pages.append
            elif rec.tagid == HWPTAG_FOOTNOTE_SHAPE:
                return FootnoteShape, self.footnoteShapes.append
            elif rec.tagid == HWPTAG_PAGE_BORDER_FILL:
                return PageBorderFill, self.pageBorderFills.append
            elif rec.tagid == HWPTAG_CTRL_DATA:
                return SectionDefData, 'data'
    Control.addsubtype(SectionDef)

    # samples-local / 5024
    class SectionDefData:
        def getFields(self):
            yield BYTESTREAM, 'unknownbytes'

    class ColumnsDef(Control):
        chid = 'cold'
        def getFields(o):
            for x in Control.getFields(o):
                yield x
            yield UINT16, 'attr'
            yield HWPUNIT16, 'spacing'
            if not o.sameWidths:
                yield ARRAY(WORD, o.count), 'widths'
            yield UINT16, 'attr2'
            yield Border, 'splitterStyle'

        def kind(self):
            return self.attr & 3
        kind = property(kind)

        def count(self):
            return (self.attr >> 2) & 0xff
        count = property(count)

        def direction(self):
            return (self.attr >> 10) & 3
        direction = property(direction)

        def sameWidths(self):
            return (self.attr & 4096) != 0
        sameWidths = property(sameWidths)
    Control.addsubtype(ColumnsDef)

    class NumberingControl(Control):
        Kind = dataio.Enum(
                PAGE = 0,
                FOOTNOTE = 1,
                ENDNOTE = 2,
                PICTURE = 3,
                TABLE = 4,
                EQUATION = 5,
                )
        Flags = dataio.Flags(UINT32, (
                (0, 3, Kind), 'kind',
                (4, 11), 'footnoteShape',
                12, 'superscript',
                ))
        def getFields(self):
            for x in Control.getFields(self):
                yield x
            yield self.Flags, 'flags',
            yield UINT16, 'number',
    class AutoNumbering(NumberingControl):
        chid = 'atno'
        def getFields(self):
            for x in NumberingControl.getFields(self):
                yield x
            yield WCHAR, 'usersymbol',
            yield WCHAR, 'prefix',
            yield WCHAR, 'suffix',
        def __unicode__(self):
            prefix = u''
            suffix = u''
            if self.flags.kind == self.Kind.FOOTNOTE:
                if self.suffix != u'\x00':
                    suffix = self.suffix
            return prefix + unicode(self.number) + suffix
    Control.addsubtype(AutoNumbering)

    class NewNumbering(NumberingControl):
        chid = 'nwno'
        def getFields(self):
            for x in Control.getFields(self):
                yield x
    Control.addsubtype(NewNumbering)

    class PageNumberPosition(Control):
        ''' 4.2.10.9. 쪽 번호 위치 '''
        chid = 'pgnp'
        Position = dataio.Enum(
                NONE = 0,
                TOP_LEFT = 1,
                TOP_CENTER = 2,
                TOP_RIGHT = 3,
                BOTTOM_LEFT = 4,
                BOTTOM_CENTER = 5,
                BOTTOM_RIGHT = 6,
                OUTSIDE_TOP = 7,
                OUTSIDE_BOTTOM = 8,
                INSIDE_TOP = 9,
                INSIDE_BOTTOM = 10,
            )
        Flags = dataio.Flags(UINT32, (
            (0, 7), 'shape',
            (8, 11, Position), 'position',
            ))
        def getFields(self):
            for x in Control.getFields(self):
                yield x
            yield self.Flags, 'pagenumberflags'
            yield WCHAR, 'usersymbol'
            yield WCHAR, 'prefix'
            yield WCHAR, 'suffix'
            yield WCHAR, 'dash'
    Control.addsubtype(PageNumberPosition)

    class Header(Control):
        ''' 머리말 '''
        chid = 'head'
        def getSubModeler(self, rec):
            if rec.tagid == HWPTAG_LIST_HEADER:
                return ListHeader, 'listhead'
            if rec.tagid == HWPTAG_PARA_HEADER:
                return Paragraph, self.listhead.paragraphs.append
    Control.addsubtype(Header)

    class Footer(Control):
        ''' 꼬리말 '''
        chid = 'foot'
        def getSubModeler(self, rec):
            if rec.tagid == HWPTAG_LIST_HEADER:
                return ListFooter, 'listhead'
            if rec.tagid == HWPTAG_PARA_HEADER:
                return Paragraph, self.listhead.paragraphs.append
    Control.addsubtype(Footer)

    class FootNote(Control):
        ''' 각주 '''
        chid = 'fn  '
        def getSubModeler(self, rec):
            tagid = rec.tagid
            if tagid == HWPTAG_LIST_HEADER:
                return ListHeader, 'listhead'
            if tagid == HWPTAG_PARA_HEADER:
                return Paragraph, self.listhead.paragraphs.append
        def getAutoNumber(self):
            for paragraph in self.listhead.paragraphs:
                for elem in paragraph.getElementsWithControl():
                    if isinstance(elem.control, AutoNumbering):
                        return elem.control
    Control.addsubtype(FootNote)

    class EndNote(Control):
        ''' 미주 '''
        chid = 'en  '
        def getSubModeler(self, rec):
            tagid = rec.tagid
            if tagid == HWPTAG_LIST_HEADER:
                return ListHeader, 'listhead'
            if tagid == HWPTAG_PARA_HEADER:
                return Paragraph, self.listhead.paragraphs.append
    Control.addsubtype(EndNote)

    class Field(Control):
        pass

    class FieldHyperLink(Field):
        chid = '%hlk'
        Flags = dataio.Flags(UINT32, (
                0, 'editableInReadOnly',
                (11, 14), 'visitedType',
                15, 'modified',
                ))
        def getFields(self):
            for x in Control.getFields(self):
                yield x
            yield self.Flags, 'flags',
            yield BYTE, 'extra_attr',
            yield BSTR, 'command',
            yield UINT32, 'id',
        def geturl(self):
            s = self.command.split(';')
            return s[0].replace('\\:', ':')
        def __repr__(self):
            return '\n'.join(['- %s: %s'%(name, repr(getattr(self, name))) for type, name in self.getFields()])
    Control.addsubtype(FieldHyperLink)

    class BookmarkData:
        def getFields(self):
            yield UINT32, 'unknown1'
            yield UINT32, 'unknown2'
            yield UINT16, 'unknown3'
            yield BSTR, 'name'
        def __repr__(self):
            return '%s\n'%self.__class__.__name__+'\n'.join([ ' - %s = %s'%(name, repr(getattr(self, name))) for type, name in self.getFields()])
    class Bookmark(Control):
        chid = 'bokm'
        def getSubModeler(self, rec):
            if rec.tagid == HWPTAG_CTRL_DATA:
                return BookmarkData, 'data'
    Control.addsubtype(Bookmark)

    class ParaCharShape(list):
        def __init__(self, size):
            self.size = size
        def parse(self, f):
            for i in xrange(0, self.size):
                pos = UINT32.parse(f)
                charShapeId = UINT32.parse(f)
                self.append((pos, charShapeId))
            return self

    class Paragraph:
        def __init__(self):
            self.textdata = None
            self.charShapes = None
            self.controls = {}
            self.sectionDef = None

        SplitFlags = dataio.Flags(BYTE, (
                0, 'section',
                1, 'multicolumn',
                2, 'page',
                3, 'column',
                ))
        ControlMask = dataio.Flags(UINT32, (
                2, 'unknown1',
                11, 'control',
                21, 'new_number',
                ))
        Flags = dataio.Flags(UINT32, (
                31, 'unknown',
                (0, 30), 'chars',
                ))
        def getFields(self):
            yield self.Flags, 'text',
            yield self.ControlMask, 'controlMask',
            yield UINT16, 'paragraphShapeId',
            yield BYTE, 'styleId',
            yield self.SplitFlags, 'split',
            yield UINT16, 'characterShapeCount',
            yield UINT16, 'rangeTagCount',
            yield UINT16, 'nLineSegs',
            yield UINT32, 'instanceId',
        def __repr__(self):
            return 'Paragraph\n'+'\n'.join([ ' - %s = %s'%(name, repr(getattr(self, name))) for type, name in self.getFields()])

        def getSubModeler(paragraph, rec):
            tagid = rec.tagid
#            if tagid == HWPTAG_PARA_TEXT:
#                return ParaText, 'textdata'
#            if tagid == HWPTAG_PARA_CHAR_SHAPE:
#                return ParaCharShape, 'charShapes'
            if tagid == HWPTAG_CTRL_HEADER:
                Model = Control.getsubtype(rec)
                return Model, paragraph.addControl
#            if tagid == HWPTAG_PARA_LINE_SEG:
#                class ParaLineSeg:
#                    def getFields(self):
#                        yield ARRAY(LineSeg, paragraph.nLineSegs), 'lineSegs'
#                #return ARRAY(LineSeg, paragraph.nLineSegs), 'lineSegs'
#                return ParaLineSeg, 'lineSegs'
        def addsubrec(paragraph, rec):
            if rec.tagid == HWPTAG_PARA_TEXT:
                paragraph.textdata = ParaText()
                paragraph.textdata.decode(rec.bytes)
                paragraph.textdata.record = rec
                rec.model = paragraph.textdata
            elif rec.tagid == HWPTAG_PARA_CHAR_SHAPE:
                paragraph.charShapes = ParaCharShape(paragraph.characterShapeCount)
                paragraph.charShapes.parse(rec.bytestream())
                paragraph.charShapes.record = rec
                rec.model = paragraph.charShapes
            elif rec.tagid == HWPTAG_PARA_LINE_SEG:
                paragraph.lineSegs = ARRAY(LineSeg, paragraph.nLineSegs)
                paragraph.lineSegs.parse(rec.bytestream())
                paragraph.lineSegs.record = rec
                rec.model = paragraph.lineSegs

        def getElementsWithControl(self):
            if self.textdata is None:
                return
            ctrliters = {}
            for elem in self.textdata.getElements():
                if isinstance(elem, doc.ControlChar) and elem.kind == elem.extended:
                    controls = self.controls.get(elem.chid, None)
                    if controls is not None:
                        ctrliter = ctrliters.setdefault( elem.chid, iter(controls) )
                        try:
                            elem.control = ctrliter.next()
                        except StopIteration:
                            logging.fatal('can\'t find control')
                yield elem

        def getSegmentedElements(self, elemiter, segments):
            try:
                elem = elemiter.next()
                for (segmentstart, segmentend, segmentid) in segments:
                    if segmentstart == segmentend: continue
                    #logging.debug('RANGE = (%s~%s) with %s'%(segmentstart, segmentend, segmentid))
                    while True:
                        elemstart = elem.charoffset
                        elemend = elem.charoffset + len(elem)
                        if elemstart == elemend:
                            elem = elemiter.next()
                            continue
                        #logging.debug('ELEM = (%s,%s) %s'%(elemstart, elemend, elem))
                        if elemend <= segmentstart:
                            elem = elemiter.next()
                            continue
                        if elemstart < segmentstart and segmentstart < elemend:
                            # split Text
                            if isinstance(elem, Text):
                                split_pos = segmentstart - elemstart
                                prev, next = elem.split(split_pos)
                                yield prev, segmentid
                                elem = next
                                #logging.debug('SPLIT: %s / %s'%(prev, next))
                                continue
                            else:
                                logging.warning('element %s is over ParaCharShape (%d~%d, %d)'%(repr(elem), segmentstart, segmentend, segmentid))
                        if segmentstart <= elemstart and elemend <= segmentend:
                            #logging.debug('APPLIED: %s'%elem)
                            yield elem, segmentid
                            elem = elemiter.next()
                            continue
                        if elemstart < segmentend and segmentend < elemend:
                            assert(segmentstart <= elemstart)
                            if isinstance(elem, Text):
                                split_pos = segmentend - elemstart
                                prev, next = elem.split(split_pos)
                                yield prev, segmentid
                                #logging.debug('SPLIT2: %s / %s'%(prev, next))
                                elem = next
                                continue
                            else:
                                logging.warning('element %s is over ParaCharShape (%d~%d, %d)'%(repr(elem), segmentstart, segmentend, segmentid))
                        if segmentend <= elemstart:
                            break # next shape
            except StopIteration:
                pass
            except KeyboardInterrupt:
                logging.error( self.record )
                logging.error( 'elem: (%s - %s) %s'%(elemstart, elemend, elem) )
                logging.error( 'segment: (%s - %s) %s'%(segmentstart, segmentend, segmentid) )
                raise

        def getCharShapeSegments(self):
            if self.textdata is None:
                return
            start = None
            shapeid = None
            for (pos, next_shapeid) in self.charShapes:
                if start is not None:
                    yield start, pos, shapeid
                start = pos
                shapeid = next_shapeid
            if start is not None:
                end = len(self.textdata.record.bytes)/2
                if end > 0:
                    yield start, end, shapeid

        def getShapedElements(self):
            if self.textdata is None:
                return
            elements = self.exclude_last_paragraph_break(self.getElementsWithControl())
            for elem, charShapeId in self.getSegmentedElements(elements, self.getCharShapeSegments()):
                elem.charShapeId = charShapeId
                yield elem

        def getLineSegments(self):
            if self.textdata is None:
                return
            start = None
            lineseg = None
            for lineno, next_lineseg in enumerate(self.lineSegs):
                pos = next_lineseg.chpos
                if start is not None:
                    lineseg.number_in_paragraph = lineno-1
                    yield start, pos, lineseg
                start = pos
                lineseg = next_lineseg
            if start is not None:
                end = len(self.textdata.record.bytes)/2
                if end > 0:
                    lineseg.number_in_paragraph = lineno
                    yield start, end, lineseg

        def getLinedElements(self):
            elements = self.getShapedElements()
            for elem, lineSeg in self.getSegmentedElements(elements, self.getLineSegments()):
                yield elem, lineSeg

        def getLines(self):
            elements = self.getShapedElements()
            return groupby_mapfunc(self.getSegmentedElements(elements, self.getLineSegments()),
                    lambda (elem, lineSeg): lineSeg,
                    lambda (elem, lineSeg): elem)

        def getPagedLines(paragraph, page=0, prev_line=None):
            for line, line_elements in paragraph.getLines():
                if prev_line is not None:
                    if line.offsetY <= prev_line.offsetY:
                        page += 1
                prev_line = line
                yield page, line, line_elements
        def getPages(self, page, prev_line):
            for page, page_lines in groupby_mapfunc(self.getPagedLines(page, prev_line),
                    lambda (page, line, line_elements): page,
                    lambda (page, line, line_elements): (line, line_elements)):
                yield (page, page_lines)

        def exclude_last_paragraph_break(self, elements):
            prev = None
            for elem in elements:
                if prev is not None:
                    yield prev
                prev = elem
            if prev is not None:
                if not isinstance(prev, ControlChar) or not prev.ch == ControlChar.PARAGRAPH_BREAK:
                    yield prev

        def addControl(self, ctrl):
            chid = getattr(ctrl, 'chid', None)
            if chid is not None:
                self.controls.setdefault(ctrl.chid, []).append(ctrl)
                ctlchs = [c for c in self.textdata.controlchars_by_chid(chid)]
                ctlchs[ len(self.controls[ctrl.chid])-1 ].control = ctrl

        def __getattr__(paragraph, name):
            if name == 'style':
                style = doc.docinfo.mappings[doc.Style][paragraph.styleId]
                style.paragraphShape = doc.docinfo.mappings[doc.ParaShape][style.paragraphShapeId]
                style.characterShape = doc.docinfo.mappings[doc.CharShape][style.characterShapeId]
                return style
            elif name == 'paragraphShape':
                return doc.docinfo.mappings[doc.ParaShape][paragraph.paragraphShapeId]
            raise AttributeError(name)

    class Section(RecordsContainer):
        def __init__(self):
            RecordsContainer.__init__(self)
            self.paragraphs = []

        def getPages(self, factory):
            page = factory.Page()
            paragraph = None
            line = None
            for ev, param in getElementEvents(self.paragraphs):
                if ev == EV_PAGE:
                    if page is not None:
                        yield page
                    page = factory.Page()
                elif ev == EV_PARAGRAPH:
                    paragraph = page.Paragraph(param)
                    page.append(paragraph)
                elif ev == EV_LINE:
                    line = paragraph.Line(param)
                    paragraph.append(line)
                elif ev == EV_ELEMENT:
                    line.append(line.Element(param))
            if page is not None:
                yield page

        def getSubModeler(self, rec):
            tagid = rec.tagid
            if tagid == HWPTAG_PARA_HEADER:
                return Paragraph, self.paragraphs.append
        def getSectionDef(self):
            paragraph = self.paragraphs[0]
            for e in paragraph.getElementsWithControl():
                if isinstance(e, ControlChar) and e.ch == ControlChar.SECTION_COLUMN_DEF:
                    if isinstance(e.control, SectionDef):
                        return e.control
        sectionDef = property(getSectionDef)
        def getColumnsDef(self):
            paragraph = self.paragraphs[0]
            for e in paragraph.getElementsWithControl():
                if isinstance(e, ControlChar) and e.ch == ControlChar.SECTION_COLUMN_DEF:
                    if isinstance(e.control, ColumnsDef):
                        return e.control
        columnsDef = property(getColumnsDef)

    class DocInfo(RecordsContainer):
        def getSubModeler(self, rec):
            tagid = rec.tagid
            if tagid == HWPTAG_ID_MAPPINGS:
                return IdMappings, 'mappings'
            elif tagid == HWPTAG_DOCUMENT_PROPERTIES:
                return DocumentProperties, 'documentProperties'
            elif tagid == HWPTAG_DOC_DATA:
                return DocData, 'docData'

    for name, v in dict(locals()).iteritems():
        if (name not in ['doc', 'inch2mm', 'inch2px', 'hwp2inch', 'hwp2mm', 'hwp2px', 'hwp2pt']) and not isinstance(v, str):
            fixup_parse(v)
    del name, v

    return locals()

EV_PAGE = 0
EV_PARAGRAPH = 1
EV_LINE = 2
EV_ELEMENT = 3
def getElementEvents(paragraphs):
    prev_line = None
    line = None
    for paragraph in paragraphs:
        splitted_by_paragraph_flag = False
        if paragraph.split.page:
            yield EV_PAGE, None
            splitted_by_paragraph_flag = True
        yield EV_PARAGRAPH, paragraph

        for elem, line_of_elem in paragraph.getLinedElements():
            if line != line_of_elem:
                # new line
                line = line_of_elem
                if prev_line is not None:
                    if line.offsetY <= prev_line.offsetY:
                        if not splitted_by_paragraph_flag:
                            yield EV_PAGE, None
                            yield EV_PARAGRAPH, paragraph

                yield EV_LINE, line
                prev_line = line

            yield EV_ELEMENT, elem

        for table in paragraph.controls.get(CHID.TABLE, []):
            pass

def groupby_mapfunc(sequence, keyfunc, grouper_mapfunc):
    for key, grouper in itertools.groupby(sequence, keyfunc):
        yield key, itertools.imap(grouper_mapfunc, grouper)


def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(itertools.islice(iterable, n, None), default)

def merge_iterators(*iterators):
    n = len(iterators)
    while n > 0:
        x = ()
        for idx, iterator in enumerate(iterators):
            if iterator is not None:
                try:
                    x += (iterator.next(), )
                except StopIteration:
                    x += (None, )
                    n -= 1
            else:
                x += (None, )
        yield x

def getPagedLines(paragraphs):
    page = 0
    prev_line = None
    line = None
    for paragraph in paragraphs:
        if paragraph.split.page:
            page += 1
            prev_line = None

        for line, line_elements in paragraph.getLines():
            if prev_line is not None:
                if line.offsetY <= prev_line.offsetY:
                    page += 1
            prev_line = line
            yield page, paragraph, line, line_elements

def groupByPage(paged_lines):
    for page, page_lines in groupby_mapfunc(paged_lines,
            lambda (page, paragraph, line, line_elements): page,
            lambda (page, paragraph, line, line_elements): (paragraph, line, line_elements)):
        yield groupByParagraph(page_lines)

def groupByParagraph(page_lines):
    for paragraph, paragraph_lines in groupby_mapfunc(page_lines,
            lambda (paragraph, line, line_elements): paragraph,
            lambda (paragraph, line, line_elements): (line, line_elements)):
        yield paragraph, paragraph_lines

def getPagedParagraphs_x(paragraphs):
    page = 0
    prev_line = None
    for paragraph in paragraphs:
        if paragraph.split.page:
            page += 1
            prev_line = None

        for (page, lines) in paragraph.getPages(page, prev_line):
            for line, line_elements in lines:
                prev_line = line
                yield page, paragraph, line, line_elements

'''
usage:
    for paragraphs in getPagedParagraphs(section.paragraphs):
        for (paragraph, paragraph_lines) in paragraphs:
            for (line, line_elements) in paragraph_lines:
                pass
'''
def getPagedParagraphs(paragraphs):
    return groupByPage(getPagedParagraphs_x(paragraphs))

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
                            strm = StringIO(zlib.decompress(strm.read(), -15)) # without gzip header
                        return strm
                    elif name == 'section':
                        class SectionStreams:
                            def __getitem__(sectionstreams, idx):
                                try:
                                    sec = self.openstream('BodyText/Section'+str(idx))
                                    if self.header.flags.compressed:
                                        sec = StringIO(zlib.decompress(sec.read(), -15))
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
                                        strm = StringIO(zlib.decompress(strm.read(), -15))
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
            header = FileHeader.parse(self.streams.fileheader)
            self.__dict__[name] = header
            return header
        elif name == 'docinfo':
            docinfo = self.DocInfo()
            buildModelTree(docinfo, self.streams.docinfo)
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
                sect.idx = idx
                buildModelTree(sect, self.streams.section[idx])
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
