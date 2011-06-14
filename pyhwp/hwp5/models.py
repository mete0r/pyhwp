# -*- coding: utf-8 -*-
from .dataio import readn, read_struct_attributes, match_attribute_types,\
        StructType, Struct, Flags, Enum, BYTE, WORD, UINT32, UINT16, INT32, INT16, UINT8, INT8,\
        DOUBLE, ARRAY, N_ARRAY, SHWPUNIT, HWPUNIT16, HWPUNIT, BSTR, WCHAR
from .utils import cached_property
from .tagids import tagnames, HWPTAG_BEGIN, HWPTAG_DOCUMENT_PROPERTIES, HWPTAG_ID_MAPPINGS, HWPTAG_BIN_DATA, HWPTAG_FACE_NAME,\
        HWPTAG_BORDER_FILL, HWPTAG_CHAR_SHAPE, HWPTAG_TAB_DEF, HWPTAG_NUMBERING, HWPTAG_BULLET,\
        HWPTAG_PARA_SHAPE, HWPTAG_STYLE, HWPTAG_DOC_DATA, HWPTAG_DISTRIBUTE_DOC_DATA,\
        HWPTAG_COMPATIBLE_DOCUMENT, HWPTAG_LAYOUT_COMPATIBILITY,\
        HWPTAG_PARA_HEADER, HWPTAG_PARA_TEXT, HWPTAG_PARA_CHAR_SHAPE, HWPTAG_PARA_LINE_SEG, HWPTAG_PARA_RANGE_TAG,\
        HWPTAG_CTRL_HEADER, HWPTAG_LIST_HEADER, HWPTAG_PAGE_DEF, HWPTAG_FOOTNOTE_SHAPE, HWPTAG_PAGE_BORDER_FILL,\
        HWPTAG_SHAPE_COMPONENT, HWPTAG_TABLE, HWPTAG_SHAPE_COMPONENT_LINE, HWPTAG_SHAPE_COMPONENT_RECTANGLE,\
        HWPTAG_SHAPE_COMPONENT_ELLIPSE, HWPTAG_SHAPE_COMPONENT_ARC, HWPTAG_SHAPE_COMPONENT_POLYGON,\
        HWPTAG_SHAPE_COMPONENT_CURVE, HWPTAG_SHAPE_COMPONENT_OLE, HWPTAG_SHAPE_COMPONENT_PICTURE,\
        HWPTAG_SHAPE_COMPONENT_CONTAINER, HWPTAG_CTRL_DATA, HWPTAG_CTRL_EQEDIT, HWPTAG_SHAPE_COMPONENT_TEXTART,\
        HWPTAG_FORBIDDEN_CHAR

from . import dataio

def parse_model_attributes(model, attributes, context, stream):
    return model, read_struct_attributes(model, attributes, context, stream)

def typed_model_attributes(model, attributes, context):
    import inspect
    attributes = dict(attributes)
    for cls in filter(lambda x: x is not RecordModel and issubclass(x, RecordModel), inspect.getmro(model)):
        types = getattr(cls, 'attributes', None)
        if types:
            types = types(context)
            for x in match_attribute_types(types, attributes):
                yield x
    for name, value in attributes.iteritems():
        yield name, (type(value), value)

tag_models = dict()

class RecordModelType(StructType):
    def __init__(cls, name, bases, attrs):
        super(RecordModelType, cls).__init__(name, bases, attrs)
        if 'tagid' in attrs:
            tagid = attrs['tagid']
            existing = tag_models.get(tagid)
            assert not tagid in tag_models,\
                    'duplicated RecordModels for tagid \'%s\': new=%s, existing=%s'%(tagnames[tagid], name, existing.__name__)
            tag_models[tagid] = cls

class RecordModel(object):
    __metaclass__ = RecordModelType
    def __init__(self, context, attributes):
        self.__dict__.update(attributes)
        self.context = context


class BasicRecordModel(RecordModel):
    def attributes(context):
        if False: yield
    attributes = staticmethod(attributes)
    parse_pass1 = classmethod(parse_model_attributes)


class AttributeDeterminedRecordModel(BasicRecordModel):
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


class DocumentProperties(BasicRecordModel):
    tagid = HWPTAG_DOCUMENT_PROPERTIES
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


class IdMappings(BasicRecordModel):
    tagid = HWPTAG_ID_MAPPINGS
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


class BinData(AttributeDeterminedRecordModel):
    tagid = HWPTAG_BIN_DATA
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


class AlternateFont(Struct):
    def attributes(context):
        yield BYTE, 'kind'
        yield BSTR, 'name'
    attributes = staticmethod(attributes)


class Panose1(Struct):
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


class FaceName(BasicRecordModel):
    tagid = HWPTAG_FACE_NAME
    Flags = Flags(BYTE,
        5, 'default',
        6, 'metric',
        7, 'alternate',
        )
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


class COLORREF(int):
    read = staticmethod(INT32.read)
    __slots__ = []
    def __getattr__(self, name):
        if name == 'r': return self & 0xff
        elif name == 'g': return (self & 0xff00) >> 8
        elif name == 'b': return (self & 0xff0000) >> 16
        elif name == 'a': return (self & 0xff000000) >> 24
        elif name == 'rgb': return self.r, self.g, self.b
    def __str__(self): return '#%02x%02x%02x'%(self.r, self.g, self.b)
    def __repr__(self): return self.__class__.__name__+('(0x%02x, 0x%02x, 0x%02x)'%self.rgb)

class Border(Struct):
    def attributes(context):
        yield UINT8, 'style',
        yield UINT8, 'width',
        yield COLORREF, 'color',
    attributes = staticmethod(attributes)


class Fill(Struct):
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


class BorderFill(BasicRecordModel):
    tagid = HWPTAG_BORDER_FILL
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


class CharShape(BasicRecordModel):
    tagid = HWPTAG_CHAR_SHAPE
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


class TabDef(BasicRecordModel):
    tagid = HWPTAG_TAB_DEF
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


class Numbering(BasicRecordModel):
    tagid = HWPTAG_NUMBERING
    Align = Enum(LEFT=0, CENTER=1, RIGHT=2)
    DistanceType = Enum(RATIO=0, VALUE=1)
    Flags = Flags(UINT32,
        0, 1, Align, 'paragraphAlign',
        2, 'autowidth',
        3, 'autodedent',
        4, DistanceType, 'distance_to_body_type',
        )
    def attributes(cls, context):
        yield cls.Flags, 'flags'
        yield HWPUNIT16, 'width_correction'
        yield HWPUNIT16, 'distance_to_body'
        yield UINT32, 'charShapeId' # SPEC ?????
    attributes = classmethod(attributes)
        

class Bullet(BasicRecordModel):
    tagid = HWPTAG_BULLET


class ParaShape(BasicRecordModel):
    tagid = HWPTAG_PARA_SHAPE
    Flags = Flags(UINT32,
            0, 1, 'lineSpacingType',
            2, 4, 'textAlign',
            # TODO
            )
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


class Style(BasicRecordModel):
    tagid = HWPTAG_STYLE
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


class DocData(BasicRecordModel):
    tagid = HWPTAG_DOC_DATA
    pass


class DistributeDocData(BasicRecordModel):
    tagid = HWPTAG_DISTRIBUTE_DOC_DATA
    pass


class CompatibleDocument(BasicRecordModel):
    tagid = HWPTAG_COMPATIBLE_DOCUMENT
    Target = Enum(DEFAULT=0, HWP2007=1, MSWORD=2)
    def attributes(context):
        yield Target, 'target'
    attributes = staticmethod(attributes)


class LayoutCompatibility(BasicRecordModel):
    tagid = HWPTAG_LAYOUT_COMPATIBILITY
    def attributes(context):
        yield UINT32, 'char',
        yield UINT32, 'paragraph',
        yield UINT32, 'section',
        yield UINT32, 'object',
        yield UINT32, 'field',
    attributes = staticmethod(attributes)


class CHID(str):
    # Common controls
    GSO = 'gso '
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

    # Controls
    SECD = 'secd'
    COLD = 'cold'
    HEADER = 'head'
    FOOTER = 'foot'
    FN = 'fn  '
    EN = 'en  '
    ATNO = 'atno'
    NWNO = 'nwno'
    PGHD = 'pghd'
    PGCT = 'pgct'
    PGNP = 'pgnp'
    IDXM = 'idxm'
    BOKM = 'bokm'
    TCPS = 'tcps'
    TDUT = 'tdut'
    TCMT = 'tcmt'

    # Field starts
    UNK = '%unk'
    DTE = '%dte'
    #...
    HLK = '%hlk'

    def decode(bytes):
        return bytes[3] + bytes[2] + bytes[1] + bytes[0]
    decode = staticmethod(decode)

    def read(cls, f, context=None):
        bytes = readn(f, 4)
        return cls.decode(bytes)
    read = classmethod(read)

    def __new__(cls, *args):
        return str.__new__(cls, *args)


control_models = dict()

class ControlType(RecordModelType):
    def __init__(cls, name, bases, attrs):
        super(ControlType, cls).__init__(name, bases, attrs)
        if 'chid' in attrs:
            chid = attrs['chid']
            existing = control_models.get(chid)
            assert not chid in control_models, 'duplicated ControlType instances for chid \'%s\': new=%s, existing=%s'%(chid, name, existing.__name__)
            control_models[chid] = cls

class Control(AttributeDeterminedRecordModel):
    __metaclass__ = ControlType
    tagid = HWPTAG_CTRL_HEADER

    def attributes(context):
        chid = yield CHID, 'chid'
    attributes = staticmethod(attributes)

    key_attribute = 'chid'
    def concrete_type_by_attribute(cls, chid):
        return control_models.get(chid)
    concrete_type_by_attribute = classmethod(concrete_type_by_attribute)


MarginPadding = ARRAY(HWPUNIT16, 4)

class CommonControl(Control):
    Flow = Enum(FLOAT=0, BLOCK=1, BACK=2, FRONT=3)
    TextSide = Enum(BOTH=0, LEFT=1, RIGHT=2, LARGER=3)
    VRelTo = Enum(PAPER=0, PAGE=1, PARAGRAPH=2)
    HRelTo = Enum(PAPER=0, PAGE=1, COLUMN=2, PARAGRAPH=3)
    VAlign = Enum(TOP=0, CENTER=1, BOTTOM=2, INSIDE=3, OUTSIDE=4)
    HAlign = Enum(LEFT=0, CENTER=1, RIGHT=2, INSIDE=3, OUTSIDE=4)
    WidthRelTo = Enum(PAPER=0, PAGE=1, COLUMN=2, PARAGRAPH=3, ABSOLUTE=4)
    HeightRelTo = Enum(PAPER=0, PAGE=1, ABSOLUTE=2)
    NumberCategory = Enum(NONE=0, FIGURE=1, TABLE=2, EQUATION=3)

    CommonControlFlags = dataio.Flags(UINT32,
            0, 'inline',
            2, 'affect_line_spacing',
            3, 4, VRelTo, 'vrelto',
            5, 7, VAlign, 'valign',
            8, 9, HRelTo, 'vrelto',
            10, 12, HAlign, 'halign',
            13, 'restrict_in_page',
            14, 'overlap_others',
            15, 17, WidthRelTo, 'width_relto',
            18, 19, HeightRelTo, 'height_relto',
            20, 'protect_size_when_vrelto_paragraph',
            21, 23, Flow, 'flow',
            24, 25, TextSide, 'text_side',
            26, 27, NumberCategory, 'number_category'
            )

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
    chid = CHID.TBL
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


class ListHeader(BasicRecordModel):
    tagid = HWPTAG_LIST_HEADER
    Flags = Flags(UINT32,
        0, 2, 'textdirection',
        3, 4, 'linebreak',
        5, 6, 'vertAlign',
        )
    VALIGN_MASK     = 0x60
    VALIGN_TOP      = 0x00
    VALIGN_MIDDLE   = 0x20
    VALIGN_BOTTOM   = 0x40
    def attributes(cls, context):
        yield UINT16, 'nParagraphs',
        yield UINT16, 'unknown1',
        yield cls.Flags, 'listflags',
    attributes = classmethod(attributes)


class PageDef(BasicRecordModel):
    tagid = HWPTAG_PAGE_DEF
    Flags = Flags(UINT32,
                0, 'landscape',
                1, 2, 'bookcompilingStyle'
                )
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


class FootnoteShape(BasicRecordModel):
    tagid = HWPTAG_FOOTNOTE_SHAPE
    Flags = Flags(UINT32,
        )
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


class PageBorderFill(BasicRecordModel):
    tagid = HWPTAG_PAGE_BORDER_FILL
    Oriented = Enum(FROM_BODY=0, FROM_PAPER=1)
    FillArea = Enum(PAPER=0, PAGE=1, BORDER=2)
    Flags = Flags(UINT32,
        0, Oriented, 'oriented',
        1, 'include_header',
        2, 'include_footer',
        3, 4, FillArea, 'fill_area',
        )
    def attributes(cls, context):
        yield cls.Flags, 'flags'
        yield MarginPadding, 'margin'
        yield UINT16, 'borderFillId'
    attributes = classmethod(attributes)


class TableCaption(ListHeader):
    Position = Enum(LEFT=0, RIGHT=1, TOP=2, BOTTOM=3)
    CaptionFlags = Flags(UINT32,
                0, 1, Position, 'position',
                2, 'include_margin',
                )
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


class TableBody(BasicRecordModel):
    tagid = HWPTAG_TABLE
    Split = Enum(NONE=0, BY_CELL=1, SPLIT=2)
    TableFlags = Flags(UINT32,
                0, 1, Split, 'splitPage',
                2, 'repeatHeaderRow',
                )
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


class Paragraph(BasicRecordModel):
    tagid = HWPTAG_PARA_HEADER

    SplitFlags = Flags(BYTE,
            0, 'section',
            1, 'multicolumn',
            2, 'page',
            3, 'column',
            )
    ControlMask = Flags(UINT32,
            2, 'unknown1',
            11, 'control',
            21, 'new_number',
            )
    Flags = Flags(UINT32,
            31, 'unknown',
            0, 30, 'chars',
            )
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
    class CHAR(object):
        size = 1
    class INLINE(object):
        size = 8
    class EXTENDED(object):
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
        return self.kinds[self.ch]
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
    pass

class ParaText(RecordModel):
    tagid = HWPTAG_PARA_TEXT
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


class ParaCharShape(RecordModel):
    tagid = HWPTAG_PARA_CHAR_SHAPE
    def parse_with_parent(cls, context, (parent_context, parent_model, parent_attributes, parent_stream), stream, attributes):
        nCharShapes = parent_attributes['characterShapeCount']
        attributes['charshapes'] = ARRAY(ARRAY(UINT32, 2), nCharShapes).read(stream)
        return cls, attributes
    parse_with_parent = classmethod(parse_with_parent)


class ParaLineSeg(RecordModel):
    tagid = HWPTAG_PARA_LINE_SEG
    class LineSeg(Struct):
        Flags = Flags(UINT16,
                4, 'indented')
        def attributes(cls, context):
            yield INT32, 'chpos',
            yield SHWPUNIT, 'offsetY',
            yield SHWPUNIT, 'a2',
            yield SHWPUNIT, 'height',
            yield SHWPUNIT, 'a3',
            yield SHWPUNIT, 'marginBottom',
            yield SHWPUNIT, 'offsetX',
            yield SHWPUNIT, 'width'
            yield UINT16, 'a8'
            yield cls.Flags, 'linesegflags'
        attributes = classmethod(attributes)

    def parse_with_parent(cls, context, (parent_context, parent_model, parent_attributes, parent_stream), stream, attributes):
        nLineSegs = parent_attributes['nLineSegs']
        attributes['linesegs'] = ARRAY(cls.LineSeg, nLineSegs).read(stream)
        return cls, attributes
    parse_with_parent = classmethod(parse_with_parent)


class ParaRangeTag(BasicRecordModel):
    tagid = HWPTAG_PARA_RANGE_TAG
    def attributes(context):
        yield UINT32, 'start'
        yield UINT32, 'end'
        yield UINT32, 'tag'
        # TODO: SPEC
    attributes = staticmethod(attributes)


class GShapeObjectControl(CommonControl):
    chid = CHID.GSO
    def parse_child(cls, attributes, context, (child_context, child_model, child_attributes, child_stream)):
        # TODO: ListHeader to Caption
        return child_model, child_attributes
    parse_child = classmethod(parse_child)


class Matrix(tuple):
    def read(f, context):
        return ARRAY(ARRAY(DOUBLE, 3), 2).read(f, context) + ((0.0, 0.0, 1.0),)
    read = staticmethod(read)

    def applyTo(self, (x, y)):
        ret = []
        for row in self:
            ret.append(row[0] * x + row[1] * y + row[2] * 1)
        return (ret[0], ret[1])
    def scale(self, (w, h)):
        ret = []
        for row in self:
            ret.append(row[0] * w + row[1] * h + row[2] * 0)
        return (ret[0], ret[1])
    def product(self, mat):
        ret = []
        rs = [0, 1, 2]
        cs = [0, 1, 2]
        for r in rs:
            row = []
            for c in cs:
                row.append( self[r][c] * mat[c][r])
            ret.append(row)
        return Matrix(ret)


class ScaleRotationMatrix(Struct):
    def attributes(context):
        yield Matrix, 'scaler',
        yield Matrix, 'rotator',
    attributes = staticmethod(attributes)

class ShapeComponent(RecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT
    Flags = Flags(UINT32,
            0, 'flip'
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


Coord = ARRAY(SHWPUNIT, 2)

class ShapeLine(BasicRecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_LINE
    def attributes(context):
        yield ARRAY(Coord, 2), 'coords'
        yield UINT16, 'attr'
    attributes = staticmethod(attributes)


class ShapeRectangle(BasicRecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_RECTANGLE
    def attributes(context):
        yield BYTE, 'round',
        yield ARRAY(Coord, 4), 'coords',
    attributes = staticmethod(attributes)


class ShapeEllipse(BasicRecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_ELLIPSE
    Flags = Flags(UINT32) # TODO
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


class ShapeArc(BasicRecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_ARC
    def attributes(cls, context):
        #yield ShapeEllipse.Flags, 'flags' # SPEC
        yield Coord, 'center'
        yield Coord, 'axis1'
        yield Coord, 'axis2'
    attributes = classmethod(attributes)


class ShapePolygon(BasicRecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_POLYGON
    def attributes(cls, context):
        count = yield UINT16, 'count'
        yield ARRAY(Coord, count), 'points'
    attributes = classmethod(attributes)


class ShapeCurve(BasicRecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_CURVE
    def attributes(cls, context):
        count = yield UINT16, 'count'
        yield ARRAY(Coord, count), 'points'
        # TODO: segment type
    attributes = classmethod(attributes)


class ShapeOLE(BasicRecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_OLE
    # TODO


class PictureInfo(Struct):
    def attributes(context):
        yield INT8, 'brightness',
        yield INT8, 'contrast',
        yield BYTE, 'effect',
        yield UINT16, 'binId',
    attributes = staticmethod(attributes)


class ShapePicture(BasicRecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_PICTURE
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


class ShapeContainer(BasicRecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_CONTAINER
    # TODO


class ShapeTextArt(BasicRecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_TEXTART
    # TODO


class ControlData(RecordModel):
    tagid = HWPTAG_CTRL_DATA


class EqEdit(BasicRecordModel):
    tagid = HWPTAG_CTRL_EQEDIT
    # TODO


class ForbiddenChar(BasicRecordModel):
    tagid = HWPTAG_FORBIDDEN_CHAR
    # TODO


class SectionDef(Control):
    ''' 4.2.10.1. 구역 정의 '''
    chid = CHID.SECD
    def attributes(context):
        yield UINT32, 'attr',
        yield HWPUNIT16, 'intercolumnSpacing',
        yield ARRAY(HWPUNIT16, 2), 'grid',
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


class ColumnsDef(Control):
    ''' 4.2.10.2. 단 정의 '''
    chid = CHID.COLD

    Flags = Flags(UINT16,
            0, 1, 'kind',
            2, 9, 'count',
            10, 11, 'direction',
            12, 'sameWidths',
            )
    def attributes(cls, context):
        flags = yield cls.Flags, 'flags'
        flags = cls.Flags(flags)
        yield HWPUNIT16, 'spacing'
        if not flags.sameWidths:
            yield ARRAY(WORD, flags.count), 'widths'
        yield UINT16, 'attr2'
        yield Border, 'splitterStyle'
    attributes = classmethod(attributes)


class HeaderFooter(Control):
    ''' 4.2.10.3. 머리말/꼬리말 '''
    Places = Enum(BOTH_PAGES=0, EVEN_PAGE=1, ODD_PAGE=2)
    Flags = Flags(UINT32,
        0, 1, Places, 'places'
    )
    def attributes(cls, context):
        yield cls.Flags, 'flags'
    attributes = classmethod(attributes)

    class ParagraphList(ListHeader):
        def attributes(context):
            yield HWPUNIT, 'width'
            yield HWPUNIT, 'height'
            yield BYTE, 'textrefsbitmap'
            yield BYTE, 'numberrefsbitmap'
        attributes = staticmethod(attributes)

    def parse_child(cls, attributes, context, (child_context, child_model, child_attributes, child_stream)):
        if child_model is ListHeader:
            return parse_model_attributes(cls.ParagraphList, child_attributes, child_context, child_stream)
        else:
            return child_model, child_attributes
    parse_child = classmethod(parse_child)

class Header(HeaderFooter):
    ''' 머리말 '''
    chid = CHID.HEADER

class Footer(HeaderFooter):
    ''' 꼬리말 '''
    chid = CHID.FOOTER


class Note(Control):
    ''' 4.2.10.4 미주/각주 '''
    def attributes(context):
        if context['version'] >= (5, 0, 0, 6):
            yield UINT32, 'number' # SPEC
    attributes = staticmethod(attributes)

class FootNote(Note):
    ''' 각주 '''
    chid = CHID.FN

class EndNote(Note):
    ''' 미주 '''
    chid = CHID.EN


class NumberingControl(Control):
    Kind = Enum(PAGE=0, FOOTNOTE=1, ENDNOTE=2, PICTURE=3, TABLE=4, EQUATION=5)
    Flags = Flags(UINT32,
            0, 3, Kind, 'kind',
            4, 11, 'footnoteShape',
            12, 'superscript',
            )
    def attributes(cls, context):
        yield cls.Flags, 'flags',
        yield UINT16, 'number',
    attributes = classmethod(attributes)


class AutoNumbering(NumberingControl):
    ''' 4.2.10.5. 자동 번호 '''
    chid = CHID.ATNO
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


class NewNumbering(NumberingControl):
    ''' 4.2.10.6. 새 번호 지정 '''
    chid = CHID.NWNO


class PageHide(Control):
    ''' 4.2.10.7 감추기 '''
    chid = CHID.PGHD
    Flags = Flags(UINT32,
            0, 'header',
            1, 'footer',
            2, 'basepage',
            3, 'pageborder',
            4, 'pagefill',
            5, 'pagenumber'
            )
    def attributes(cls, context):
        yield cls.Flags, 'flags'
    attributes = classmethod(attributes)


class PageOddEven(Control):
    ''' 4.2.10.8 홀/짝수 조정 '''
    chid = CHID.PGCT
    OddEven = Enum(BOTH_PAGES=0, EVEN_PAGE=1, ODD_PAGE=2)
    Flags = Flags(UINT32,
        0, 1, 'pages'
        )
    def attributes(cls, context):
        yield cls.Flags, 'flags'
    attributes = classmethod(attributes)


class PageNumberPosition(Control):
    ''' 4.2.10.9. 쪽 번호 위치 '''
    chid = CHID.PGNP
    Position = Enum(NONE=0,
            TOP_LEFT=1, TOP_CENTER=2, TOP_RIGHT=3,
            BOTTOM_LEFT=4, BOTTOM_CENTER=5, BOTTOM_RIGHT=6,
            OUTSIDE_TOP=7, OUTSIDE_BOTTOM=8,
            INSIDE_TOP=9, INSIDE_BOTTOM=10)
    Flags = Flags(UINT32,
        0, 7, 'shape',
        8, 11, Position, 'position',
        )
    def attributes(cls, context):
        yield cls.Flags, 'pagenumberflags'
        yield WCHAR, 'usersymbol'
        yield WCHAR, 'prefix'
        yield WCHAR, 'suffix'
        yield WCHAR, 'dash'
    attributes = classmethod(attributes)


class IndexMarker(Control):
    ''' 4.2.10.10. 찾아보기 표식 '''
    chid = CHID.IDXM
    def attributes(context):
        yield BSTR, 'keyword1'
        yield BSTR, 'keyword2'
        yield UINT16, 'dummy'
    attributes = staticmethod(attributes)


class BookmarkControl(Control):
    ''' 4.2.10.11. 책갈피 '''
    chid = CHID.BOKM
    def attributes(context):
        if False: yield
    attributes = staticmethod(attributes)

    def parse_child(cls, attributes, context, (child_context, child_model, child_attributes, child_stream)):
        if child_model is ControlData:
            return parse_model_attributes(BookmarkControlData, child_attributes, child_context, child_stream)
        return child_model, child_attributes
    parse_child = classmethod(parse_child)

class BookmarkControlData(ControlData):
    def attributes(context):
        yield UINT32, 'unknown1'
        yield UINT32, 'unknown2'
        yield UINT16, 'unknown3'
        yield BSTR, 'name'
    attributes = staticmethod(attributes)


class TCPSControl(Control):
    ''' 4.2.10.12. 글자 겹침 '''
    chid = CHID.TCPS
    def attributes(context):
        yield BSTR, 'textLength'
        #yield UINT8, 'frameType'
        #yield INT8, 'internalCharacterSize'
        #yield UINT8, 'internalCharacterFold'
        #yield N_ARRAY(UINT8, UINT32), 'characterShapeIds'
    attributes = staticmethod(attributes)


class Dutmal(Control):
    ''' 4.2.10.13. 덧말 '''
    chid = CHID.TDUT
    Position = Enum(ABOVE=0, BELOW=1, CENTER=2)
    Align = Enum(BOTH=0, LEFT=1, RIGHT=2, CENTER=3, DISTRIBUTE=4, DISTRIBUTE_SPACE=5)
    def attributes(context):
        yield BSTR, 'mainText'
        yield BSTR, 'subText'
        yield UINT32, 'position'
        yield UINT32, 'fsizeratio'
        yield UINT32, 'option'
        yield UINT32, 'styleNumber'
        yield UINT32, 'align'
    attributes = staticmethod(attributes)


class HiddenComment(Control):
    ''' 4.2.10.14 숨은 설명 '''
    chid = CHID.TCMT
    def attributes(context):
        if False: yield
    attributes = staticmethod(attributes)


class Field(Control):
    ''' 4.2.10.15 필드 시작 '''

    Flags = Flags(UINT32,
            0, 'editableInReadOnly',
            11, 14, 'visitedType',
            15, 'modified',
            )
    def attributes(cls, context):
        yield cls.Flags, 'flags',
        yield BYTE, 'extra_attr',
        yield BSTR, 'command',
        yield UINT32, 'id',
    attributes = classmethod(attributes)


class FieldUnknown(Field):
    chid = '%unk'

class FieldDate(Field):
    chid = CHID.DTE

class FieldDocDate(Field):
    chid = '%ddt'

class FieldPath(Field):
    chid = '%pat'

class FieldBookmark(Field):
    chid = '%bmk'

class FieldMailMerge(Field):
    chid = '%mmg'

class FieldCrossRef(Field):
    chid = '%xrf'

class FieldFormula(Field):
    chid = '%fmu'

class FieldClickHere(Field):
    chid = '%clk'

class FieldSummary(Field):
    chid = '%smr'

class FieldUserInfo(Field):
    chid = '%usr'

class FieldHyperLink(Field):
    chid = CHID.HLK
    def geturl(self):
        s = self.command.split(';')
        return s[0].replace('\\:', ':')

# TODO: FieldRevisionXXX

class FieldMemo(Field):
    chid = '%%me'

class FieldPrivateInfoSecurity(Field):
    chid = '%cpr'


def _check_tag_models():
    for tagid, name in tagnames.iteritems():
        assert tagid in tag_models, 'RecordModel for %s is missing!'%name
_check_tag_models()

def pass1(context, records):
    for record in records:
        context = dict(context)
        context['hwptag'] = record.tag
        context['recordid'] = record.id
        context['logging'].debug('Record %s at %s:%s:%d', record.tag, *record.id)
        stream = record.bytestream()
        model = tag_models.get(record.tagid, RecordModel)
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

def make_ranged_shapes(shapes):
    last = None
    for item in shapes:
        if last is not None:
            yield (last[0], item[0]), last[1]
        last = item
    yield (item[0], 0x7fffffff), item[1]

def split_and_shape(chunks, ranged_shapes):
    (chunk_start, chunk_end), chunk_attr, chunk = chunks.next()
    for (shape_start, shape_end), shape in ranged_shapes:
        while True:
            # case 0: chunk has left intersection
            #        vvvv
            #      ----...
            if chunk_start < shape_start:
                assert False

            # case 1: chunk is far right: get next shape
            #         vvvv
            #             ----
            if shape_end <= chunk_start:        # (1)
                break

            assert chunk_start < shape_end      # by (1)
            assert shape_start <= chunk_start
            # case 2: chunk has left intersection
            #         vvvv
            #         ..----
            if shape_end < chunk_end:           # (2)
                prev = (chunk_start, shape_end), chunk[:shape_end-chunk_start]
                next = (shape_end, chunk_end), chunk[shape_end-chunk_start:]
                (chunk_start, chunk_end), chunk = prev
            else:
                next = None

            assert chunk_end <= shape_end       # by (2)
            yield (chunk_start, chunk_end), (shape, chunk_attr), chunk

            if next is not None:
                (chunk_start, chunk_end), chunk = next
                continue

            (chunk_start, chunk_end), chunk_attr, chunk = chunks.next()

def line_segmented(chunks, ranged_linesegs):
    prev_lineseg = None
    line = None
    for (chunk_start, chunk_end), (lineseg, chunk_attr), chunk in split_and_shape(chunks, ranged_linesegs):
        if lineseg is not prev_lineseg:
            if line is not None:
                yield prev_lineseg, line
            line = []
        line.append( ((chunk_start, chunk_end), chunk_attr, chunk) )
        prev_lineseg = lineseg
    if line is not None:
        yield prev_lineseg, line

def pass3_lineseg_charshaped_texts(event_prefixed_cmas):
    ''' lineseg/charshaped text chunks '''
    stack = [] # stack of ancestor Paragraphs
    for event, (context, model, attributes, stream) in event_prefixed_cmas:
        if model is Paragraph:
            if event == STARTEVENT:
                stack.append(dict())
                yield STARTEVENT, (context, model, attributes, stream)
            else:
                paratext = stack[-1].get(ParaText)
                paracharshape = stack[-1].get(ParaCharShape)
                paralineseg = stack[-1].get(ParaLineSeg)
                if paratext is None:
                    from cStringIO import StringIO
                    paratext = dict(), ParaText, dict(chunks=[((0,0),'')]), StringIO()
                paratext_context, paratext_model, paratext_attributes, paratext_stream = paratext
                chunks = ((range, None, chunk) for range, chunk in paratext_attributes['chunks'])
                charshapes = paracharshape[2]['charshapes']
                shaped_chunks = split_and_shape(chunks, make_ranged_shapes(charshapes))
                linesegs = ((lineseg['chpos'], lineseg) for lineseg in paralineseg[2]['linesegs'])
                lined_chunks = line_segmented(shaped_chunks, make_ranged_shapes(linesegs))
                for lineseg, line in lined_chunks:
                    yield STARTEVENT, (paralineseg[0], ParaLineSeg.LineSeg, lineseg, paralineseg[3])
                    for (startpos, endpos), (shape, none), chunk in line:
                        if isinstance(chunk, basestring):
                            textitem = (paratext_context, Text, dict(text=chunk, characterShapeId=shape), paratext_stream)
                            yield STARTEVENT, textitem
                            yield ENDEVENT, textitem
                        elif isinstance(chunk, ControlChar):
                            ctrlch = (paratext_context, ControlChar, dict(name=chunk.name, kind=chunk.kind, characterShapeId=shape), paratext_stream)
                            yield STARTEVENT, ctrlch
                            yield ENDEVENT, ctrlch
                    yield ENDEVENT, (paralineseg[0], ParaLineSeg.LineSeg, lineseg, paralineseg[3])
                yield ENDEVENT, (context, model, attributes, stream)
                stack.pop()
        #elif model in (ParaText, ParaCharShape):
        elif model in (ParaText, ParaCharShape, ParaLineSeg):
            if event == STARTEVENT:
                stack[-1][model] = context, model, attributes, stream
        else:
            yield event, (context, model, attributes, stream)

def pass3_inline_extended_controls(event_prefixed_cmas, stack=None):
    ''' inline extended-controls into paragraph texts '''
    if stack is None:
        stack = [] # stack of ancestor Paragraphs
    for event, (context, model, attributes, stream) in event_prefixed_cmas:
        if model is Paragraph:
            if event == STARTEVENT:
                stack.append(dict())
                yield STARTEVENT, (context, model, attributes, stream)
            else:
                yield ENDEVENT, (context, model, attributes, stream)
                stack.pop()
        elif model is ControlChar:
            ctrlch = context, model, attributes, stream
            if event is STARTEVENT:
                if attributes['kind'] is ControlChar.EXTENDED:
                    control_subtree = stack[-1].get(Control).pop(0)
                    tev = tree_events(*control_subtree)
                    yield tev.next() # to evade the Control/STARTEVENT trigger in parse_models_pass3()
                    for k in pass3_inline_extended_controls(tev, stack):
                        yield k
                else:
                    yield STARTEVENT, ctrlch
                    yield ENDEVENT, ctrlch
        elif issubclass(model, Control) and event == STARTEVENT:
            control_subtree = build_subtree(event_prefixed_cmas)
            stack[-1].setdefault(Control, []).append( control_subtree )
        else:
            yield event, (context, model, attributes, stream)

def build_subtree(event_prefixed_items_iterator):
    childs = []
    for event, item in event_prefixed_items_iterator:
        if event == STARTEVENT:
            childs.append(build_subtree(event_prefixed_items_iterator))
        elif event == ENDEVENT:
            return item, childs

def tree_events(rootitem, childs):
    yield STARTEVENT, rootitem
    for child in childs:
        for k in tree_events(*child):
            yield k
    yield ENDEVENT, rootitem

def pass3_field_start_end_pair(event_prefixed_cmas):
    stack = []
    for event, cmas in event_prefixed_cmas:
        (context, model, attributes, stream) = cmas
        if issubclass(model, Field):
            if event is STARTEVENT:
                stack.append(cmas)
                yield event, cmas
            else:
                pass
        elif model is ControlChar and attributes['name'] == 'FIELD_END':
            if event is ENDEVENT:
                yield event, stack.pop()
        else:
            yield event, cmas

def pass3_listheader_paragraphs(event_prefixed_cmas):
    ''' make paragraphs children of the listheader '''
    stack = []
    level = 0
    for event, cmas in event_prefixed_cmas:
        (context, model, attributes, stream) = cmas
        if event is STARTEVENT:
            level += 1
        if len(stack) > 0 and ((event is STARTEVENT and stack[-1][0] == level and model is not Paragraph) or
                               (event is ENDEVENT and stack[-1][0]-1 == level)):
            lh_level, lh_cmas = stack.pop()
            yield ENDEVENT, lh_cmas

        if issubclass(model, ListHeader):
            if event is STARTEVENT:
                stack.append((level, cmas))
                yield event, cmas
            else:
                pass
        else:
            yield event, cmas

        if event is ENDEVENT:
            level -= 1

def parse_models_pass3(event_prefixed_cmas):
    event_prefixed_cmas = pass3_lineseg_charshaped_texts(event_prefixed_cmas)
    event_prefixed_cmas = pass3_inline_extended_controls(event_prefixed_cmas)
    event_prefixed_cmas = pass3_field_start_end_pair(event_prefixed_cmas)
    event_prefixed_cmas = pass3_listheader_paragraphs(event_prefixed_cmas)
    return event_prefixed_cmas

def parse_models(context, records, passes=3):
    result = parse_models_pass1(context, records)
    if passes >= 2:
        result = parse_models_pass2(result)
    if passes >= 3:
        result = parse_models_pass3(result)
    for event, (context, model, attributes, stream) in result:
        if stream is not None:
            context['unparsed'] = stream.read()
        yield event, (model, attributes, context)

def create_context(file=None, **context):
    if file is not None:
        context['version'] = file.fileheader.version
    assert 'version' in context
    assert 'logging' in context
    return context

class ModelEventHandler(object):
    def startModel(self, model, attributes, **kwargs):
        raise NotImplementedError
    def endModel(self, model):
        raise NotImplementedError

def wrap_modelevents(wrapper_model, modelevents):
    yield STARTEVENT, wrapper_model
    for mev in modelevents:
        yield mev
    yield ENDEVENT, wrapper_model

def dispatch_model_events(handler, events):
    for event, (model, attributes, context) in events:
        if event == STARTEVENT:
            handler.startModel(model, attributes, **context)
        elif event == ENDEVENT:
            handler.endModel(model)

def main():
    import sys
    import logging
    import itertools
    from ._scriptutils import OptionParser, args_pop, args_pop_range
    from .filestructure import File
    from .recordstream import read_records

    op = OptionParser(usage='usage: %prog [options] filename <record-stream>')
    op.add_option('--pass', dest='passes', type='int', default=2, help='parsing pass: 1 <= PASSES <= 3 [default: 2]')
    op.add_option('-f', '--format', dest='format', default='xml', help='output format: xml | nul [default: xml]')

    options, args = op.parse_args()

    out = options.outfile

    filename = args_pop(args, 'filename')
    if filename == '-':
        filename = 'STDIN'
        streamname = 'STDIN'
        bytestream = sys.stdin
        version = args_pop(args, 'version').split('.')
    else:
        file = File(filename)
        streamname = args_pop(args, '<record-stream>')
        bytestream = file.pseudostream(streamname)
        version = file.fileheader.version

    records = read_records(bytestream, streamname, filename)

    from xml.sax.saxutils import XMLGenerator
    xmlgen = XMLGenerator(out, 'utf-8')
    class XmlFormat(ModelEventHandler):
        def startDocument(self):
            xmlgen.startDocument()
        def startModel(self, model, attributes, **context):
            def xmlattrval(v):
                if isinstance(v, basestring):
                    return v
                elif isinstance(v, type):
                    return v.__name__
                else:
                    return str(v)
            def xmlattr(item):
                try:
                    name, (type, value) = item
                    return name, xmlattrval(value)
                except Exception, e:
                    context['logging'].error('can\'t serialize xml attribute %s: %s'%(name, repr(v)))
                    context['logging'].exception(e)
                    raise
            recordid = context.get('recordid', ('UNKNOWN', 'UNKNOWN', -1))
            hwptag = context.get('hwptag', '')
            if options.loglevel <= logging.INFO:
                xmlgen._write('<!-- rec:%d %s -->'%(recordid[2], hwptag))
            if model is ParaText:
                if 'chunks' in attributes:
                    chunks = attributes.pop('chunks')
                else:
                    chunks = None
            else:
                pass
            if model is Text:
                text = attributes.pop('text')
            else:
                text = None

            typed_attributes = typed_model_attributes(model, attributes, context)
            xmlgen.startElement(model.__name__, dict(xmlattr(x) for x in typed_attributes))

            if model is Text and text is not None:
                xmlgen.characters(text)
            if model is ParaText and chunks is not None:
                for (start, end), chunk in chunks:
                    chunk_attr = dict(start=str(start), end=str(end))
                    if isinstance(chunk, basestring):
                        xmlgen.startElement('Text', chunk_attr)
                        xmlgen.characters(chunk)
                        xmlgen.endElement('Text')
                    elif isinstance(chunk, ControlChar):
                        chunk_attr['name'] = chunk.name
                        chunk_attr['kind'] = chunk.kind.__name__
                        xmlgen.startElement('ControlChar', chunk_attr)
                        xmlgen.endElement('ControlChar')
                    else:
                        xmlgen._write('<!-- unknown chunk: (%d, %d), %s -->'%(start, end, chunk))
            if options.loglevel <= logging.INFO:
                unparsed = context.get('unparsed', '')
                if len(unparsed) > 0:
                    xmlgen._write('<!-- UNPARSED\n')
                    xmlgen._write(dataio.hexdump(unparsed, True))
                    xmlgen._write('\n-->')
        def endModel(self, model):
            xmlgen.endElement(model.__name__)
        def endDocument(self):
            xmlgen.endDocument()
        def getlogger():
            return getlogger(options, loghandler(out, logformat_xml))

    class NulFormat(ModelEventHandler):
        def startDocument(self): pass
        def endDocument(self): pass
        def startModel(self, model, attributes, **context): pass
        def endModel(self, model): pass

    from ._scriptutils import getlogger, loghandler, logformat_xml
    if options.format == 'xml':
        logger = getlogger(options, loghandler(out, logformat_xml))
    else:
        logger = getlogger(options)

    formats = dict(xml=XmlFormat, nul=NulFormat)
    oformat = formats[options.format]()

    context = create_context(version=version, logging=logger)
    models = parse_models(context, records, options.passes)

    def statistics(models):
        occurrences = dict()
        for event, (model, attributes, context) in models:
            if event is STARTEVENT:
                occurrences.setdefault(model, 0)
                occurrences[model] += 1
            yield event, (model, attributes, context)
        for model, count in occurrences.iteritems():
            logger.info('%30s: %d', model.__name__, count)
    models = statistics(models)

    class Records(object): pass
    models = wrap_modelevents((Records, dict(filename=filename, streamid=streamname), dict(context)), models)

    oformat.startDocument()
    dispatch_model_events(oformat, models)
    oformat.endDocument()
