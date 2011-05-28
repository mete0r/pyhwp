# -*- coding: utf-8 -*-
import logging
from .dataio import *
from .utils import cached_property
from .tagids import *
from . import dataio

class Element(object):
    def __init__(self, context, attributes):
        self.__dict__.update(attributes)
        self.context = context


class BasicElement(Element):
    def attributes(context):
        if False: yield
    attributes = staticmethod(attributes)
    parse_pass1 = classmethod(parse_model_attributes)


class AttributeDeterminedElement(BasicElement):
    key_attribute = None
    def concrete_type_by_attribute(cls, key_attribute_value):
        raise Exception()
    concrete_type_by_attribute = classmethod(concrete_type_by_attribute)

    def parse_pass1(model, attributes, context, stream):
        model, attributes = parse_model_attributes(model, attributes, context, stream)
        altered_model = model.concrete_type_by_attribute(attributes[model.key_attribute])
        if altered_model is not None:
            return parse_model_attributes(altered_model, attributes, context, stream)
        return model, attributes
    parse_pass1 = classmethod(parse_pass1)


class DocumentProperties(BasicElement):
    def attributes(context):
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
    attributes = staticmethod(attributes)


class IdMappings(BasicElement):
    def attributes(context):
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
        if context['version'] >= (5, 0, 1, 7):
            yield ARRAY(UINT32, 8), 'unknown' # SPEC
    attributes = staticmethod(attributes)


class BinData(AttributeDeterminedElement):
    def attributes(context):
        yield UINT16, 'flags'
    attributes = staticmethod(attributes)

    key_attribute = 'flags'
    def concrete_type_by_attribute(cls, flags):
        return [BinLink, BinEmbedded, BinStorage][flags & 3]
    concrete_type_by_attribute = classmethod(concrete_type_by_attribute)


class BinLink(BinData):
    def attributes(context):
        yield BSTR, 'abspath'
        yield BSTR, 'relpath'
    attributes = staticmethod(attributes)


class BinEmbedded(BinData):
    def attributes(context):
        yield UINT16, 'storageId'
        yield BSTR, 'ext'
    attributes = staticmethod(attributes)

    def get_name(self):
        return 'BIN%04X.%s'%(self.storageId, self.ext) # DIFFSPEC
    name = property(get_name)

    def open_stream(self):
        return self.context.open_bindata(self.name)
    stream = property(open_stream)


class BinStorage(BinData):
    def attributes(context):
        yield UINT16, 'storageId'
    attributes = staticmethod(attributes)


class AlternateFont(BasicModel):
    def attributes(context):
        yield BYTE, 'kind'
        yield BSTR, 'name'
    attributes = staticmethod(attributes)


class Panose1(BasicModel):
    def attributes(context):
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
    attributes = staticmethod(attributes)


class FaceName(BasicElement):
    Flags = dataio.Flags(BYTE, (
        5, 'default',
        6, 'metric',
        7, 'alternate',
        ))
    def attributes(cls, context):
        attr = yield cls.Flags, 'attr'
        yield BSTR, 'fontName'
        if attr.alternate:
            yield AlternateFont, 'alternateFont'
        if attr.metric:
            yield Panose1, 'panose1'
        if attr.default:
            yield BSTR, 'defaultFontName'
    attributes = classmethod(attributes)


class Border(BasicModel):
    def attributes(context):
        yield UINT8, 'style',
        yield UINT8, 'width',
        yield COLORREF, 'color',
    attributes = staticmethod(attributes)


class Fill(BasicModel):
    def attributes(context):
        raise Exception('Not implemented')
    attributes = staticmethod(attributes)


class FillNone(Fill):
    def attributes(context):
        yield UINT32, 'size', # SPEC is confusing
    attributes = staticmethod(attributes)


class FillColorPattern(Fill):
    def attributes(context):
        yield COLORREF, 'backgroundColor',
        yield COLORREF, 'patternColor',
        yield UINT32, 'patternType',
        yield UINT32, 'unknown',
    attributes = staticmethod(attributes)


class FillGradation(Fill):
    def attributes(context):
        yield BYTE,   'type',
        yield UINT32, 'shear',
        yield UINT32, 'centerX',
        yield UINT32, 'centerY',
        yield UINT32, 'blur',
        yield N_ARRAY(UINT32, COLORREF), 'colors',
        yield UINT32, 'shape',
        yield BYTE,   'blurCenter',
    attributes = staticmethod(attributes)


class BorderFill(BasicElement):
    FILL_NONE = 0
    FILL_COLOR_PATTERN = 1
    FILL_GRADATION = 4
    def attributes(cls, context):
        yield UINT16, 'attr'
        yield ARRAY(Border, 4), 'border' # DIFFSPEC
        yield Border, 'slash'
        filltype = yield UINT32, 'fillType'
        if filltype == cls.FILL_NONE:
            yield FillNone, 'fill'
        elif filltype == cls.FILL_COLOR_PATTERN:
            yield FillColorPattern, 'fill'
        elif filltype == cls.FILL_GRADATION:
            yield FillGradation, 'fill'
    attributes = classmethod(attributes)


class CharShape(BasicElement):
    def attributes(context):
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
    attributes = staticmethod(attributes)

    ITALIC  = 0x00000001
    BOLD    = 0x00000002
    UNDERLINE_MASK  = 0x0000000C
    UNDERLINE_NONE  = 0x00000000
    UNDERLINE       = 0x00000004
    UPPERLINE       = 0x0000000C
    UNDERLINE_LINESTYLE_MASK    = 0x000000F0
    OUTLINE_MASK    = 0x000000700
    SHADOW_MASK     = 0x000003800


class TabDef(BasicElement):
    def attributes(context):
        # SPEC is confusing
        if context['version'] == (5, 0, 1, 7):
            yield UINT32, 'unknown1'
            yield UINT32, 'unknown2'
        #yield UINT32, 'attr',
        #yield UINT16, 'count',
        #yield HWPUNIT, 'pos',
        #yield UINT8, 'kind',
        #yield UINT8, 'fillType',
        #yield UINT16, 'reserved',
    attributes = staticmethod(attributes)


class Numbering(BasicElement):
    Align = dataio.Enum(LEFT=0, CENTER=1, RIGHT=2)
    DistanceType = dataio.Enum(RATIO=0, VALUE=1)
    Flags = dataio.Flags(UINT32, (
        (0, 1, Align), 'paragraphAlign',
        2, 'autowidth',
        3, 'autodedent',
        (4, 4, DistanceType), 'distance_to_body_type',
        ))
    def attributes(cls, context):
        yield cls.Flags, 'flags'
        yield HWPUNIT16, 'width_correction'
        yield HWPUNIT16, 'distance_to_body'
        yield UINT32, 'charShapeId' # SPEC ?????
    attributes = classmethod(attributes)
        

class Bullet(BasicElement):
    pass


class ParaShape(BasicElement):
    Flags = dataio.Flags(UINT32, (
            (0, 1), 'lineSpacingType',
            (2, 4), 'textAlign',
            # TODO
            ))
    def attributes(cls, context):
        yield cls.Flags, 'attr1',
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
        if context['version'] > (5, 0, 1, 6):
            yield UINT32, 'attr2',       # above 5016
            #yield UINT32, 'attr3',       # DIFFSPEC
            #yield UINT32, 'lineSpacing', # DIFFSPEC
    attributes = classmethod(attributes)


class Style(BasicElement):
    def attributes(context):
        yield BSTR, 'localName',
        yield BSTR, 'name',
        yield BYTE, 'attr',
        yield BYTE, 'nextStyleId',
        yield INT16, 'langId',
        yield UINT16, 'paragraphShapeId',
        yield UINT16, 'characterShapeId',
        if context['version'] >= (5, 0, 1, 7):
            pass
            #yield UINT16, 'unknown' # SPEC
    attributes = staticmethod(attributes)


class DocData(BasicElement):
    pass


class DistributeDocData(BasicElement):
    pass


class CompatibleDocument(BasicElement):
    Target = dataio.Enum(DEFAULT=0, HWP2007=1, MSWORD=2)
    def attributes(context):
        yield Target, 'target'
    attributes = staticmethod(attributes)


class LayoutCompatibility(BasicElement):
    def attributes(context):
        yield UINT32, 'char',
        yield UINT32, 'paragraph',
        yield UINT32, 'section',
        yield UINT32, 'object',
        yield UINT32, 'field',
    attributes = staticmethod(attributes)


class CHID(object):
    GSO = 'gso '
    SECD = 'secd'
    COLD = 'cold'
    ATNO = 'atno'
    NWNO = 'nwno'
    PGNP = 'pgnp'
    HEADER = 'head'
    FOOTER = 'foot'
    FN = 'fn  '
    EN = 'en  '
    HLK = '%hlk'
    BOKM = 'bokm'

    TBL = 'tbl '
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
    def decode(self, bytes):
        return bytes[3] + bytes[2] + bytes[1] + bytes[0]

    def read(self, f):
        bytes = readn(f, 4)
        return self.decode(bytes)

    def parse(self, f):
        return self, self.read( f )

    def __call__(self, value):
        return value

CHID = CHID()


class Control(AttributeDeterminedElement):
    def attributes(context):
        chid = yield CHID, 'chid'
    attributes = staticmethod(attributes)

    key_attribute = 'chid'
    def concrete_type_by_attribute(cls, chid):
        return cls.concrete_types.get(chid)
    concrete_type_by_attribute = classmethod(concrete_type_by_attribute)
    concrete_types = dict()
    def concrete_type(cls, chid):
        def wrapper(subclass):
            cls.concrete_types[chid] = subclass
            return subclass
        return wrapper
    concrete_type = classmethod(concrete_type)


class MarginPadding(BasicModel):
    def attributes(context):
        yield HWPUNIT16, 'left'
        yield HWPUNIT16, 'right'
        yield HWPUNIT16, 'top'
        yield HWPUNIT16, 'bottom'
    attributes = staticmethod(attributes)


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
    def attributes(cls, context):
        yield cls.CommonControlFlags, 'flags',
        yield SHWPUNIT, 'offsetY',    # DIFFSPEC
        yield SHWPUNIT, 'offsetX',    # DIFFSPEC
        yield HWPUNIT, 'width',
        yield HWPUNIT, 'height',
        yield INT16, 'zOrder',
        yield INT16, 'unknown1',
        yield MarginPadding, 'margin',
        yield UINT32, 'instanceId',
        if context['version'] > (5, 0, 0, 4):
            yield INT16, 'unknown2',
            yield BSTR, 'description'
    attributes = classmethod(attributes)


class TableControl(CommonControl):
    def getBorderFill(self):
        return self.context.mappings[BorderFill][tbl.body.borderFillId - 1] # TODO: is this right?
    borderFill = property(getBorderFill)

    def parse_child(cls, attributes, context, child):
        child_context, child_model, child_attributes, child_stream = child
        if child_model is TableBody:
            context['table_body'] = True
        elif child_model is ListHeader:
            if context.get('table_body', False):
                return parse_model_attributes(TableCell, child_attributes, child_context, child_stream)
            else:
                return parse_model_attributes(TableCaption, child_attributes, child_context, child_stream)
        return child_model, child_attributes
    parse_child = classmethod(parse_child)
TableControl = Control.concrete_type(CHID.TBL)(TableControl)


class ListHeader(BasicElement):
    Flags = dataio.Flags(UINT32, (
        (0, 2), 'textdirection',
        (3, 4), 'linebreak',
        (5, 6), 'vertAlign',
        ))
    VALIGN_MASK     = 0x60
    VALIGN_TOP      = 0x00
    VALIGN_MIDDLE   = 0x20
    VALIGN_BOTTOM   = 0x40
    def attributes(cls, context):
        yield UINT16, 'nParagraphs',
        yield UINT16, 'unknown1',
        yield cls.Flags, 'listflags',
    attributes = classmethod(attributes)


class PageDef(BasicElement):
    Flags = dataio.Flags(UINT32, (
                    0, 'landscape',
                    (1, 2), 'bookcompilingStyle',
                    ))
    def attributes(cls, context):
        yield HWPUNIT, 'paper_width',
        yield HWPUNIT, 'paper_height',
        yield HWPUNIT, 'offsetLeft',
        yield HWPUNIT, 'offsetRight',
        yield HWPUNIT, 'offsetTop',
        yield HWPUNIT, 'offsetBottom',
        yield HWPUNIT, 'offsetHeader',
        yield HWPUNIT, 'offsetFooter',
        yield HWPUNIT, 'jebonOffset',
        yield cls.Flags, 'attr',
        #yield UINT32, 'attr',
    attributes = classmethod(attributes)

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


class FootnoteShape(BasicElement):
    Flags = dataio.Flags(UINT32, (
        ))
    def attributes(cls, context):
        yield cls.Flags, 'flags'
        yield WCHAR, 'usersymbol'
        yield WCHAR, 'prefix' 
        yield WCHAR, 'suffix' 
        yield WCHAR, 'starting_number'
        yield HWPUNIT16, 'splitterLength'
        yield HWPUNIT16, 'splitterMarginTop'
        yield HWPUNIT16, 'splitterMarginBottom'
        yield HWPUNIT16, 'notesSpacing'
        yield Border, 'splitterStyle'
        if context['version'] >= (5, 0, 0, 6):
            yield UINT16, 'unknown1' # TODO
    attributes = classmethod(attributes)


class PageBorderFill(BasicElement):
    Oriented = dataio.Enum(
            FROM_BODY = 0,
            FROM_PAPER = 1,
            )
    FillArea = dataio.Enum(
            PAPER = 0,
            PAGE = 1,
            BORDER = 2,
            )
    Flags = dataio.Flags(UINT32, (
        (0, 0, Oriented), 'oriented',
        1, 'include_header',
        2, 'include_footer',
        (3, 4, FillArea), 'fill_area',
        ))
    def attributes(cls, context):
        yield cls.Flags, 'flags'
        yield MarginPadding, 'margin'
        yield UINT16, 'borderFillId'
    attributes = classmethod(attributes)


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
    def attributes(cls, context):
        yield cls.CaptionFlags, 'captflags',
        yield HWPUNIT, 'width',
        yield HWPUNIT16, 'offset', # 캡션과 틀 사이 간격
        yield HWPUNIT, 'maxsize',
    attributes = classmethod(attributes)


class TableCell(ListHeader):
    def attributes(context):
        yield UINT16, 'col',
        yield UINT16, 'row',
        yield UINT16, 'colspan',
        yield UINT16, 'rowspan',
        yield HWPUNIT, 'width',
        yield HWPUNIT, 'height',
        yield MarginPadding, 'padding',
        yield UINT16, 'borderFillId',
        yield HWPUNIT, 'unknown_width',
    attributes = staticmethod(attributes)

    def getBorderFill(self):
        return context.mappings[BorderFill][self.borderFillId - 1] # TODO: is this right?
    borderFill = property(getBorderFill)


class TableBody(BasicElement):
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
    def attributes(cls, context):
        yield cls.TableFlags, 'attr'
        nRows = yield UINT16, 'nRows'
        yield UINT16, 'nCols'
        yield HWPUNIT16, 'cellspacing'
        yield MarginPadding, 'padding'
        yield ARRAY(UINT16, nRows), 'rowSizes'
        yield UINT16, 'borderFillId'
        if context['version'] > (5, 0, 0, 6):
            yield N_ARRAY(UINT16, cls.ZoneInfo), 'validZones' # above 5006
    attributes = classmethod(attributes)


class Paragraph(BasicElement):

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
    def attributes(cls, context):
        yield cls.Flags, 'text',
        yield cls.ControlMask, 'controlMask',
        yield UINT16, 'paragraphShapeId',
        yield BYTE, 'styleId',
        yield cls.SplitFlags, 'split',
        yield UINT16, 'characterShapeCount',
        yield UINT16, 'rangeTagCount',
        yield UINT16, 'nLineSegs',
        yield UINT32, 'instanceId',
    attributes = classmethod(attributes)


class ControlChar(object):
    class CHAR:
        size = 1
    class INLINE:
        size = 8
    class EXTENDED:
        size = 8
    chars = {
            0x00 : ('NULL', CHAR),
            0x01 : ('CTLCHR01', EXTENDED),
            0x02 : ('SECTION_COLUMN_DEF', EXTENDED),
            0x03 : ('FIELD_START', EXTENDED),
            0x04 : ('FIELD_END', INLINE),
            0x05 : ('CTLCHR05', INLINE),
            0x06 : ('CTLCHR06', INLINE),
            0x07 : ('CTLCHR07', INLINE),
            0x08 : ('TITLE_MARK', INLINE),
            0x09 : ('TAB', INLINE),
            0x0a : ('LINE_BREAK', CHAR),
            0x0b : ('DRAWING_TABLE_OBJECT', EXTENDED),
            0x0c : ('CTLCHR0C', EXTENDED),
            0x0d : ('PARAGRAPH_BREAK', CHAR),
            0x0e : ('CTLCHR0E', EXTENDED),
            0x0f : ('HIDDEN_EXPLANATION', EXTENDED),
            0x10 : ('HEADER_FOOTER', EXTENDED),
            0x11 : ('FOOT_END_NOTE', EXTENDED),
            0x12 : ('AUTO_NUMBER', EXTENDED),
            0x13 : ('CTLCHR13', INLINE),
            0x14 : ('CTLCHR14', INLINE),
            0x15 : ('PAGE_CTLCHR', EXTENDED),
            0x16 : ('BOOKMARK', EXTENDED),
            0x17 : ('CTLCHR17', EXTENDED),
            0x18 : ('HYPHEN', CHAR),
            0x1e : ('NONBREAK_SPACE', CHAR),
            0x1f : ('FIXWIDTH_SPACE', CHAR),
    }
    names = dict((unichr(code), name) for code, (name, kind) in chars.items())
    kinds = dict((unichr(code), kind) for code, (name, kind) in chars.items())
    def _populate(cls):
        for ch, name in cls.names.items():
            setattr(cls, name, ch)
    _populate = classmethod(_populate)
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

    __slots__ = ['ch', 'chid', 'param']
    def __init__(self, ch, chid=None, param=None):
        self.ch = ch
        self.chid = chid
        self.param = param
    def decode_bytes(cls, bytes):
        ch = dataio.decode_utf16le_besteffort(bytes[0:2])
        if cls.kinds[ch].size == 8:
            bytes = bytes[2:2+12]
            chid = CHID.decode(bytes[0:4])
            param = bytes[4:12]
            return cls(ch, chid, param)
        else:
            return cls(ch)
    decode_bytes = classmethod(decode_bytes)

    def kind(self):
        return self.kinds[self.ch].size
    kind = property(kind)

    def code(self):
        return ord(self.ch)
    code = property(code)

    def name(self):
        return self.names.get(self.ch, 'CTLCHR%02x'%self.code)
    name = property(name)

    def __len__(self):
        return self.kind.size

    def __repr__(self):
        return 'ControlChar(%s, %s, %s)'%( self.name, repr(self.chid), repr(self.param))
ControlChar._populate()

class Text(object):
    def split(self, pos):
        prev, next = Text(self[:pos]), Text(self[pos:])
        prev.byteoffset = self.byteoffset
        prev.charoffset = self.charoffset
        prev.charShapeId = self.charShapeId
        next.charoffset = self.charoffset + pos
        next.byteoffset = next.charoffset * 2
        next.charShapeId = self.charShapeId
        return prev, next
    def __call__(self, value):
        return value

Text = Text()

class ParaText(Element):
    def parse_with_parent(cls, context, parent, stream, attributes):
        text = parent[2]['text']
        nChars = Paragraph.Flags(text).chars
        bytes = stream.read()
        attributes['chunks'] = [x for x in cls.parseBytes(bytes)]
        return cls, attributes
    parse_with_parent = classmethod(parse_with_parent)

    def parseBytes(bytes):
        size = len(bytes)
        idx = 0
        while idx < size:
            ctrlpos, ctrlpos_end = ControlChar.find(bytes, idx)
            if idx < ctrlpos:
                yield (idx/2, ctrlpos/2), dataio.decode_utf16le_besteffort(bytes[idx:ctrlpos])
            if ctrlpos < ctrlpos_end:
                yield (ctrlpos/2, ctrlpos_end/2), ControlChar.decode_bytes(bytes[ctrlpos:ctrlpos_end])
            idx = ctrlpos_end
    parseBytes = staticmethod(parseBytes)


class ParaCharShape(Element):
    def parse_with_parent(cls, context, (parent_context, parent_model, parent_attributes, parent_stream), stream, attributes):
        nCharShapes = parent_attributes['characterShapeCount']
        attributes['charshapes'] = ARRAY(ARRAY(UINT32, 2), nCharShapes).read(stream)
        return cls, attributes
    parse_with_parent = classmethod(parse_with_parent)


class ParaLineSeg(Element):
    class LineSeg(BasicModel):
        def attributes(context):
            yield INT32, 'chpos',
            yield SHWPUNIT, 'offsetY',
            yield SHWPUNIT, 'a2',
            yield SHWPUNIT, 'height',
            yield SHWPUNIT, 'a3',
            yield SHWPUNIT, 'marginBottom',
            yield INT32, 'a4',
            yield ARRAY(SHWPUNIT, 2), 'a5',
        attributes = staticmethod(attributes)

    def parse_with_parent(cls, context, (parent_context, parent_model, parent_attributes, parent_stream), stream, attributes):
        nLineSegs = parent_attributes['nLineSegs']
        attributes['linesegs'] = ARRAY(cls.LineSeg, nLineSegs).read(stream)
        return cls, attributes
    parse_with_parent = classmethod(parse_with_parent)


class ParaRangeTag(BasicElement):
    def attributes(context):
        yield UINT32, start
        yield UINT32, end
        yield UINT32, tag
        # TODO: SPEC
    attributes = staticmethod(attributes)


class GShapeObjectControl(CommonControl):
    def parse_child(cls, attributes, context, (child_context, child_model, child_attributes, child_stream)):
        # TODO: ListHeader to Caption
        return child_model, child_attributes
    parse_child = classmethod(parse_child)
GShapeObjectControl = Control.concrete_type(CHID.GSO)(GShapeObjectControl)


class ScaleRotationMatrix(BasicModel):
    def attributes(context):
        yield Matrix, 'scaler',
        yield Matrix, 'rotator',
    attributes = staticmethod(attributes)

class ShapeComponent(Element):
    Flags = dataio.Flags(UINT32, (
            0, 'flip')
        )
    def attributes(cls, context):
        chid = yield CHID, 'chid'
        yield SHWPUNIT, 'xoffsetInGroup'
        yield SHWPUNIT, 'yoffsetInGroup'
        yield WORD, 'groupingLevel'
        yield WORD, 'localVersion'
        yield SHWPUNIT, 'initialWidth'
        yield SHWPUNIT, 'initialHeight'
        yield SHWPUNIT, 'width'
        yield SHWPUNIT, 'height'
        yield cls.Flags, 'attr'
        yield WORD, 'angle'
        yield SHWPUNIT, 'rotationCenterX'
        yield SHWPUNIT, 'rotationCenterY'
        nMatrices = yield WORD, 'nMatrices'
        yield Matrix, 'matTranslation'
        yield ARRAY(ScaleRotationMatrix, nMatrices), 'matScaleRotation'
        if chid == CHID.CONTAINER:
            yield N_ARRAY(WORD, CHID), 'controls',
    attributes = classmethod(attributes)

    def parse_with_parent(cls, context, (parent_context, parent_model, parent_attributes, parent_stream), stream, attributes):
        if parent_model is GShapeObjectControl:
            attributes['chid0'] = CHID.read(stream) # GSO-child ShapeComponent specific: it may be a GSO model's attribute, e.g. 'child_chid'
        return parse_model_attributes(cls, attributes, context, stream)
    parse_with_parent = classmethod(parse_with_parent)

    def parse_child(cls, attributes, context, (child_context, child_model, child_attributes, child_stream)):
        if child_model is ListHeader:
            return parse_model_attributes(TextboxParagraphList, child_attributes, child_context, child_stream)
        else:
            return child_model, child_attributes
    parse_child = classmethod(parse_child)


class TextboxParagraphList(ListHeader):
    def attributes(context):
        yield MarginPadding, 'padding'
        yield HWPUNIT, 'maxwidth'
    attributes = staticmethod(attributes)


class Coord:
    def attributes(context):
        yield SHWPUNIT, 'x',
        yield SHWPUNIT, 'y',
    attributes = staticmethod(attributes)

    def parse(cls, f):
        return parse_model_attributes(cls, dict(), None, f)
    parse = classmethod(parse)


class ShapeLine(BasicElement):
    def attributes(context):
        yield Coord, 'start'
        yield Coord, 'end'
        yield UINT16, 'attr'
    attributes = staticmethod(attributes)


class ShapeRectangle(BasicElement):
    def attributes(context):
        yield BYTE, 'round',
        yield ARRAY(Coord, 4), 'coords',
    attributes = staticmethod(attributes)


class ShapeEllipse(BasicElement):
    Flags = dataio.Flags(UINT32, ()) # TODO
    def attributes(cls, context):
        yield cls.Flags, 'flags'
        yield Coord, 'center'
        yield Coord, 'axis1'
        yield Coord, 'axis2'
        yield Coord, 'start1'
        yield Coord, 'end1'
        yield Coord, 'start2'
        yield Coord, 'end2'
    attributes = classmethod(attributes)


class ShapeArc(BasicElement):
    def attributes(cls, context):
        #yield ShapeEllipse.Flags, 'flags' # SPEC
        yield Coord, 'center'
        yield Coord, 'axis1'
        yield Coord, 'axis2'
    attributes = classmethod(attributes)


class ShapePolygon(BasicElement):
    def attributes(cls, context):
        count = yield UINT16, 'count'
        yield ARRAY(Coord, count), 'points'
    attributes = classmethod(attributes)


class ShapeCurve(BasicElement):
    def attributes(cls, context):
        count = yield UINT16, 'count'
        yield ARRAY(Coord, count), 'points'
        # TODO: segment type
    attributes = classmethod(attributes)


class ShapeOLE(BasicElement):
    # TODO
    pass


class PictureInfo(BasicModel):
    def attributes(context):
        yield INT8, 'brightness',
        yield INT8, 'contrast',
        yield BYTE, 'effect',
        yield UINT16, 'binId',
    attributes = staticmethod(attributes)


class ShapePicture(BasicElement):
    def attributes(context):
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
    attributes = staticmethod(attributes)


class ShapeContainer(BasicElement):
    # TODO
    pass


class ShapeTextArt(BasicElement):
    # TODO
    pass


class ControlData(Element):
    pass


class EqEdit(BasicElement):
    # TODO
    pass


class ForbiddenChar(BasicElement):
    # TODO
    pass


class SectionDef(Control):
    def attributes(context):
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
        if context['version'] >= (5, 0, 1, 7):
            yield UINT32, 'unknown1',
            yield UINT32, 'unknown2',
    attributes = staticmethod(attributes)
SectionDef = Control.concrete_type(CHID.SECD)(SectionDef)


class ColumnsDef(Control):
    def attributes(cls, context):
        flags = yield cls.Flags, 'flags'
        yield HWPUNIT16, 'spacing'
        if not flags.sameWidths:
            yield ARRAY(WORD, flags.count), 'widths'
        yield UINT16, 'attr2'
        yield Border, 'splitterStyle'
    attributes = classmethod(attributes)

    Flags = dataio.Flags(UINT16, (
            (0, 1), 'kind',
            (2, 9), 'count',
            (10, 11), 'direction',
            12, 'sameWidths',
            ))
ColumnsDef = Control.concrete_type(CHID.COLD)(ColumnsDef)


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
    def attributes(cls, context):
        yield cls.Flags, 'flags',
        yield UINT16, 'number',
    attributes = classmethod(attributes)


class AutoNumbering(NumberingControl):
    chid = 'atno'
    def attributes(cls, context):
        for x in NumberingControl.attributes(context):
            yield x
        yield WCHAR, 'usersymbol',
        yield WCHAR, 'prefix',
        yield WCHAR, 'suffix',
    attributes = classmethod(attributes)
    def __unicode__(self):
        prefix = u''
        suffix = u''
        if self.flags.kind == self.Kind.FOOTNOTE:
            if self.suffix != u'\x00':
                suffix = self.suffix
        return prefix + unicode(self.number) + suffix
AutoNumbering = Control.concrete_type(CHID.ATNO)(AutoNumbering)


class NewNumbering(NumberingControl):
    pass
NewNumbering = Control.concrete_type(CHID.NWNO)(NewNumbering)


class PageNumberPosition(Control):
    ''' 4.2.10.9. 쪽 번호 위치 '''
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
    def attributes(cls, context):
        yield cls.Flags, 'pagenumberflags'
        yield WCHAR, 'usersymbol'
        yield WCHAR, 'prefix'
        yield WCHAR, 'suffix'
        yield WCHAR, 'dash'
    attributes = classmethod(attributes)
PageNumberPosition = Control.concrete_type(CHID.PGNP)(PageNumberPosition)


class HeaderFooter(Control):
    def attributes(context):
        yield UINT32, 'flags' # TODO
    attributes = staticmethod(attributes)

class Header(HeaderFooter):
    ''' 머리말 '''
    def parse_child(cls, attributes, context, (child_context, child_model, child_attributes, child_stream)):
        if child_model is ListHeader:
            return parse_model_attributes(HeaderParagraphList, child_attributes, child_context, child_stream)
        else:
            return child_model, child_attributes
    parse_child = classmethod(parse_child)
Header = Control.concrete_type(CHID.HEADER)(Header)

class HeaderParagraphList(ListHeader):
    def attributes(context):
        yield HWPUNIT, 'width'
        yield HWPUNIT, 'height'
        yield BYTE, 'textrefsbitmap'
        yield BYTE, 'numberrefsbitmap'
    attributes = staticmethod(attributes)

class Footer(HeaderFooter):
    ''' 꼬리말 '''
    def parse_child(cls, attributes, context, (child_context, child_model, child_attributes, child_stream)):
        if child_model is ListHeader:
            return parse_model_attributes(FooterParagraphList, child_attributes, child_context, child_stream)
        else:
            return child_model, child_attributes
    parse_child = classmethod(parse_child)
Footer = Control.concrete_type(CHID.FOOTER)(Footer)

class FooterParagraphList(ListHeader):
    def attributes(context):
        yield HWPUNIT, 'width'
        yield HWPUNIT, 'height'
        yield BYTE, 'textrefsbitmap'
        yield BYTE, 'numberrefsbitmap'
    attributes = staticmethod(attributes)

class Note(Control):
    ''' 미주/각주 '''
    def attributes(context):
        if context['version'] >= (5, 0, 0, 6):
            yield UINT32, 'number' # SPEC
    attributes = staticmethod(attributes)


class FootNote(Note):
    ''' 각주 '''
    pass
#    def getAutoNumber(self):
#        for paragraph in self.listhead.paragraphs:
#            for elem in paragraph.getElementsWithControl():
#                if isinstance(elem.control, AutoNumbering):
#                    return elem.control
FootNote = Control.concrete_type(CHID.FN)(FootNote)


class EndNote(Note):
    ''' 미주 '''
    pass
EndNote = Control.concrete_type(CHID.EN)(EndNote)


class Field(Control):
    Flags = dataio.Flags(UINT32, (
            0, 'editableInReadOnly',
            (11, 14), 'visitedType',
            15, 'modified',
            ))
    def attributes(cls, context):
        yield cls.Flags, 'flags',
        yield BYTE, 'extra_attr',
        yield BSTR, 'command',
        yield UINT32, 'id',
    attributes = classmethod(attributes)

class FieldHyperLink(Field):
    def geturl(self):
        s = self.command.split(';')
        return s[0].replace('\\:', ':')
FieldHyperLink = Control.concrete_type(CHID.HLK)(FieldHyperLink)

class BookmarkControl(Control):
    def attributes(context):
        if False: yield
    attributes = staticmethod(attributes)

    def parse_child(cls, attributes, context, (child_context, child_model, child_attributes, child_stream)):
        if child_model is ControlData:
            return parse_model_attributes(BookmarkControlData, child_attributes, child_context, child_stream)
        return child_model, child_attributes
    parse_child = classmethod(parse_child)
BookmarkControl = Control.concrete_type(CHID.BOKM)(BookmarkControl)


class BookmarkControlData(ControlData):
    def attributes(context):
        yield UINT32, 'unknown1'
        yield UINT32, 'unknown2'
        yield UINT16, 'unknown3'
        yield BSTR, 'name'
    attributes = staticmethod(attributes)


tag_models = {
        HWPTAG_DOCUMENT_PROPERTIES: DocumentProperties,
        HWPTAG_ID_MAPPINGS: IdMappings,
        HWPTAG_BIN_DATA: BinData,
        HWPTAG_FACE_NAME: FaceName,
        HWPTAG_BORDER_FILL: BorderFill,
        HWPTAG_CHAR_SHAPE: CharShape,
        HWPTAG_TAB_DEF: TabDef,
        HWPTAG_NUMBERING: Numbering,
        HWPTAG_BULLET: Bullet,
        HWPTAG_PARA_SHAPE: ParaShape,
        HWPTAG_STYLE: Style,
        HWPTAG_DOC_DATA: DocData,
        HWPTAG_DISTRIBUTE_DOC_DATA: DistributeDocData,
        # HWPTAG_BEGIN + 13 : RESERVED,
        HWPTAG_COMPATIBLE_DOCUMENT: CompatibleDocument,
        HWPTAG_LAYOUT_COMPATIBILITY: LayoutCompatibility,
        HWPTAG_PARA_HEADER: Paragraph,
        HWPTAG_PARA_TEXT: ParaText,
        HWPTAG_PARA_CHAR_SHAPE: ParaCharShape,
        HWPTAG_PARA_LINE_SEG: ParaLineSeg,
        HWPTAG_PARA_RANGE_TAG: ParaRangeTag,
        HWPTAG_CTRL_HEADER: Control,
        HWPTAG_LIST_HEADER: ListHeader,
        HWPTAG_PAGE_DEF: PageDef,
        HWPTAG_FOOTNOTE_SHAPE: FootnoteShape,
        HWPTAG_PAGE_BORDER_FILL: PageBorderFill,
        HWPTAG_SHAPE_COMPONENT: ShapeComponent,
        HWPTAG_TABLE: TableBody,
        HWPTAG_SHAPE_COMPONENT_LINE: ShapeLine,
        HWPTAG_SHAPE_COMPONENT_RECTANGLE: ShapeRectangle,
        HWPTAG_SHAPE_COMPONENT_ELLIPSE: ShapeEllipse,
        HWPTAG_SHAPE_COMPONENT_ARC: ShapeArc,
        HWPTAG_SHAPE_COMPONENT_POLYGON: ShapePolygon,
        HWPTAG_SHAPE_COMPONENT_CURVE: ShapeCurve,
        HWPTAG_SHAPE_COMPONENT_OLE: ShapeOLE,
        HWPTAG_SHAPE_COMPONENT_PICTURE: ShapePicture,
        HWPTAG_SHAPE_COMPONENT_CONTAINER: ShapeContainer,
        HWPTAG_CTRL_DATA: ControlData,
        HWPTAG_CTRL_EQEDIT: EqEdit,
        # HWPTAG_BEGIN + 73 : RESERVED
        HWPTAG_SHAPE_COMPONENT_TEXTART: ShapeTextArt,
        # ...
        HWPTAG_FORBIDDEN_CHAR: ForbiddenChar,
        }

def pass1(context, records):
    for record in records:
        context = dict(context)
        context['hwptag'] = record.tag
        context['recordid'] = record.id
        context['logging'].debug('Record %s at %s:%s:%d', record.tag, *record.id)
        stream = record.bytestream()
        model = tag_models.get(record.tagid, Element)
        attributes = dict()
        parse_pass1 = getattr(model, 'parse_pass1', None)
        if parse_pass1 is not None:
            model, attributes = parse_pass1(attributes, context, stream)
        context['logging'].debug('pass1: %s, %s', model, attributes.keys())
        yield record.level, (context, model, attributes, stream)

def parse_models_pass1(context, records):
    level_prefixed_cmas = pass1(context, records)
    event_prefixed_cmas = prefix_event(level_prefixed_cmas)
    return event_prefixed_cmas

class STARTEVENT: pass
class ENDEVENT: pass
def prefix_event(level_prefixed_items, root_item=None):
    baselevel = None
    stack = [root_item]
    for level, item in level_prefixed_items:
        if baselevel is None:
            baselevel = level
            level = 0
        else:
            level -= baselevel

        while level + 1 < len(stack):
            yield ENDEVENT, stack.pop()
        while len(stack) < level + 1:
            raise Exception('invalid level: %d, %d, %s'%(level, len(stack)-1, item))
        assert(len(stack) == level + 1)

        stack.append(item)
        yield STARTEVENT, item

    while 1 < len(stack):
        yield ENDEVENT, stack.pop()

def prefix_ancestors(event_prefixed_items, root_item=None):
    stack = [root_item]
    for event, item in event_prefixed_items:
        if event is STARTEVENT:
            yield stack, item
            stack.append(item)
        elif event is ENDEVENT:
            parent = stack.pop()

def pass2_child(ancestors_cmas):
    for ancestors, (context, model, attributes, stream) in ancestors_cmas:
        parent = ancestors[-1]
        parent_context, parent_model, parent_attributes, parent_stream = parent
        parse_child = getattr(parent_model, 'parse_child', None)
        if parse_child is not None:
            model, attributes = parse_child(parent_attributes, parent_context, (context, model, attributes, stream))

        parse_with_parent = getattr(model, 'parse_with_parent', None)
        if parse_with_parent is not None:
            model, attributes = model.parse_with_parent(context, parent, stream, attributes)

        context['logging'].debug('pass2: %s, %s', model, attributes.keys())
        yield len(ancestors)-1, (context, model, attributes, stream)

def parse_models_pass2(event_prefixed_cmas):
    ancestors_prefixed_cmas = prefix_ancestors(event_prefixed_cmas, (None, None, None, None))
    level_prefixed_cmas = pass2_child(ancestors_prefixed_cmas)
    event_prefixed_cmas = prefix_event(level_prefixed_cmas)
    return event_prefixed_cmas

def parse_models(context, records):
    pass1 = parse_models_pass1(context, records)
    pass2 = parse_models_pass2(pass1)
    for event, (context, model, attributes, stream) in pass2:
        context['unparsed'] = stream.read()
        yield event, (model, attributes, context)

#    class ParaText(BasicElement, list):
#        def decode(self, bytes):
#            for elem in self.parseBytes(bytes):
#                self.append(elem)
#            return self
#        def parseBytes(cls, bytes):
#            size = len(bytes)
#            idx = 0
#            while idx < size:
#                ctrlpos, ctrlpos_end = ControlChar.find(bytes, idx)
#                if idx < ctrlpos:
#                    text = Text(dataio.decode_utf16le_besteffort(bytes[idx:ctrlpos]))
#                    text.byteoffset = idx
#                    text.charoffset = idx/2
#                    text.charShapeId = None
#                    yield text
#                if ctrlpos < ctrlpos_end:
#                    ctlch = ControlChar.decode_bytes(bytes[ctrlpos:ctrlpos_end])
#                    ctlch.byteoffset = ctrlpos
#                    ctlch.charoffset = ctrlpos/2
#                    ctlch.charShapeId = None
#                    yield ctlch
#                idx = ctrlpos_end
#        parseBytes = classmethod(parseBytes)
#        def getElements(self):
#            return self.parseBytes(self.record.bytes)
#        def controlchars_by_chid(self, chid):
#            return itertools.ifilter(
#                    lambda elem: isinstance(elem, ControlChar) and elem.chid == chid,
#                    self)
#        def __repr__(self):
#            return '\n'.join(['- '+repr(x) for x in self])
#
#    class Paragraph:
#        def __init__(self):
#            self.textdata = None
#            self.charShapes = None
#            self.controls = {}
#            self.sectionDef = None
#
#        SplitFlags = dataio.Flags(BYTE, (
#                0, 'section',
#                1, 'multicolumn',
#                2, 'page',
#                3, 'column',
#                ))
#        ControlMask = dataio.Flags(UINT32, (
#                2, 'unknown1',
#                11, 'control',
#                21, 'new_number',
#                ))
#        Flags = dataio.Flags(UINT32, (
#                31, 'unknown',
#                (0, 30), 'chars',
#                ))
#        def addsubrec(paragraph, rec):
#            if rec.tagid == HWPTAG_PARA_TEXT:
#                paragraph.textdata = ParaText()
#                paragraph.textdata.decode(rec.bytes)
#                paragraph.textdata.record = rec
#                rec.model = paragraph.textdata
#            elif rec.tagid == HWPTAG_PARA_CHAR_SHAPE:
#                paragraph.charShapes = ParaCharShape(paragraph.characterShapeCount)
#                paragraph.charShapes.parse(rec.bytestream())
#                paragraph.charShapes.record = rec
#                rec.model = paragraph.charShapes
#            elif rec.tagid == HWPTAG_PARA_LINE_SEG:
#                paragraph.lineSegs = ARRAY(LineSeg, paragraph.nLineSegs)
#                paragraph.lineSegs.parse(rec.bytestream())
#                paragraph.lineSegs.record = rec
#                rec.model = paragraph.lineSegs
#
#        def getElementsWithControl(self):
#            if self.textdata is None:
#                return
#            ctrliters = {}
#            for elem in self.textdata.getElements():
#                if isinstance(elem, ControlChar) and elem.kind == elem.extended:
#                    controls = self.controls.get(elem.chid, None)
#                    if controls is not None:
#                        ctrliter = ctrliters.setdefault( elem.chid, iter(controls) )
#                        try:
#                            elem.control = ctrliter.next()
#                        except StopIteration:
#                            logging.fatal('can\'t find control')
#                yield elem
#
#        def getSegmentedElements(self, elemiter, segments):
#            try:
#                elem = elemiter.next()
#                for (segmentstart, segmentend, segmentid) in segments:
#                    if segmentstart == segmentend: continue
#                    #logging.debug('RANGE = (%s~%s) with %s'%(segmentstart, segmentend, segmentid))
#                    while True:
#                        elemstart = elem.charoffset
#                        elemend = elem.charoffset + len(elem)
#                        if elemstart == elemend:
#                            elem = elemiter.next()
#                            continue
#                        #logging.debug('ELEM = (%s,%s) %s'%(elemstart, elemend, elem))
#                        if elemend <= segmentstart:
#                            elem = elemiter.next()
#                            continue
#                        if elemstart < segmentstart and segmentstart < elemend:
#                            # split Text
#                            if isinstance(elem, Text):
#                                split_pos = segmentstart - elemstart
#                                prev, next = elem.split(split_pos)
#                                yield prev, segmentid
#                                elem = next
#                                #logging.debug('SPLIT: %s / %s'%(prev, next))
#                                continue
#                            else:
#                                logging.warning('element %s is over ParaCharShape (%d~%d, %d)'%(repr(elem), segmentstart, segmentend, segmentid))
#                        if segmentstart <= elemstart and elemend <= segmentend:
#                            #logging.debug('APPLIED: %s'%elem)
#                            yield elem, segmentid
#                            elem = elemiter.next()
#                            continue
#                        if elemstart < segmentend and segmentend < elemend:
#                            assert(segmentstart <= elemstart)
#                            if isinstance(elem, Text):
#                                split_pos = segmentend - elemstart
#                                prev, next = elem.split(split_pos)
#                                yield prev, segmentid
#                                #logging.debug('SPLIT2: %s / %s'%(prev, next))
#                                elem = next
#                                continue
#                            else:
#                                logging.warning('element %s is over ParaCharShape (%d~%d, %d)'%(repr(elem), segmentstart, segmentend, segmentid))
#                        if segmentend <= elemstart:
#                            break # next shape
#            except StopIteration:
#                pass
#            except KeyboardInterrupt:
#                logging.error( self.record )
#                logging.error( 'elem: (%s - %s) %s'%(elemstart, elemend, elem) )
#                logging.error( 'segment: (%s - %s) %s'%(segmentstart, segmentend, segmentid) )
#                raise
#
#        def getCharShapeSegments(self):
#            if self.textdata is None:
#                return
#            start = None
#            shapeid = None
#            for (pos, next_shapeid) in self.charShapes:
#                if start is not None:
#                    yield start, pos, shapeid
#                start = pos
#                shapeid = next_shapeid
#            if start is not None:
#                end = len(self.textdata.record.bytes)/2
#                if end > 0:
#                    yield start, end, shapeid
#
#        def getShapedElements(self):
#            if self.textdata is None:
#                return
#            elements = self.exclude_last_paragraph_break(self.getElementsWithControl())
#            for elem, charShapeId in self.getSegmentedElements(elements, self.getCharShapeSegments()):
#                elem.charShapeId = charShapeId
#                yield elem
#
#        def getLineSegments(self):
#            if self.textdata is None:
#                return
#            start = None
#            lineseg = None
#            for lineno, next_lineseg in enumerate(self.lineSegs):
#                pos = next_lineseg.chpos
#                if start is not None:
#                    lineseg.number_in_paragraph = lineno-1
#                    yield start, pos, lineseg
#                start = pos
#                lineseg = next_lineseg
#            if start is not None:
#                end = len(self.textdata.record.bytes)/2
#                if end > 0:
#                    lineseg.number_in_paragraph = lineno
#                    yield start, end, lineseg
#
#        def getLinedElements(self):
#            elements = self.getShapedElements()
#            for elem, lineSeg in self.getSegmentedElements(elements, self.getLineSegments()):
#                yield elem, lineSeg
#
#        def getLines(self):
#            elements = self.getShapedElements()
#            return groupby_mapfunc(self.getSegmentedElements(elements, self.getLineSegments()),
#                    lambda (elem, lineSeg): lineSeg,
#                    lambda (elem, lineSeg): elem)
#
#        def getPagedLines(paragraph, page=0, prev_line=None):
#            for line, line_elements in paragraph.getLines():
#                if prev_line is not None:
#                    if line.offsetY <= prev_line.offsetY:
#                        page += 1
#                prev_line = line
#                yield page, line, line_elements
#        def getPages(self, page, prev_line):
#            for page, page_lines in groupby_mapfunc(self.getPagedLines(page, prev_line),
#                    lambda (page, line, line_elements): page,
#                    lambda (page, line, line_elements): (line, line_elements)):
#                yield (page, page_lines)
#
#        def exclude_last_paragraph_break(self, elements):
#            prev = None
#            for elem in elements:
#                if prev is not None:
#                    yield prev
#                prev = elem
#            if prev is not None:
#                if not isinstance(prev, ControlChar) or not prev.ch == ControlChar.PARAGRAPH_BREAK:
#                    yield prev
#
#        def addControl(self, ctrl):
#            chid = getattr(ctrl, 'chid', None)
#            if chid is not None:
#                self.controls.setdefault(ctrl.chid, []).append(ctrl)
#                ctlchs = [c for c in self.textdata.controlchars_by_chid(chid)]
#                ctlchs[ len(self.controls[ctrl.chid])-1 ].control = ctrl
#
#        def __getattr__(paragraph, name):
#            if name == 'style':
#                style = context.mappings[Style][paragraph.styleId]
#                style.paragraphShape = context.mappings[ParaShape][style.paragraphShapeId]
#                style.characterShape = context.mappings[CharShape][style.characterShapeId]
#                return style
#            elif name == 'paragraphShape':
#                return context.mappings[ParaShape][paragraph.paragraphShapeId]
#            raise AttributeError(name)
#
#    class Section(RecordsContainer):
#        def __init__(self):
#            RecordsContainer.__init__(self)
#            self.paragraphs = []
#
#        def getPages(self, factory):
#            page = factory.Page()
#            paragraph = None
#            line = None
#            for ev, param in getElementEvents(self.paragraphs):
#                if ev == EV_PAGE:
#                    if page is not None:
#                        yield page
#                    page = factory.Page()
#                elif ev == EV_PARAGRAPH:
#                    paragraph = page.Paragraph(param)
#                    page.append(paragraph)
#                elif ev == EV_LINE:
#                    line = paragraph.Line(param)
#                    paragraph.append(line)
#                elif ev == EV_ELEMENT:
#                    line.append(line.BasicElement(param))
#            if page is not None:
#                yield page
#
#        def getSubModeler(self, rec):
#            tagid = rec.tagid
#            if tagid == HWPTAG_PARA_HEADER:
#                return Paragraph, self.paragraphs.append
#        def getSectionDef(self):
#            paragraph = self.paragraphs[0]
#            for e in paragraph.getElementsWithControl():
#                if isinstance(e, ControlChar) and e.ch == ControlChar.SECTION_COLUMN_DEF:
#                    if isinstance(e.control, SectionDef):
#                        return e.control
#        sectionDef = property(getSectionDef)
#        def getColumnsDef(self):
#            paragraph = self.paragraphs[0]
#            for e in paragraph.getElementsWithControl():
#                if isinstance(e, ControlChar) and e.ch == ControlChar.SECTION_COLUMN_DEF:
#                    if isinstance(e.control, ColumnsDef):
#                        return e.control
#        columnsDef = property(getColumnsDef)
#
#    class DocInfo(RecordsContainer):
#        def getSubModeler(self, rec):
#            tagid = rec.tagid
#            if tagid == HWPTAG_ID_MAPPINGS:
#                return IdMappings, 'mappings'
#            elif tagid == HWPTAG_DOCUMENT_PROPERTIES:
#                return DocumentProperties, 'documentProperties'
#            elif tagid == HWPTAG_DOC_DATA:
#                return DocData, 'docData'
#
#    return locals()

def main():
    import sys
    import logging
    import itertools
    from .filestructure import File

    from optparse import OptionParser as OP
    op = OP(usage='usage: %prog [options] filename <record-stream> [<record-range>]\n\n<record-range> : <index> | <start-index>: | :<end-index> | <start-index>:<end-index>')
    op.add_option('-V', '--hwp-version', dest='print_hwp_version', action='store_true', default=False,
            help='print hwp5 file format version')
    op.add_option('', '--loglevel', dest='loglevel', default='warning', help='log level (debug, info, warning, error, critical)')
    op.add_option('', '--pass', dest='passes', type='int', default=2)

    options, args = op.parse_args()
    try:
        filename = args.pop(0)
    except IndexError:
        print 'the input filename is required'
        op.print_help()
        return -1

    file = File(filename)
    if options.print_hwp_version:
        print file.fileheader.version

    from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
    loglevels = dict(debug=DEBUG, info=INFO, warning=WARNING, error=ERROR, critical=CRITICAL)

    logger = logging.getLogger()
    logger.setLevel(loglevels.get(options.loglevel, WARNING))
    loghandler = logging.StreamHandler(sys.stdout)
    loghandler.setFormatter(logging.Formatter('<!-- %(message)s -->'))
    logger.addHandler(loghandler)
    context = dict(version=file.fileheader.version, logging=logger)

    try:
        stream_specifier = args.pop(0)
    except IndexError:
        print '<record-stream> is not specified'
        op.print_help()
        print 'Available <record-stream>s:'
        print ''
        print 'docinfo'
        print 'bodytext/<idx>'
        return -1

    class DocumentHandler(object):
        def startDocument(self):
            pass
        def startElement(self, model, attributes, **kwargs):
            pass
        def endElement(self, model):
            pass
        def endDocument(self):
            pass

    from xml.sax.saxutils import XMLGenerator
    class XmlHandler(DocumentHandler):
        xmlgen = XMLGenerator(sys.stdout, 'utf-8')
        def __init__(self):
            pass
        def startDocument(self):
            self.xmlgen.startDocument()
            self.xmlgen.startElement('Records', dict(filename=filename, streamid=stream_specifier))
        def startElement(self, model, attributes, **kwargs):
            def attr2str(v):
                if isinstance(v, basestring):
                    return v
                else:
                    return str(v)
            def attritem2str(item):
                try:
                    name, v = item
                    return name, attr2str(v)
                except Exception, e:
                    logging.error('can\'t serialize xml attribute %s: %s'%(name, repr(v)))
                    logging.exception(e)
                    raise
            recordid = kwargs.get('recordid', ('UNKNOWN', 'UNKNOWN', -1))
            hwptag = kwargs.get('hwptag', '')
            self.xmlgen._write('<!-- rec:%d %s -->'%(recordid[2], hwptag))
            self.xmlgen.startElement(model.__name__, dict(attritem2str(x) for x in attributes.items()))
            unparsed = kwargs.get('unparsed', '')
            if len(unparsed) > 0:
                self.xmlgen._write('<!-- UNPARSED\n')
                self.xmlgen._write(dataio.hexdump(unparsed, True))
                self.xmlgen._write('\n-->')
        def endElement(self, model):
            self.xmlgen.endElement(model.__name__)
        def endDocument(self):
            self.xmlgen.endElement('Records')
            self.xmlgen.endDocument()

    oformat = XmlHandler()

    stream_spec = stream_specifier.split('/')
    stream_name = stream_spec[0]
    stream_args = stream_spec[1:]

    method = getattr(file, stream_name)
    bytestream = method(*stream_args)
    from .recordstream import read_records
    records = read_records(bytestream, stream_specifier, filename)

    models = parse_models_pass1(context, records)
    if options.passes >= 2:
        models = parse_models_pass2(models)

    oformat.startDocument()
    for event, (context, model, attributes, stream) in models:
        if event == STARTEVENT:
            context['unparsed'] = stream.read()
            oformat.startElement(model, attributes, **context)
        elif event == ENDEVENT:
            oformat.endElement(model)
    oformat.endDocument()
