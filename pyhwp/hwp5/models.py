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
        yield UINT16, 'section_count',
        yield UINT16, 'page_startnum',
        yield UINT16, 'footnote_startnum',
        yield UINT16, 'endnote_startnum',
        yield UINT16, 'picture_startnum',
        yield UINT16, 'table_startnum',
        yield UINT16, 'math_startnum',
        yield UINT32, 'list_id',
        yield UINT32, 'paragraph_id',
        yield UINT32, 'character_unit_loc_in_paragraph',
        #yield UINT32, 'flags',   # DIFFSPEC
    attributes = staticmethod(attributes)


class IdMappings(BasicRecordModel):
    tagid = HWPTAG_ID_MAPPINGS
    def attributes(context):
        yield UINT16, 'bindata',
        yield UINT16, 'ko_fonts',
        yield UINT16, 'en_fonts',
        yield UINT16, 'cn_fonts',
        yield UINT16, 'jp_fonts',
        yield UINT16, 'other_fonts',
        yield UINT16, 'symbol_fonts',
        yield UINT16, 'user_fonts',
        yield UINT16, 'borderfills',
        yield UINT16, 'charshapes',
        yield UINT16, 'tabdefs',
        yield UINT16, 'numberings',
        yield UINT16, 'bullets',
        yield UINT16, 'parashapes',
        yield UINT16, 'styles',
        yield UINT16, 'memoshapes',
        if context['version'] >= (5, 0, 1, 7):
            yield ARRAY(UINT32, 8), 'unknown' # SPEC
    attributes = staticmethod(attributes)


class BinData(BasicRecordModel):
    tagid = HWPTAG_BIN_DATA
    def attributes(cls, context):
        flags = yield UINT16, 'flags'
        yield [BinLink, BinEmbedded, BinStorage][flags & 3], 'data'
    attributes = classmethod(attributes)


class BinLink(Struct):
    def attributes(context):
        yield BSTR, 'abspath'
        yield BSTR, 'relpath'
    attributes = staticmethod(attributes)

class BinStorageId(UINT16):
    pass

class BinEmbedded(Struct):
    def attributes(context):
        yield BinStorageId, 'storage_id'
        yield BSTR, 'ext'
    attributes = staticmethod(attributes)

    def get_name(self):
        return 'BIN%04X.%s'%(self.storage_id, self.ext) # DIFFSPEC
    name = property(get_name)


class BinStorage(Struct):
    def attributes(context):
        yield UINT16, 'storage_id'
    attributes = staticmethod(attributes)


class AlternateFont(Struct):
    def attributes(context):
        yield BYTE, 'kind'
        yield BSTR, 'name'
    attributes = staticmethod(attributes)


class Panose1(Struct):
    def attributes(context):
        yield BYTE, 'family_kind',
        yield BYTE, 'serif_style',
        yield BYTE, 'weight',
        yield BYTE, 'proportion',
        yield BYTE, 'contrast',
        yield BYTE, 'stroke_variation',
        yield BYTE, 'arm_style',
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
        has = yield cls.Flags, 'has'
        yield BSTR, 'name'
        if has.alternate:
            yield AlternateFont, 'alternate_font'
        if has.metric:
            yield Panose1, 'panose1'
        if has.default:
            yield BSTR, 'default_font'
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
    ''' 표 23 채우기 정보 '''
    def attributes(context):
        yield COLORREF, 'background_color',
        yield COLORREF, 'pattern_color',
        yield INT32, 'pattern_type',
        yield UINT32, 'unknown',
    attributes = staticmethod(attributes)


class FillGradation(Fill):
    def attributes(context):
        yield BYTE,   'type',
        yield UINT32, 'shear',
        yield ARRAY(UINT32, 2), 'center'
        yield UINT32, 'blur',
        yield N_ARRAY(UINT32, COLORREF), 'colors',
        yield UINT32, 'shape',
        yield BYTE,   'blur_center',
    attributes = staticmethod(attributes)


class BorderFill(BasicRecordModel):
    tagid = HWPTAG_BORDER_FILL
    FILL_NONE = 0
    FILL_COLOR_PATTERN = 1
    FILL_GRADATION = 4
    def attributes(cls, context):
        yield UINT16, 'attr'
        yield Border, 'left',
        yield Border, 'right',
        yield Border, 'top',
        yield Border, 'bottom',
        yield Border, 'diagonal'
        fill_type = yield UINT32, 'fill_type'
        if fill_type == cls.FILL_NONE:
            pass
        elif fill_type == cls.FILL_COLOR_PATTERN:
            yield FillColorPattern, 'fill'
        elif fill_type == cls.FILL_GRADATION:
            yield FillGradation, 'fill'
    attributes = classmethod(attributes)


class LanguageStructType(StructType):
    def attributes(cls, context):
        basetype = cls.basetype
        for lang in ('ko', 'en', 'cn', 'jp', 'other', 'symbol', 'user'):
            yield basetype, lang

def LanguageStruct(name, basetype):
    return LanguageStructType(name, (Struct,), dict(basetype=basetype))

class CharShape(BasicRecordModel):
    tagid = HWPTAG_CHAR_SHAPE

    Underline = Enum(NONE=0, UNDERLINE=1, UNKNOWN=2, UPPERLINE=3)
    Flags = Flags(UINT32,
            0, 'italic',
            1, 'bold',
            2, 3, Underline, 'underline',
            4, 7, 'underline_style',
            8, 10, 'outline',
            11, 13, 'shadow')

    def attributes(cls, context):
        yield LanguageStruct('FontFace', WORD), 'font_face',
        yield LanguageStruct('LetterWidthExpansion', UINT8), 'letter_width_expansion'
        yield LanguageStruct('LetterSpacing', INT8), 'letter_spacing'
        yield LanguageStruct('RelativeSize', INT8), 'relative_size'
        yield LanguageStruct('Position', INT8), 'position'
        yield INT32, 'basesize',
        yield cls.Flags, 'charshapeflags',
        yield ARRAY(INT8, 2), 'shadow_space'
        yield COLORREF, 'text_color',
        yield COLORREF, 'underline_color',
        yield COLORREF, 'shade_color',
        yield COLORREF, 'shadow_color',
        #yield UINT16, 'borderfill_id',        # DIFFSPEC
        #yield COLORREF, 'strikeoutColor',    # DIFFSPEC
    attributes = classmethod(attributes)



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
        0, 1, Align, 'paragraph_align',
        2, 'auto_width',
        3, 'auto_dedent',
        4, DistanceType, 'distance_to_body_type',
        )
    def attributes(cls, context):
        yield cls.Flags, 'flags'
        yield HWPUNIT16, 'width_correction'
        yield HWPUNIT16, 'distance_to_body'
        yield UINT32, 'charshape_id' # SPEC ?????
    attributes = classmethod(attributes)
        

class Bullet(BasicRecordModel):
    tagid = HWPTAG_BULLET


class ParaShape(BasicRecordModel):
    ''' 4.1.10. 문단 모양 '''
    tagid = HWPTAG_PARA_SHAPE
    LineSpacingType = Enum(RATIO=0, FIXED=1, SPACEONLY=2, MINIMUM=3)
    Align = Enum(BOTH=0, LEFT=1, RIGHT=2, CENTER=3, DISTRIBUTE=4, DISTRIBUTE_SPACE=5)
    VAlign = Enum(FONT=0, TOP=1, CENTER=2, BOTTOM=3)
    LineBreakAlphabet = Enum(WORD=0, HYPHEN=1, CHAR=2)
    LineBreakHangul = Enum(WORD=0, CHAR=1)
    HeadShape = Enum(NONE=0, OUTLINE=1, NUMBER=2, BULLET=3)
    Flags = Flags(UINT32,
            0, 1, LineSpacingType, 'linespacing_type',
            2, 4, Align, 'align',
            5, 6, LineBreakAlphabet, 'linebreak_alphabet',
            7, LineBreakHangul, 'linebreak_hangul',
            8, 'use_paper_grid',
            9, 15, 'minimum_space', # 공백 최소값
            16, 'protect_single_line', # 외톨이줄 보호
            17, 'with_next_paragraph', # 다음 문단과 함께
            18, 'protect', # 문단 보호
            19, 'start_new_page', # 문단 앞에서 항상 쪽 나눔
            20, 21, VAlign, 'valign', 
            22, 'lineheight_along_fontsize', # 글꼴에 어울리는 줄 높이
            23, 24, HeadShape, 'head_shape', # 문단 머리 모양
            25, 27, 'level', # 문단 수준
            28, 'linked_border', # 문단 테두리 연결 여부
            29, 'ignore_margin', # 문단 여백 무시
            30, 'tail_shape', # 문단 꼬리 모양
            )
    Flags2 = dataio.Flags(UINT32,
            0, 1, 'in_single_line',
            2, 3, 'reserved',
            4, 'autospace_alphabet',
            5, 'autospace_number',
            )
    Flags3 = dataio.Flags(UINT32,
            0, 4, LineSpacingType, 'linespacing_type3'
            )
    def attributes(cls, context):
        yield cls.Flags, 'parashapeflags',
        yield INT32,  'doubled_margin_left',   # 1/7200 * 2 # DIFFSPEC
        yield INT32,  'doubled_margin_right',  # 1/7200 * 2
        yield SHWPUNIT,  'indent',
        yield INT32,  'doubled_margin_top',    # 1/7200 * 2
        yield INT32,  'doubled_margin_bottom', # 1/7200 * 2
        yield SHWPUNIT,  'linespacing',
        yield UINT16, 'tabdef_id',
        yield UINT16, 'numbering_bullet_id',
        yield UINT16, 'borderfill_id',
        yield HWPUNIT16,  'border_left',
        yield HWPUNIT16,  'border_right',
        yield HWPUNIT16,  'border_top',
        yield HWPUNIT16,  'border_bottom',
        if context['version'] > (5, 0, 1, 6):
            yield cls.Flags2, 'flags2',       # above 5016
            #yield cls.Flags3, 'flags3',       # DIFFSPEC
            #yield UINT32, 'lineSpacing', # DIFFSPEC
    attributes = classmethod(attributes)


class Style(BasicRecordModel):
    tagid = HWPTAG_STYLE
    def attributes(context):
        yield BSTR, 'local_name',
        yield BSTR, 'name',
        yield BYTE, 'attr',
        yield BYTE, 'next_style_id',
        yield INT16, 'lang_id',
        yield UINT16, 'parashape_id',
        yield UINT16, 'charshape_id',
        if context['version'] >= (5, 0, 1, 7):
            pass
            #yield UINT16, 'unknown' # SPEC
    attributes = staticmethod(attributes)


class DocData(BasicRecordModel):
    tagid = HWPTAG_DOC_DATA


class DistributeDocData(BasicRecordModel):
    tagid = HWPTAG_DISTRIBUTE_DOC_DATA


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


class Spaces(Struct):
    def attributes(context):
        yield HWPUNIT16, 'left'
        yield HWPUNIT16, 'right'
        yield HWPUNIT16, 'top'
        yield HWPUNIT16, 'bottom'
    attributes = staticmethod(attributes)

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
            8, 9, HRelTo, 'hrelto',
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
        yield SHWPUNIT, 'y',    # DIFFSPEC
        yield SHWPUNIT, 'x',    # DIFFSPEC
        yield HWPUNIT, 'width',
        yield HWPUNIT, 'height',
        yield INT16, 'z_order',
        yield INT16, 'unknown1',
        yield Spaces, 'margin',
        yield UINT32, 'instance_id',
        if context['version'] > (5, 0, 0, 4):
            yield INT16, 'unknown2',
            yield BSTR, 'description'
    attributes = classmethod(attributes)


class TableControl(CommonControl):
    chid = CHID.TBL
    def getBorderFill(self):
        return self.context.mappings[BorderFill][tbl.body.borderfill_id - 1] # TODO: is this right?
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
        5, 6, 'valign',
        )
    VALIGN_MASK     = 0x60
    VALIGN_TOP      = 0x00
    VALIGN_MIDDLE   = 0x20
    VALIGN_BOTTOM   = 0x40
    def attributes(cls, context):
        yield UINT16, 'paragraphs',
        yield UINT16, 'unknown1',
        yield cls.Flags, 'listflags',
    attributes = classmethod(attributes)


class PageDef(BasicRecordModel):
    tagid = HWPTAG_PAGE_DEF
    Orientation = Enum(PORTRAIT=0, LANDSCAPE=1)
    BookBinding = Enum(LEFT=0, RIGHT=1, TOP=2, BOTTOM=3)
    Flags = Flags(UINT32,
                0, Orientation, 'orientation',
                1, 2, BookBinding, 'bookbinding'
                )
    def attributes(cls, context):
        yield HWPUNIT, 'width',
        yield HWPUNIT, 'height',
        yield HWPUNIT, 'left_offset',
        yield HWPUNIT, 'right_offset',
        yield HWPUNIT, 'top_offset',
        yield HWPUNIT, 'bottom_offset',
        yield HWPUNIT, 'header_offset',
        yield HWPUNIT, 'footer_offset',
        yield HWPUNIT, 'bookbinding_offset',
        yield cls.Flags, 'attr',
        #yield UINT32, 'attr',
    attributes = classmethod(attributes)

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
        yield UINT16, 'starting_number'
        yield HWPUNIT16, 'splitter_length'
        yield HWPUNIT16, 'splitter_margin_top'
        yield HWPUNIT16, 'splitter_margin_bottom'
        yield HWPUNIT16, 'notes_spacing'
        yield Border, 'splitter_border'
        if context['version'] >= (5, 0, 0, 6):
            yield UINT16, 'unknown1' # TODO
    attributes = classmethod(attributes)


class PageBorderFill(BasicRecordModel):
    tagid = HWPTAG_PAGE_BORDER_FILL
    RelativeTo = Enum(BODY=0, PAPER=1)
    FillArea = Enum(PAPER=0, PAGE=1, BORDER=2)
    Flags = Flags(UINT32,
        0, RelativeTo, 'relative_to',
        1, 'include_header',
        2, 'include_footer',
        3, 4, FillArea, 'fill',
        )
    def attributes(cls, context):
        yield cls.Flags, 'flags'
        yield Spaces, 'margin'
        yield UINT16, 'borderfill_id'
    attributes = classmethod(attributes)


class TableCaption(ListHeader):
    Position = Enum(LEFT=0, RIGHT=1, TOP=2, BOTTOM=3)
    Flags = Flags(UINT32,
                0, 1, Position, 'position',
                2, 'include_margin',
                )
    def attributes(cls, context):
        yield cls.Flags, 'flags',
        yield HWPUNIT, 'width',
        yield HWPUNIT16, 'separation', # 캡션과 틀 사이 간격
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
        yield Spaces, 'padding',
        yield UINT16, 'borderfill_id',
        yield HWPUNIT, 'unknown_width',
    attributes = staticmethod(attributes)

    def getBorderFill(self):
        return context.mappings[BorderFill][self.borderfill_id - 1] # TODO: is this right?
    borderFill = property(getBorderFill)


class TableBody(BasicRecordModel):
    tagid = HWPTAG_TABLE
    Split = Enum(NONE=0, BY_CELL=1, SPLIT=2)
    Flags = Flags(UINT32,
                0, 1, Split, 'split_page',
                2, 'repeat_header',
                )
    ZoneInfo = ARRAY(UINT16, 5)
    def attributes(cls, context):
        yield cls.Flags, 'flags'
        nRows = yield UINT16, 'rows'
        yield UINT16, 'cols'
        yield HWPUNIT16, 'cellspacing'
        yield Spaces, 'padding'
        yield ARRAY(UINT16, nRows), 'rowcols'
        yield UINT16, 'borderfill_id'
        if context['version'] > (5, 0, 0, 6):
            yield N_ARRAY(UINT16, cls.ZoneInfo), 'validZones' # above 5006
    attributes = classmethod(attributes)


class Paragraph(BasicRecordModel):
    tagid = HWPTAG_PARA_HEADER

    SplitFlags = Flags(BYTE,
            0, 'new_section',
            1, 'new_columnsdef',
            2, 'new_page',
            3, 'new_column',
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
        yield cls.ControlMask, 'controlmask',
        yield UINT16, 'parashape_id',
        yield BYTE, 'style_id',
        yield cls.SplitFlags, 'split',
        yield UINT16, 'charshapes',
        yield UINT16, 'rangetags',
        yield UINT16, 'linesegs',
        yield UINT32, 'instance_id',
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
                yield (idx/2, ctrlpos/2), bytes[idx:ctrlpos].decode('utf-16le', 'replace')
            if ctrlpos < ctrlpos_end:
                yield (ctrlpos/2, ctrlpos_end/2), ControlChar.decode_bytes(bytes[ctrlpos:ctrlpos_end])
            idx = ctrlpos_end
    parseBytes = staticmethod(parseBytes)


class ParaCharShape(RecordModel):
    tagid = HWPTAG_PARA_CHAR_SHAPE
    def parse_with_parent(cls, context, (parent_context, parent_model, parent_attributes, parent_stream), stream, attributes):
        nCharShapes = parent_attributes['charshapes']
        #attributes['charshapes'] = ARRAY(ARRAY(UINT32, 2), nCharShapes).read(stream)
        attributes = cls.decode(stream.read(), context)
        return cls, attributes
    parse_with_parent = classmethod(parse_with_parent)

    def decode(cls, payload, context=None):
        import struct
        fmt = 'II'
        unitsize = struct.calcsize('<'+fmt)
        unitcount = len(payload) / unitsize
        values = struct.unpack('<'+(fmt*unitcount), payload)
        return dict(charshapes=(tuple(values[i*2:i*2+2]) for i in range(0, unitcount)))
    decode = classmethod(decode)


class ParaLineSeg(RecordModel):
    tagid = HWPTAG_PARA_LINE_SEG
    class LineSeg(Struct):
        Flags = Flags(UINT16,
                4, 'indented')
        def attributes(cls, context):
            yield INT32, 'chpos',
            yield SHWPUNIT, 'y',
            yield SHWPUNIT, 'height',
            yield SHWPUNIT, 'height2',
            yield SHWPUNIT, 'height85',
            yield SHWPUNIT, 'space_below',
            yield SHWPUNIT, 'x',
            yield SHWPUNIT, 'width'
            yield UINT16, 'a8'
            yield cls.Flags, 'flags'
        attributes = classmethod(attributes)

    def parse_with_parent(cls, context, (parent_context, parent_model, parent_attributes, parent_stream), stream, attributes):
        nLineSegs = parent_attributes['linesegs']
        #attributes['linesegs'] = ARRAY(cls.LineSeg, nLineSegs).read(stream)
        attributes['linesegs'] = cls.decode(attributes, context, stream.read())
        return cls, attributes
    parse_with_parent = classmethod(parse_with_parent)

    def decode(cls, attributes, context, payload):
        from itertools import izip
        import struct
        unitfmt = 'iiiiiiiiHH'
        unitsize = struct.calcsize('<'+unitfmt)
        unitcount = len(payload) / unitsize
        values = struct.unpack('<'+unitfmt*unitcount, payload)
        names = ['chpos', 'y', 'height', 'height2', 'height85', 'space_below', 'x', 'width', 'a8', 'flags']
        return (dict(izip(names, tuple(values[i*10:i*10+10]))) for i in range(0, unitcount))
    decode = classmethod(decode)


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
    ''' 4.2.9.2 그리기 개체 '''
    tagid = HWPTAG_SHAPE_COMPONENT
    FillFlags = Flags(UINT16,
            8, 'fill_colorpattern',
            9, 'fill_image',
            10, 'fill_gradation',
            )
    Flags = Flags(UINT32,
            0, 'flip'
            )

    def attributes(cls, context):
        chid = yield CHID, 'chid'
        yield SHWPUNIT, 'x_in_group'
        yield SHWPUNIT, 'y_in_group'
        yield WORD, 'level_in_group'
        yield WORD, 'local_version'
        yield SHWPUNIT, 'initial_width'
        yield SHWPUNIT, 'initial_height'
        yield SHWPUNIT, 'width'
        yield SHWPUNIT, 'height'
        yield cls.Flags, 'flags'
        yield WORD, 'angle'
        yield Coord, 'rotation_center'
        nMatrices = yield WORD, 'scalerotations_count'
        yield Matrix, 'translation'
        yield ARRAY(ScaleRotationMatrix, nMatrices), 'scalerotations'
        if chid == CHID.CONTAINER:
            yield N_ARRAY(WORD, CHID), 'controls',
        elif chid == CHID.RECT:
            yield BorderLine, 'border'
            fill_flags = yield cls.FillFlags, 'fill_flags'
            yield UINT16, 'unknown'
            yield UINT8, 'unknown1'
            if fill_flags.fill_colorpattern:
                yield FillColorPattern, 'colorpattern'
            if fill_flags.fill_gradation:
                yield FillGradation, 'gradation'
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
        yield Spaces, 'padding'
        yield HWPUNIT, 'maxwidth'
    attributes = staticmethod(attributes)


class Coord(Struct):
    def attributes(context):
        yield SHWPUNIT, 'x'
        yield SHWPUNIT, 'y'
    attributes = staticmethod(attributes)

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
        yield UINT16, 'bindata_id',
    attributes = staticmethod(attributes)


class BorderLine(Struct):
    ''' 표 81. 테두리 선 정보 '''

    LineEnd = Enum('round', 'flat')
    ArrowShape = Enum('none', 'arrow', 'arrow2', 'diamond', 'circle', 'rect', 'diamondfilled', 'disc', 'rectfilled')
    ArrowSize = Enum('smallest', 'smaller', 'small', 'abitsmall', 'normal', 'abitlarge', 'large', 'larger', 'largest')
    Flags = Flags(UINT32, 
            0, 5, 'type',
            6, 9, LineEnd, 'line_end',
            10, 15, ArrowShape, 'arrow_start',
            16, 21, ArrowShape, 'arrow_end',
            22, 25, ArrowSize, 'arrow_start_size',
            26, 29, ArrowSize, 'arrow_end_size',
            30, 'arrow_start_fill',
            31, 'arrow_end_fill')

    def attributes(cls, context):
        yield COLORREF, 'color'
        yield INT32, 'width'
        yield cls.Flags, 'flags'
    attributes = classmethod(attributes)

class ShapePicture(BasicRecordModel):
    ''' 4.2.9.4. 그림 개체 '''
    tagid = HWPTAG_SHAPE_COMPONENT_PICTURE
    def attributes(context):
        yield BorderLine, 'border'
        yield ARRAY(ARRAY(INT32,2), 4), 'rect',
        yield ARRAY(INT32, 4), 'crop',
        yield ARRAY(UINT16, 4), 'padding',
        yield PictureInfo, 'picture',
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
        yield HWPUNIT16, 'columnspacing',
        yield ARRAY(HWPUNIT16, 2), 'grid',
        yield HWPUNIT, 'defaultTabStops',
        yield UINT16, 'numbering_shape_id',
        yield UINT16, 'starting_pagenum',
        yield UINT16, 'starting_picturenum',
        yield UINT16, 'starting_tablenum',
        yield UINT16, 'starting_equationnum',
        if context['version'] >= (5, 0, 1, 7):
            yield UINT32, 'unknown1',
            yield UINT32, 'unknown2',
    attributes = staticmethod(attributes)


class ColumnsDef(Control):
    ''' 4.2.10.2. 단 정의 '''
    chid = CHID.COLD

    Kind = Enum('normal', 'distribute', 'parallel')
    Direction = Enum('l2r', 'r2l', 'both')
    Flags = Flags(UINT16,
            0, 1, Kind, 'kind',
            2, 9, 'count',
            10, 11, Direction, 'direction',
            12, 'same_widths',
            )
    def attributes(cls, context):
        flags = yield cls.Flags, 'flags'
        flags = cls.Flags(flags)
        yield HWPUNIT16, 'spacing'
        if not flags.same_widths:
            yield ARRAY(WORD, flags.count), 'widths'
        yield UINT16, 'attr2'
        yield Border, 'splitter'
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
            4, 11, 'footnoteshape',
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
        yield cls.Flags, 'flags'
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
        yield BSTR, 'textlength'
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
        yield BSTR, 'maintext'
        yield BSTR, 'subtext'
        yield UINT32, 'position'
        yield UINT32, 'fsizeratio'
        yield UINT32, 'option'
        yield UINT32, 'stylenumber'
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
                    paratext = dict(context), ParaText, dict(chunks=[((0,0),'')]), StringIO()
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
                            textitem = (paratext_context, Text, dict(text=chunk, charshape_id=shape), paratext_stream)
                            yield STARTEVENT, textitem
                            yield ENDEVENT, textitem
                        elif isinstance(chunk, ControlChar):
                            chunk_attributes = dict(name=chunk.name, code=chunk.code, kind=chunk.kind, charshape_id=shape)
                            if chunk.code in (0x9, 0xa, 0xd): # http://www.w3.org/TR/xml/#NT-Char
                                chunk_attributes['char'] = unichr(chunk.code)
                            ctrlch = (paratext_context, ControlChar, chunk_attributes, paratext_stream)
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
    for k in tree_events_childs(childs):
        yield k
    yield ENDEVENT, rootitem

def tree_events_childs(childs):
    for child in childs:
        for k in tree_events(*child):
            yield k

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

def pass3_listheader_paragraphs(event_prefixed_cmas, parentmodel=ListHeader, childmodel=Paragraph):
    ''' make paragraphs children of the listheader '''
    stack = []
    level = 0
    for event, cmas in event_prefixed_cmas:
        (context, model, attributes, stream) = cmas
        if event is STARTEVENT:
            level += 1
        if len(stack) > 0 and ((event is STARTEVENT and stack[-1][0] == level and model is not childmodel) or
                               (event is ENDEVENT and stack[-1][0]-1 == level)):
            lh_level, lh_cmas = stack.pop()
            yield ENDEVENT, lh_cmas

        if issubclass(model, parentmodel):
            if event is STARTEVENT:
                stack.append((level, cmas))
                yield event, cmas
            else:
                pass
        else:
            yield event, cmas

        if event is ENDEVENT:
            level -= 1

def pass3_tablebody(event_prefixed_cmas):
    from collections import deque
    class TableRow: pass
    stack = []
    for event, item in event_prefixed_cmas:
        (context, model, attributes, stream) = item
        if model is TableBody:
            if event is STARTEVENT:
                rowcols = deque()
                for cols in attributes.pop('rowcols'):
                    if cols == 1:
                        rowcols.append(3)
                    else:
                        rowcols.append(1)
                        for i in range(0, cols-2):
                            rowcols.append(0)
                        rowcols.append(2)
                stack.append((context, rowcols))
                yield event, item
            else:
                yield event, item
                stack.pop()
        elif model is TableCell:
            table_context, rowcols = stack[-1]
            row_context = dict(table_context)
            if event is STARTEVENT:
                how = rowcols[0]
                if how & 1:
                    yield STARTEVENT, (row_context, TableRow, dict(), None)
            yield event, item
            if event is ENDEVENT:
                how = rowcols.popleft()
                if how & 2:
                    yield ENDEVENT, (row_context, TableRow, dict(), None)
        else:
            yield event, item

def parse_models_pass3(event_prefixed_cmas):
    event_prefixed_cmas = pass3_lineseg_charshaped_texts(event_prefixed_cmas)
    event_prefixed_cmas = pass3_inline_extended_controls(event_prefixed_cmas)
    event_prefixed_cmas = pass3_field_start_end_pair(event_prefixed_cmas)
    event_prefixed_cmas = pass3_listheader_paragraphs(event_prefixed_cmas)
    event_prefixed_cmas = pass3_listheader_paragraphs(event_prefixed_cmas, TableBody, TableCell)
    event_prefixed_cmas = pass3_tablebody(event_prefixed_cmas)
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
    from ._scriptutils import OptionParser, args_pop, args_pop_range, open_or_exit
    from .filestructure import open
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
        file = open_or_exit(open, filename)
        streamname = args_pop(args, '<record-stream>')
        bytestream = file.pseudostream(streamname)
        version = file.fileheader.version

    records = read_records(bytestream, streamname, filename)

    import types
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
                elif isinstance(v, types.GeneratorType):
                    return str(list(v))
                else:
                    return str(v)
            def xmlattr(item):
                try:
                    name, (type, value) = item
                    return name, xmlattrval(value)
                except Exception, e:
                    context['logging'].error('can\'t serialize xml attribute %s: %s'%(name, repr(value)))
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
