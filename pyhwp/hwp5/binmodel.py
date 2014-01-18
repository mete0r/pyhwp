# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2014 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import logging
logger = logging.getLogger(__name__)

from .dataio import (PrimitiveType,
                     CompoundType,
                     ArrayType,
                     StructType, Struct, Flags, Enum, BYTE, WORD, UINT32,
                     UINT16, INT32, INT16, UINT8, INT8, DOUBLE, ARRAY, N_ARRAY,
                     SHWPUNIT, HWPUNIT16, HWPUNIT, BSTR, WCHAR)
from .dataio import HexBytes
from .tagids import (tagnames, HWPTAG_DOCUMENT_PROPERTIES, HWPTAG_ID_MAPPINGS,
                     HWPTAG_BIN_DATA, HWPTAG_FACE_NAME, HWPTAG_BORDER_FILL,
                     HWPTAG_CHAR_SHAPE, HWPTAG_TAB_DEF, HWPTAG_NUMBERING,
                     HWPTAG_BULLET, HWPTAG_PARA_SHAPE, HWPTAG_STYLE,
                     HWPTAG_DOC_DATA, HWPTAG_DISTRIBUTE_DOC_DATA,
                     HWPTAG_COMPATIBLE_DOCUMENT, HWPTAG_LAYOUT_COMPATIBILITY,
                     HWPTAG_PARA_HEADER, HWPTAG_PARA_TEXT,
                     HWPTAG_PARA_CHAR_SHAPE, HWPTAG_PARA_LINE_SEG,
                     HWPTAG_PARA_RANGE_TAG, HWPTAG_CTRL_HEADER,
                     HWPTAG_LIST_HEADER, HWPTAG_PAGE_DEF,
                     HWPTAG_FOOTNOTE_SHAPE, HWPTAG_PAGE_BORDER_FILL,
                     HWPTAG_SHAPE_COMPONENT, HWPTAG_TABLE,
                     HWPTAG_SHAPE_COMPONENT_LINE,
                     HWPTAG_SHAPE_COMPONENT_RECTANGLE,
                     HWPTAG_SHAPE_COMPONENT_ELLIPSE,
                     HWPTAG_SHAPE_COMPONENT_ARC,
                     HWPTAG_SHAPE_COMPONENT_POLYGON,
                     HWPTAG_SHAPE_COMPONENT_CURVE, HWPTAG_SHAPE_COMPONENT_OLE,
                     HWPTAG_SHAPE_COMPONENT_PICTURE,
                     HWPTAG_SHAPE_COMPONENT_CONTAINER, HWPTAG_CTRL_DATA,
                     HWPTAG_CTRL_EQEDIT, HWPTAG_SHAPE_COMPONENT_TEXTART,
                     HWPTAG_FORBIDDEN_CHAR)
from .importhelper import importStringIO
from . import dataio
from hwp5.recordstream import nth


StringIO = importStringIO()


def ref_parent_member(member_name):
    def f(context, values):
        context, model = context['parent']
        return model['content'][member_name]
    f.__doc__ = 'PARENTREC.' + member_name
    return f


tag_models = dict()


class RecordModelType(StructType):

    def __new__(mcs, name, bases, attrs):
        cls = StructType.__new__(mcs, name, bases, attrs)
        if 'tagid' in attrs:
            tagid = attrs['tagid']
            assert tagid not in tag_models
            tag_models[tagid] = cls
        return cls


class RecordModel(object):
    __metaclass__ = RecordModelType


class DocumentProperties(RecordModel):
    tagid = HWPTAG_DOCUMENT_PROPERTIES

    def attributes():
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


class IdMappings(RecordModel):
    tagid = HWPTAG_ID_MAPPINGS

    def attributes():
        yield UINT32, 'bindata',
        yield UINT32, 'ko_fonts',
        yield UINT32, 'en_fonts',
        yield UINT32, 'cn_fonts',
        yield UINT32, 'jp_fonts',
        yield UINT32, 'other_fonts',
        yield UINT32, 'symbol_fonts',
        yield UINT32, 'user_fonts',
        yield UINT32, 'borderfills',
        yield UINT32, 'charshapes',
        yield UINT32, 'tabdefs',
        yield UINT32, 'numberings',
        yield UINT32, 'bullets',
        yield UINT32, 'parashapes',
        yield UINT32, 'styles',
        # TODO: memoshapes does not exist at least 5.0.1.6
        yield dict(type=UINT32, name='memoshapes', version=(5, 0, 1, 7))
    attributes = staticmethod(attributes)


class BinStorageId(UINT16):
    pass


class BinDataLink(Struct):
    def attributes():
        yield BSTR, 'abspath'
        yield BSTR, 'relpath'
    attributes = staticmethod(attributes)


class BinDataEmbedding(Struct):
    def attributes():
        yield BinStorageId, 'storage_id'
        yield BSTR, 'ext'
    attributes = staticmethod(attributes)


class BinDataStorage(Struct):
    def attributes():
        yield BinStorageId, 'storage_id'
    attributes = staticmethod(attributes)


class BinData(RecordModel):
    tagid = HWPTAG_BIN_DATA
    StorageType = Enum(LINK=0, EMBEDDING=1, STORAGE=2)
    CompressionType = Enum(STORAGE_DEFAULT=0, YES=1, NO=2)
    AccessState = Enum(NEVER=0, OK=1, FAILED=2, FAILED_IGNORED=3)
    Flags = Flags(UINT16,
                  0, 3, StorageType, 'storage',
                  4, 5, CompressionType, 'compression',
                  16, 17, AccessState, 'access')

    def attributes(cls):
        from hwp5.dataio import SelectiveType
        from hwp5.dataio import ref_member_flag
        yield cls.Flags, 'flags'
        yield (SelectiveType(ref_member_flag('flags', 'storage'),
                             {cls.StorageType.LINK: BinDataLink,
                              cls.StorageType.EMBEDDING: BinDataEmbedding,
                              cls.StorageType.STORAGE: BinDataStorage}),
               'bindata')
    attributes = classmethod(attributes)


class AlternateFont(Struct):
    def attributes():
        yield BYTE, 'kind'
        yield BSTR, 'name'
    attributes = staticmethod(attributes)


class Panose1(Struct):

    FamilyType = Enum('any', 'no_fit', 'text_display', 'script', 'decorative',
                      'pictorial')

    SerifStyle = Enum('any', 'no_fit', 'cove', 'obtuse_cove', 'square_cove',
                      'obtuse_square_cove', 'square', 'thin', 'bone',
                      'exaggerated', 'triangle', 'normal_sans', 'obtuse_sans',
                      'perp_sans', 'flared', 'rounded')

    Weight = Enum('any', 'no_fit', 'very_light', 'light', 'thin', 'book',
                  'medium', 'demi', 'bold', 'heavy', 'black', 'nord')

    Proportion = Enum('any', 'no_fit', 'old_style', 'modern', 'even_width',
                      'expanded', 'condensed', 'very_expanded',
                      'very_condensed', 'monospaced')

    Contrast = Enum('any', 'no_fit', 'none', 'very_low', 'low', 'medium_low',
                    'medium', 'medium_high', 'high', 'very_high')

    StrokeVariation = Enum('any', 'no_fit', 'gradual_diag', 'gradual_tran',
                           'gradual_vert', 'gradual_horz', 'rapid_vert',
                           'rapid_horz', 'instant_vert')

    ArmStyle = Enum('any', 'no_fit', 'straight_horz', 'straight_wedge',
                    'straight_vert', 'straight_single_serif',
                    'straight_double_serif', 'bent_horz', 'bent_wedge',
                    'bent_vert', 'bent_single_serif', 'bent_double_serif')

    Letterform = Enum('any', 'no_fit', 'normal_contact', 'normal_weighted',
                      'normal_boxed', 'normal_flattened', 'normal_rounded',
                      'normal_off_center', 'normal_square', 'oblique_contact',
                      'oblique_weighted', 'oblique_boxed', 'oblique_flattened',
                      'oblique_rounded', 'oblique_off_center',
                      'oblique_square')

    Midline = Enum('any', 'no_fit', 'standard_trimmed', 'standard_pointed',
                   'standard_serifed', 'high_trimmed', 'high_pointed',
                   'high_serifed', 'constant_trimmed', 'constant_pointed',
                   'constant_serifed', 'low_trimmed', 'low_pointed',
                   'low_serifed')

    XHeight = Enum('any', 'no_fit', 'constant_small', 'constant_std',
                   'constant_large', 'ducking_small', 'ducking_std',
                   'ducking_large')

    def attributes():
        yield BYTE, 'family_type',
        yield BYTE, 'serif_style',
        yield BYTE, 'weight',
        yield BYTE, 'proportion',
        yield BYTE, 'contrast',
        yield BYTE, 'stroke_variation',
        yield BYTE, 'arm_style',
        yield BYTE, 'letterform',
        yield BYTE, 'midline',
        yield BYTE, 'x_height',
    attributes = staticmethod(attributes)


class FaceName(RecordModel):
    tagid = HWPTAG_FACE_NAME
    FontFileType = Enum(UNKNOWN=0, TTF=1, HFT=2)
    Flags = Flags(BYTE,
                  0, 1, FontFileType, 'font_file_type',
                  5, 'default',
                  6, 'metric',
                  7, 'alternate')

    def attributes(cls):
        yield cls.Flags, 'flags'
        yield BSTR, 'name'

        def has_alternate(context, values):
            ''' flags.alternate == 1 '''
            return values['flags'].alternate

        def has_metric(context, values):
            ''' flags.metric == 1 '''
            return values['flags'].metric

        def has_default(context, values):
            ''' flags.default == 1 '''
            return values['flags'].default

        yield dict(type=AlternateFont, name='alternate_font',
                   condition=has_alternate)
        yield dict(type=Panose1, name='panose1', condition=has_metric)
        yield dict(type=BSTR, name='default_font', condition=has_default)
    attributes = classmethod(attributes)


class COLORREF(int):
    __metaclass__ = PrimitiveType
    binfmt = INT32.binfmt
    never_instantiate = False

    def __getattr__(self, name):
        if name == 'r':
            return self & 0xff
        elif name == 'g':
            return (self & 0xff00) >> 8
        elif name == 'b':
            return (self & 0xff0000) >> 16
        elif name == 'a':
            return int((self & 0xff000000) >> 24)
        elif name == 'rgb':
            return self.r, self.g, self.b

    def __str__(self):
        return '#%02x%02x%02x' % (self.r, self.g, self.b)

    def __repr__(self):
        class_name = self.__class__.__name__
        value = '(0x%02x, 0x%02x, 0x%02x)' % self.rgb
        return class_name + value


class Border(Struct):

    # 표 20 테두리선 종류
    StrokeEnum = Enum('none', 'solid',
                      'dashed', 'dotted', 'dash-dot', 'dash-dot-dot',
                      'long-dash', 'large-dot',
                      'double', 'double-2', 'double-3', 'triple',
                      'wave', 'double-wave',
                      'inset', 'outset', 'groove', 'ridge')
    StrokeType = Flags(UINT8,
                       0, 4, StrokeEnum, 'stroke_type')

    # 표 21 테두리선 굵기
    widths = {'0.1mm': 0,
              '0.12mm': 1,
              '0.15mm': 2,
              '0.2mm': 3,
              '0.25mm': 4,
              '0.3mm': 5,
              '0.4mm': 6,
              '0.5mm': 7,
              '0.6mm': 8,
              '0.7mm': 9,
              '1.0mm': 10,
              '1.5mm': 11,
              '2.0mm': 12,
              '3.0mm': 13,
              '4.0mm': 14,
              '5.0mm': 15}
    WidthEnum = Enum(**widths)
    Width = Flags(UINT8,
                  0, 4, WidthEnum, 'width')

    def attributes(cls):
        yield cls.StrokeType, 'stroke_flags',
        yield cls.Width, 'width_flags',
        yield COLORREF, 'color',
    attributes = classmethod(attributes)


class Fill(Struct):
    pass


class FillNone(Fill):
    def attributes():
        yield UINT32, 'size',  # SPEC is confusing
    attributes = staticmethod(attributes)


class FillColorPattern(Fill):
    ''' 표 23 채우기 정보 '''
    PatternTypeEnum = Enum(NONE=255, HORIZONTAL=0, VERTICAL=1, BACKSLASH=2,
                           SLASH=3, GRID=4, CROSS=5)
    PatternTypeFlags = Flags(UINT32,
                             0, 7, PatternTypeEnum, 'pattern_type')

    def attributes(cls):
        yield COLORREF, 'background_color',
        yield COLORREF, 'pattern_color',
        yield cls.PatternTypeFlags, 'pattern_type_flags',
    attributes = classmethod(attributes)


class FillImage(Fill):
    def attributes():
        yield UINT32, 'flags'
        yield BinStorageId, 'storage_id'
    attributes = staticmethod(attributes)


class Coord32(Struct):
    def attributes():
        yield UINT32, 'x'
        yield UINT32, 'y'
    attributes = staticmethod(attributes)


class FillGradation(Fill):
    def attributes():
        yield BYTE,   'type',
        yield UINT32, 'shear',
        yield Coord32, 'center',
        yield UINT32, 'blur',
        yield N_ARRAY(UINT32, COLORREF), 'colors',
    attributes = staticmethod(attributes)


class BorderFill(RecordModel):
    tagid = HWPTAG_BORDER_FILL

    BorderFlags = Flags(UINT16,
                        0, 'effect_3d',
                        1, 'effect_shadow',
                        2, 4, 'slash',
                        5, 6, 'backslash')

    FillFlags = Flags(UINT32,
                      0, 'colorpattern',
                      1, 'image',
                      2, 'gradation')

    def attributes(cls):
        yield cls.BorderFlags, 'borderflags'
        yield Border, 'left',
        yield Border, 'right',
        yield Border, 'top',
        yield Border, 'bottom',
        yield Border, 'diagonal'
        yield cls.FillFlags, 'fillflags'

        def fill_colorpattern(context, values):
            ''' fillflags.fill_colorpattern '''
            return values['fillflags'].colorpattern

        def fill_image(context, values):
            ''' fillflags.fill_image '''
            return values['fillflags'].image

        def fill_gradation(context, values):
            ''' fillflags.fill_gradation '''
            return values['fillflags'].gradation

        yield dict(type=FillColorPattern, name='fill_colorpattern',
                   condition=fill_colorpattern)
        yield dict(type=FillGradation, name='fill_gradation',
                   condition=fill_gradation)
        yield dict(type=FillImage, name='fill_image',
                   condition=fill_image)
        yield UINT32, 'shape'
        yield dict(type=BYTE, name='blur_center',
                   condition=fill_gradation)
    attributes = classmethod(attributes)


def LanguageStruct(name, basetype):
    def attributes():
        for lang in ('ko', 'en', 'cn', 'jp', 'other', 'symbol', 'user'):
            yield basetype, lang
    attributes = staticmethod(attributes)
    return StructType(name, (Struct,), dict(basetype=basetype,
                                            attributes=attributes))


class ShadowSpace(Struct):
    def attributes():
        yield INT8, 'x'
        yield INT8, 'y'
    attributes = staticmethod(attributes)


class CharShape(RecordModel):
    tagid = HWPTAG_CHAR_SHAPE

    Underline = Enum(NONE=0, UNDERLINE=1, UNKNOWN=2, UPPERLINE=3)
    Flags = Flags(UINT32,
                  0, 'italic',
                  1, 'bold',
                  2, 3, Underline, 'underline',
                  4, 7, 'underline_style',
                  8, 10, 'outline',
                  11, 13, 'shadow')

    def attributes(cls):
        yield LanguageStruct('FontFace', WORD), 'font_face',
        yield (LanguageStruct('LetterWidthExpansion', UINT8),
               'letter_width_expansion')
        yield LanguageStruct('LetterSpacing', INT8), 'letter_spacing'
        yield LanguageStruct('RelativeSize', INT8), 'relative_size'
        yield LanguageStruct('Position', INT8), 'position'
        yield INT32, 'basesize',
        yield cls.Flags, 'charshapeflags',
        yield ShadowSpace, 'shadow_space'
        yield COLORREF, 'text_color',
        yield COLORREF, 'underline_color',
        yield COLORREF, 'shade_color',
        yield COLORREF, 'shadow_color',
        #yield UINT16, 'borderfill_id',        # DIFFSPEC
        #yield COLORREF, 'strikeoutColor',    # DIFFSPEC
    attributes = classmethod(attributes)


class TabDef(RecordModel):
    tagid = HWPTAG_TAB_DEF

    def attributes():
        # SPEC is confusing
        yield dict(type=UINT32, name='unknown1', version=(5, 0, 1, 7))
        yield dict(type=UINT32, name='unknown2', version=(5, 0, 1, 7))
        #yield UINT32, 'attr',
        #yield UINT16, 'count',
        #yield HWPUNIT, 'pos',
        #yield UINT8, 'kind',
        #yield UINT8, 'fillType',
        #yield UINT16, 'reserved',
    attributes = staticmethod(attributes)


class Numbering(RecordModel):
    tagid = HWPTAG_NUMBERING
    Align = Enum(LEFT=0, CENTER=1, RIGHT=2)
    DistanceType = Enum(RATIO=0, VALUE=1)
    Flags = Flags(UINT32,
                  0, 1, Align, 'paragraph_align',
                  2, 'auto_width',
                  3, 'auto_dedent',
                  4, DistanceType, 'distance_to_body_type')

    def attributes(cls):
        yield cls.Flags, 'flags'
        yield HWPUNIT16, 'width_correction'
        yield HWPUNIT16, 'distance_to_body'
        yield UINT32, 'charshape_id'  # SPEC ?????
    attributes = classmethod(attributes)


class Bullet(RecordModel):
    tagid = HWPTAG_BULLET


class ParaShape(RecordModel):
    ''' 4.1.10. 문단 모양 '''
    tagid = HWPTAG_PARA_SHAPE
    LineSpacingType = Enum(RATIO=0, FIXED=1, SPACEONLY=2, MINIMUM=3)
    Align = Enum(BOTH=0, LEFT=1, RIGHT=2, CENTER=3, DISTRIBUTE=4,
                 DISTRIBUTE_SPACE=5)
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
                  9, 15, 'minimum_space',  # 공백 최소값
                  16, 'protect_single_line',  # 외톨이줄 보호
                  17, 'with_next_paragraph',  # 다음 문단과 함께
                  18, 'protect',  # 문단 보호
                  19, 'start_new_page',  # 문단 앞에서 항상 쪽 나눔
                  20, 21, VAlign, 'valign',
                  22, 'lineheight_along_fontsize',  # 글꼴에 어울리는 줄 높이
                  23, 24, HeadShape, 'head_shape',  # 문단 머리 모양
                  25, 27, 'level',  # 문단 수준
                  28, 'linked_border',  # 문단 테두리 연결 여부
                  29, 'ignore_margin',  # 문단 여백 무시
                  30, 'tail_shape')  # 문단 꼬리 모양

    Flags2 = dataio.Flags(UINT32,
                          0, 1, 'in_single_line',
                          2, 3, 'reserved',
                          4, 'autospace_alphabet',
                          5, 'autospace_number')

    Flags3 = dataio.Flags(UINT32,
                          0, 4, LineSpacingType, 'linespacing_type3')

    def attributes(cls):
        yield cls.Flags, 'parashapeflags',
        yield INT32,  'doubled_margin_left',   # 1/7200 * 2 # DIFFSPEC
        yield INT32,  'doubled_margin_right',  # 1/7200 * 2
        yield SHWPUNIT,  'indent',
        yield INT32,  'doubled_margin_top',    # 1/7200 * 2
        yield INT32,  'doubled_margin_bottom',  # 1/7200 * 2
        yield SHWPUNIT,  'linespacing',
        yield UINT16, 'tabdef_id',
        yield UINT16, 'numbering_bullet_id',
        yield UINT16, 'borderfill_id',
        yield HWPUNIT16,  'border_left',
        yield HWPUNIT16,  'border_right',
        yield HWPUNIT16,  'border_top',
        yield HWPUNIT16,  'border_bottom',
        yield dict(type=cls.Flags2, name='flags2', version=(5, 0, 1, 7))
        #yield cls.Flags3, 'flags3',   # DIFFSPEC
        #yield UINT32, 'lineSpacing',  # DIFFSPEC
    attributes = classmethod(attributes)


class Style(RecordModel):
    tagid = HWPTAG_STYLE

    Kind = Enum(PARAGRAPH=0, CHAR=1)
    Flags = Flags(BYTE,
                  0, 1, Kind, 'kind')

    def attributes(cls):
        yield BSTR, 'local_name',
        yield BSTR, 'name',
        yield cls.Flags, 'flags',
        yield BYTE, 'next_style_id',
        yield INT16, 'lang_id',
        yield UINT16, 'parashape_id',
        yield UINT16, 'charshape_id',
        yield dict(type=UINT16, name='unknown', version=(5, 0, 0, 5))  # SPEC
    attributes = classmethod(attributes)


class DocData(RecordModel):
    tagid = HWPTAG_DOC_DATA


class DistributeDocData(RecordModel):
    tagid = HWPTAG_DISTRIBUTE_DOC_DATA


class CompatibleDocument(RecordModel):
    tagid = HWPTAG_COMPATIBLE_DOCUMENT
    Target = Enum(DEFAULT=0, HWP2007=1, MSWORD=2)
    Flags = dataio.Flags(UINT32,
                         0, 1, 'target')

    def attributes(cls):
        yield cls.Flags, 'flags'
    attributes = classmethod(attributes)


class LayoutCompatibility(RecordModel):
    tagid = HWPTAG_LAYOUT_COMPATIBILITY

    def attributes():
        yield UINT32, 'char',
        yield UINT32, 'paragraph',
        yield UINT32, 'section',
        yield UINT32, 'object',
        yield UINT32, 'field',
    attributes = staticmethod(attributes)


class CHID(str):
    __metaclass__ = PrimitiveType

    fixed_size = 4

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

    def decode(bytes, context=None):
        return bytes[3] + bytes[2] + bytes[1] + bytes[0]
    decode = staticmethod(decode)


control_models = dict()


class ControlType(RecordModelType):

    def __new__(mcs, name, bases, attrs):
        cls = RecordModelType.__new__(mcs, name, bases, attrs)
        if 'chid' in attrs:
            chid = attrs['chid']
            assert chid not in control_models
            control_models[chid] = cls
        return cls


class Control(RecordModel):
    __metaclass__ = ControlType
    tagid = HWPTAG_CTRL_HEADER

    def attributes():
        yield CHID, 'chid'
    attributes = staticmethod(attributes)

    extension_types = control_models

    def get_extension_key(cls, context, model):
        ''' chid '''
        return model['content']['chid']
    get_extension_key = classmethod(get_extension_key)


class Margin(Struct):
    def attributes():
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
    VAlign = Enum(TOP=0, MIDDLE=1, BOTTOM=2)
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

    def attributes(cls):
        yield cls.CommonControlFlags, 'flags',
        yield SHWPUNIT, 'y',    # DIFFSPEC
        yield SHWPUNIT, 'x',    # DIFFSPEC
        yield HWPUNIT, 'width',
        yield HWPUNIT, 'height',
        yield INT16, 'z_order',
        yield INT16, 'unknown1',
        yield Margin, 'margin',
        yield UINT32, 'instance_id',
        yield dict(type=INT16, name='unknown2', version=(5, 0, 0, 5))
        yield dict(type=BSTR, name='description', version=(5, 0, 0, 5))
    attributes = classmethod(attributes)


class TableControl(CommonControl):
    chid = CHID.TBL

    def on_child(cls, attributes, context, child):
        child_context, child_model = child
        if child_model['type'] is TableBody:
            context['table_body'] = True
    on_child = classmethod(on_child)


list_header_models = dict()


class ListHeaderType(RecordModelType):

    def __new__(mcs, name, bases, attrs):
        cls = RecordModelType.__new__(mcs, name, bases, attrs)
        if 'parent_model_type' in attrs:
            parent_model_type = attrs['parent_model_type']
            before_tablebody = attrs.get('before_tablebody', False)
            list_type_key = parent_model_type, before_tablebody
            assert list_type_key not in list_header_models
            list_header_models[list_type_key] = cls
        return cls


class ListHeader(RecordModel):
    __metaclass__ = ListHeaderType
    tagid = HWPTAG_LIST_HEADER

    VAlign = Enum(TOP=0, MIDDLE=1, BOTTOM=2)
    Flags = Flags(UINT32,
                  0, 2, 'textdirection',
                  3, 4, 'linebreak',
                  5, 6, VAlign, 'valign')

    def attributes(cls):
        yield UINT16, 'paragraphs',
        yield UINT16, 'unknown1',
        yield cls.Flags, 'listflags',
    attributes = classmethod(attributes)

    extension_types = list_header_models

    def get_extension_key(context, model):
        ''' (parent model type, after TableBody) '''
        if 'parent' in context:
            context, model = context['parent']
            return model['type'], context.get('table_body', False)
    get_extension_key = staticmethod(get_extension_key)


class PageDef(RecordModel):
    tagid = HWPTAG_PAGE_DEF
    Orientation = Enum(PORTRAIT=0, LANDSCAPE=1)
    BookBinding = Enum(LEFT=0, RIGHT=1, TOP=2, BOTTOM=3)
    Flags = Flags(UINT32,
                  0, Orientation, 'orientation',
                  1, 2, BookBinding, 'bookbinding')

    def attributes(cls):
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
        width = HWPUNIT(self.paper_width - self.offsetLeft - self.offsetRight)
        height = HWPUNIT(self.paper_height
                         - (self.offsetTop + self.offsetHeader)
                         - (self.offsetBottom + self.offsetFooter))
        if self.attr.landscape:
            return (height, width)
        else:
            return (width, height)
    dimension = property(getDimension)

    def getHeight(self):
        if self.attr.landscape:
            width = HWPUNIT(self.paper_width - self.offsetLeft -
                            self.offsetRight)
            return width
        else:
            height = HWPUNIT(self.paper_height
                             - (self.offsetTop + self.offsetHeader)
                             - (self.offsetBottom + self.offsetFooter))
            return height
    height = property(getHeight)

    def getWidth(self):
        if self.attr.landscape:
            height = HWPUNIT(self.paper_height
                             - (self.offsetTop + self.offsetHeader)
                             - (self.offsetBottom + self.offsetFooter))
            return height
        else:
            width = HWPUNIT(self.paper_width - self.offsetLeft -
                            self.offsetRight)
            return width
    width = property(getWidth)


class FootnoteShape(RecordModel):
    tagid = HWPTAG_FOOTNOTE_SHAPE
    Flags = Flags(UINT32)

    def attributes(cls):
        yield cls.Flags, 'flags'
        yield WCHAR, 'usersymbol'
        yield WCHAR, 'prefix'
        yield WCHAR, 'suffix'
        yield UINT16, 'starting_number'
        yield HWPUNIT16, 'splitter_length'
        yield HWPUNIT16, 'splitter_unknown'
        yield HWPUNIT16, 'splitter_margin_top'
        yield HWPUNIT16, 'splitter_margin_bottom'
        yield HWPUNIT16, 'notes_spacing'
        yield Border.StrokeType, 'splitter_stroke_type'
        yield Border.Width, 'splitter_width'
        yield dict(type=COLORREF, name='splitter_color', version=(5, 0, 0, 6))
    attributes = classmethod(attributes)


class PageBorderFill(RecordModel):
    tagid = HWPTAG_PAGE_BORDER_FILL
    RelativeTo = Enum(BODY=0, PAPER=1)
    FillArea = Enum(PAPER=0, PAGE=1, BORDER=2)
    Flags = Flags(UINT32,
                  0, RelativeTo, 'relative_to',
                  1, 'include_header',
                  2, 'include_footer',
                  3, 4, FillArea, 'fill')

    def attributes(cls):
        yield cls.Flags, 'flags'
        yield Margin, 'margin'
        yield UINT16, 'borderfill_id'
    attributes = classmethod(attributes)


class TableCaption(ListHeader):
    parent_model_type = TableControl
    before_tablebody = False

    Position = Enum(LEFT=0, RIGHT=1, TOP=2, BOTTOM=3)
    Flags = Flags(UINT32,
                  0, 1, Position, 'position',
                  2, 'include_margin')

    def attributes(cls):
        yield cls.Flags, 'flags',
        yield HWPUNIT, 'width',
        yield HWPUNIT16, 'separation',  # 캡션과 틀 사이 간격
        yield HWPUNIT, 'maxsize',
    attributes = classmethod(attributes)


class TableCell(ListHeader):
    parent_model_type = TableControl
    before_tablebody = True

    def attributes():
        yield UINT16, 'col',
        yield UINT16, 'row',
        yield UINT16, 'colspan',
        yield UINT16, 'rowspan',
        yield SHWPUNIT, 'width',
        yield SHWPUNIT, 'height',
        yield Margin, 'padding',
        yield UINT16, 'borderfill_id',
        yield SHWPUNIT, 'unknown_width',
    attributes = staticmethod(attributes)


class ZoneInfo(Struct):
    def attributes():
        yield UINT16, 'starting_column'
        yield UINT16, 'starting_row'
        yield UINT16, 'end_column'
        yield UINT16, 'end_row'
        yield UINT16, 'borderfill_id'
    attributes = staticmethod(attributes)


class TableBody(RecordModel):
    tagid = HWPTAG_TABLE
    Split = Enum(NONE=0, BY_CELL=1, SPLIT=2)
    Flags = Flags(UINT32,
                  0, 1, Split, 'split_page',
                  2, 'repeat_header')

    def attributes(cls):
        from hwp5.dataio import X_ARRAY
        from hwp5.dataio import ref_member
        yield cls.Flags, 'flags'
        yield UINT16, 'rows'
        yield UINT16, 'cols'
        yield HWPUNIT16, 'cellspacing'
        yield Margin, 'padding'
        yield dict(type=X_ARRAY(UINT16, ref_member('rows')),
                   name='rowcols')
        yield UINT16, 'borderfill_id'
        yield dict(type=N_ARRAY(UINT16, ZoneInfo),
                   name='validZones',
                   version=(5, 0, 0, 7))
    attributes = classmethod(attributes)


class Paragraph(RecordModel):
    tagid = HWPTAG_PARA_HEADER

    SplitFlags = Flags(BYTE,
                       0, 'new_section',
                       1, 'new_columnsdef',
                       2, 'new_page',
                       3, 'new_column')
    ControlMask = Flags(UINT32,
                        2, 'unknown1',
                        11, 'control',
                        21, 'new_number')
    Flags = Flags(UINT32,
                  31, 'unknown',
                  0, 30, 'chars')

    def attributes(cls):
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
    chars = {0x00: ('NULL', CHAR),
             0x01: ('CTLCHR01', EXTENDED),
             0x02: ('SECTION_COLUMN_DEF', EXTENDED),
             0x03: ('FIELD_START', EXTENDED),
             0x04: ('FIELD_END', INLINE),
             0x05: ('CTLCHR05', INLINE),
             0x06: ('CTLCHR06', INLINE),
             0x07: ('CTLCHR07', INLINE),
             0x08: ('TITLE_MARK', INLINE),
             0x09: ('TAB', INLINE),
             0x0a: ('LINE_BREAK', CHAR),
             0x0b: ('DRAWING_TABLE_OBJECT', EXTENDED),
             0x0c: ('CTLCHR0C', EXTENDED),
             0x0d: ('PARAGRAPH_BREAK', CHAR),
             0x0e: ('CTLCHR0E', EXTENDED),
             0x0f: ('HIDDEN_EXPLANATION', EXTENDED),
             0x10: ('HEADER_FOOTER', EXTENDED),
             0x11: ('FOOT_END_NOTE', EXTENDED),
             0x12: ('AUTO_NUMBER', EXTENDED),
             0x13: ('CTLCHR13', INLINE),
             0x14: ('CTLCHR14', INLINE),
             0x15: ('PAGE_CTLCHR', EXTENDED),
             0x16: ('BOOKMARK', EXTENDED),
             0x17: ('CTLCHR17', EXTENDED),
             0x18: ('HYPHEN', CHAR),
             0x1e: ('NONBREAK_SPACE', CHAR),
             0x1f: ('FIXWIDTH_SPACE', CHAR)}
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
                return i, i + (size * 2)
            data_len = len(data)
            return data_len, data_len
    find = classmethod(find)

    def decode(cls, bytes):
        code = UINT16.decode(bytes[0:2])
        ch = unichr(code)
        if cls.kinds[ch].size == 8:
            bytes = bytes[2:2 + 12]
            if ch == ControlChar.TAB:
                param = dict(width=UINT32.decode(bytes[0:4]),
                             unknown0=UINT8.decode(bytes[4:5]),
                             unknown1=UINT8.decode(bytes[5:6]),
                             unknown2=bytes[6:])
                return dict(code=code, param=param)
            else:
                chid = CHID.decode(bytes[0:4])
                param = bytes[4:12]
                return dict(code=code, chid=chid, param=param)
        else:
            return dict(code=code)
    decode = classmethod(decode)

    def get_kind_by_code(cls, code):
        ch = unichr(code)
        return cls.kinds[ch]
    get_kind_by_code = classmethod(get_kind_by_code)

    def get_name_by_code(cls, code):
        ch = unichr(code)
        return cls.names.get(ch, 'CTLCHR%02x' % code)
    get_name_by_code = classmethod(get_name_by_code)

ControlChar._populate()


class Text(object):
    pass


class ParaTextChunks(list):
    __metaclass__ = CompoundType

    def read(cls, f):
        bytes = f.read()
        return [x for x in cls.parse_chunks(bytes)]
    read = classmethod(read)

    def parse_chunks(bytes):
        from hwp5.dataio import decode_utf16le_with_hypua
        size = len(bytes)
        idx = 0
        while idx < size:
            ctrlpos, ctrlpos_end = ControlChar.find(bytes, idx)
            if idx < ctrlpos:
                text = decode_utf16le_with_hypua(bytes[idx:ctrlpos])
                yield (idx / 2, ctrlpos / 2), text
            if ctrlpos < ctrlpos_end:
                cch = ControlChar.decode(bytes[ctrlpos:ctrlpos_end])
                yield (ctrlpos / 2, ctrlpos_end / 2), cch
            idx = ctrlpos_end
    parse_chunks = staticmethod(parse_chunks)


class ParaText(RecordModel):
    tagid = HWPTAG_PARA_TEXT

    def attributes():
        yield ParaTextChunks, 'chunks'
    attributes = staticmethod(attributes)


class ParaCharShapeList(list):
    __metaclass__ = ArrayType
    itemtype = ARRAY(UINT16, 2)

    def read(cls, f, context):
        bytes = f.read()
        return cls.decode(bytes, context)
    read = classmethod(read)

    def decode(payload, context=None):
        import struct
        fmt = 'II'
        unitsize = struct.calcsize('<' + fmt)
        unitcount = len(payload) / unitsize
        values = struct.unpack('<' + (fmt * unitcount), payload)
        return list(tuple(values[i * 2:i * 2 + 2])
                    for i in range(0, unitcount))
    decode = staticmethod(decode)


class ParaCharShape(RecordModel):
    tagid = HWPTAG_PARA_CHAR_SHAPE

    def attributes():
        from hwp5.dataio import X_ARRAY
        yield dict(name='charshapes',
                   type=X_ARRAY(ARRAY(UINT32, 2),
                                ref_parent_member('charshapes')))
    attributes = staticmethod(attributes)


class LineSeg(Struct):
    Flags = Flags(UINT16,
                  4, 'indented')

    def attributes(cls):
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


class ParaLineSegList(list):
    __metaclass__ = ArrayType
    itemtype = LineSeg

    def read(cls, f, context):
        payload = context['stream'].read()
        return cls.decode(context, payload)
    read = classmethod(read)

    def decode(cls, context, payload):
        from itertools import izip
        import struct
        unitfmt = 'iiiiiiiiHH'
        unitsize = struct.calcsize('<' + unitfmt)
        unitcount = len(payload) / unitsize
        values = struct.unpack('<' + unitfmt * unitcount, payload)
        names = ['chpos', 'y', 'height', 'height2', 'height85', 'space_below',
                 'x', 'width', 'a8', 'flags']
        x = list(dict(izip(names, tuple(values[i * 10:i * 10 + 10])))
                 for i in range(0, unitcount))
        for d in x:
            d['flags'] = LineSeg.Flags(d['flags'])
        return x
    decode = classmethod(decode)


class ParaLineSeg(RecordModel):
    tagid = HWPTAG_PARA_LINE_SEG

    def attributes(cls):
        from hwp5.dataio import X_ARRAY
        yield dict(name='linesegs',
                   type=X_ARRAY(LineSeg, ref_parent_member('linesegs')))
    attributes = classmethod(attributes)


class ParaRangeTag(RecordModel):
    tagid = HWPTAG_PARA_RANGE_TAG

    def attributes():
        yield UINT32, 'start'
        yield UINT32, 'end'
        yield UINT32, 'tag'
        # TODO: SPEC
    attributes = staticmethod(attributes)


class GShapeObjectControl(CommonControl):
    chid = CHID.GSO


class Matrix(Struct):
    ''' 2D Transform Matrix

    [a c e][x]
    [b d f][y]
    [0 0 1][1]
    '''
    def attributes():
        yield DOUBLE, 'a'
        yield DOUBLE, 'c'
        yield DOUBLE, 'e'
        yield DOUBLE, 'b'
        yield DOUBLE, 'd'
        yield DOUBLE, 'f'
    attributes = staticmethod(attributes)


class ScaleRotationMatrix(Struct):
    def attributes():
        yield Matrix, 'scaler',
        yield Matrix, 'rotator',
    attributes = staticmethod(attributes)


class Coord(Struct):
    def attributes():
        yield SHWPUNIT, 'x'
        yield SHWPUNIT, 'y'
    attributes = staticmethod(attributes)


class BorderLine(Struct):
    ''' 표 81. 테두리 선 정보 '''

    LineEnd = Enum('round', 'flat')
    ArrowShape = Enum('none', 'arrow', 'arrow2', 'diamond', 'circle', 'rect',
                      'diamondfilled', 'disc', 'rectfilled')
    ArrowSize = Enum('smallest', 'smaller', 'small', 'abitsmall', 'normal',
                     'abitlarge', 'large', 'larger', 'largest')
    Flags = Flags(UINT32,
                  0, 5, Border.StrokeEnum, 'stroke',
                  6, 9, LineEnd, 'line_end',
                  10, 15, ArrowShape, 'arrow_start',
                  16, 21, ArrowShape, 'arrow_end',
                  22, 25, ArrowSize, 'arrow_start_size',
                  26, 29, ArrowSize, 'arrow_end_size',
                  30, 'arrow_start_fill',
                  31, 'arrow_end_fill')

    def attributes(cls):
        yield COLORREF, 'color'
        yield INT32, 'width'
        yield cls.Flags, 'flags'
    attributes = classmethod(attributes)


class ShapeComponent(RecordModel):
    ''' 4.2.9.2 그리기 개체 '''
    tagid = HWPTAG_SHAPE_COMPONENT
    FillFlags = Flags(UINT16,
                      8, 'fill_colorpattern',
                      9, 'fill_image',
                      10, 'fill_gradation')
    Flags = Flags(UINT32,
                  0, 'flip')

    def attributes(cls):
        from hwp5.dataio import X_ARRAY
        from hwp5.dataio import ref_member

        def parent_must_be_gso(context, values):
            ''' parent record type is GShapeObjectControl '''
            # GSO-child ShapeComponent specific:
            # it may be a GSO model's attribute, e.g. 'child_chid'
            if 'parent' in context:
                parent_context, parent_model = context['parent']
                return parent_model['type'] is GShapeObjectControl

        yield dict(type=CHID, name='chid0', condition=parent_must_be_gso)

        yield CHID, 'chid'
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
        yield WORD, 'scalerotations_count'
        yield Matrix, 'translation'
        yield dict(type=X_ARRAY(ScaleRotationMatrix,
                                ref_member('scalerotations_count')),
                   name='scalerotations')

        def chid_is_container(context, values):
            ''' chid == CHID.CONTAINER '''
            return values['chid'] == CHID.CONTAINER
        yield dict(type=N_ARRAY(WORD, CHID),
                   name='controls',
                   condition=chid_is_container)

        def chid_is_rect(context, values):
            ''' chid == CHID.RECT '''
            return values['chid'] == CHID.RECT

        def chid_is_rect_and_fill_colorpattern(context, values):
            ''' chid == CHID.RECT and fill_flags.fill_colorpattern '''
            return (values['chid'] == CHID.RECT and
                    values['fill_flags'].fill_colorpattern)

        def chid_is_rect_and_fill_image(context, values):
            ''' chid == CHID.RECT and fill_flags.fill_image '''
            return (values['chid'] == CHID.RECT and
                    values['fill_flags'].fill_image)

        def chid_is_rect_and_fill_gradation(context, values):
            ''' chid == CHID.RECT and fill_flags.fill_gradation '''
            return (values['chid'] == CHID.RECT and
                    values['fill_flags'].fill_gradation)

        yield dict(type=BorderLine, name='border', condition=chid_is_rect)
        yield dict(type=cls.FillFlags, name='fill_flags',
                   condition=chid_is_rect)
        yield dict(type=UINT16, name='unknown', condition=chid_is_rect)
        yield dict(type=UINT8, name='unknown1', condition=chid_is_rect)
        yield dict(type=FillColorPattern, name='fill_colorpattern',
                   condition=chid_is_rect_and_fill_colorpattern)
        yield dict(type=FillGradation, name='fill_gradation',
                   condition=chid_is_rect_and_fill_gradation)
        yield dict(type=FillImage, name='fill_image',
                   condition=chid_is_rect_and_fill_image)
        yield dict(type=UINT32, name='fill_shape',
                   condition=chid_is_rect)
        yield dict(type=BYTE, name='fill_blur_center',
                   condition=chid_is_rect_and_fill_gradation)

        # TODO: 아래 두 필드: chid == $rec일 때만인지 확인 필요
        yield dict(type=HexBytes(5), name='unknown2',
                   condition=chid_is_rect, version=(5, 0, 2, 4))
        yield dict(type=HexBytes(16), name='unknown3',
                   condition=chid_is_rect, version=(5, 0, 2, 4))

        def chid_is_line(context, values):
            ''' chid == CHID.LINE '''
            return values['chid'] == CHID.LINE

        yield dict(type=BorderLine, name='line',
                   condition=chid_is_line)
    attributes = classmethod(attributes)


class TextboxParagraphList(ListHeader):
    parent_model_type = ShapeComponent

    def attributes():
        yield Margin, 'padding'
        yield HWPUNIT, 'maxwidth'
    attributes = staticmethod(attributes)


class ShapeLine(RecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_LINE

    def attributes():
        yield Coord, 'p0'
        yield Coord, 'p1'
        yield UINT16, 'attr'
    attributes = staticmethod(attributes)


class ShapeRectangle(RecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_RECTANGLE

    def attributes():
        yield BYTE, 'round',
        yield Coord, 'p0'
        yield Coord, 'p1'
        yield Coord, 'p2'
        yield Coord, 'p3'
    attributes = staticmethod(attributes)


class ShapeEllipse(RecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_ELLIPSE
    Flags = Flags(UINT32)  # TODO

    def attributes(cls):
        yield cls.Flags, 'flags'
        yield Coord, 'center'
        yield Coord, 'axis1'
        yield Coord, 'axis2'
        yield Coord, 'start1'
        yield Coord, 'end1'
        yield Coord, 'start2'
        yield Coord, 'end2'
    attributes = classmethod(attributes)


class ShapeArc(RecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_ARC

    def attributes(cls):
        #yield ShapeEllipse.Flags, 'flags' # SPEC
        yield Coord, 'center'
        yield Coord, 'axis1'
        yield Coord, 'axis2'
    attributes = classmethod(attributes)


class ShapePolygon(RecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_POLYGON

    def attributes(cls):
        yield N_ARRAY(UINT16, Coord), 'points'
    attributes = classmethod(attributes)


class ShapeCurve(RecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_CURVE

    def attributes(cls):
        yield N_ARRAY(UINT16, Coord), 'points'
        # TODO: segment type
    attributes = classmethod(attributes)


class ShapeOLE(RecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_OLE
    # TODO


class PictureInfo(Struct):
    def attributes():
        yield INT8, 'brightness',
        yield INT8, 'contrast',
        yield BYTE, 'effect',
        yield UINT16, 'bindata_id',
    attributes = staticmethod(attributes)


# HWPML에서의 이름 사용
class ImageRect(Struct):
    ''' 이미지 좌표 정보 '''

    def attributes():
        yield Coord, 'p0'
        yield Coord, 'p1'
        yield Coord, 'p2'
        yield Coord, 'p3'
    attributes = staticmethod(attributes)


# HWPML에서의 이름 사용
class ImageClip(Struct):
    ''' 이미지 자르기 정보 '''

    def attributes():
        yield SHWPUNIT, 'left',
        yield SHWPUNIT, 'top',
        yield SHWPUNIT, 'right',
        yield SHWPUNIT, 'bottom',
    attributes = staticmethod(attributes)


class ShapePicture(RecordModel):
    ''' 4.2.9.4. 그림 개체 '''
    tagid = HWPTAG_SHAPE_COMPONENT_PICTURE

    def attributes():
        yield BorderLine, 'border'
        yield ImageRect, 'rect',
        yield ImageClip, 'clip',
        yield Margin, 'padding',
        yield PictureInfo, 'picture',
        # DIFFSPEC
            # BYTE, 'transparency',
            # UINT32, 'instanceId',
            # PictureEffect, 'effect',
    attributes = staticmethod(attributes)


class ShapeContainer(RecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_CONTAINER
    # TODO


class ShapeTextArt(RecordModel):
    tagid = HWPTAG_SHAPE_COMPONENT_TEXTART
    # TODO


control_data_models = dict()


class ControlDataType(RecordModelType):

    def __new__(mcs, name, bases, attrs):
        cls = RecordModelType.__new__(mcs, name, bases, attrs)
        if 'parent_model_type' in attrs:
            parent_model_type = attrs['parent_model_type']
            assert parent_model_type not in control_data_models
            control_data_models[parent_model_type] = cls
        return cls


class ControlData(RecordModel):
    __metaclass__ = ControlDataType
    tagid = HWPTAG_CTRL_DATA

    extension_types = control_data_models

    def get_extension_key(cls, context, model):
        ''' parent model type '''
        parent = context.get('parent')
        if parent:
            return parent[1]['type']
    get_extension_key = classmethod(get_extension_key)


class EqEdit(RecordModel):
    tagid = HWPTAG_CTRL_EQEDIT
    # TODO


class ForbiddenChar(RecordModel):
    tagid = HWPTAG_FORBIDDEN_CHAR
    # TODO


class SectionDef(Control):
    ''' 4.2.10.1. 구역 정의 '''
    chid = CHID.SECD

    Flags = Flags(UINT32,
                  0, 'hide_header',
                  1, 'hide_footer',
                  2, 'hide_page',
                  3, 'hide_border',
                  4, 'hide_background',
                  5, 'hide_pagenumber',
                  8, 'show_border_on_first_page_only',
                  9, 'show_background_on_first_page_only',
                  16, 18, 'text_direction',
                  19, 'hide_blank_line',
                  20, 21, 'pagenum_on_split_section',
                  22, 'squared_manuscript_paper')

    def attributes(cls):
        yield cls.Flags, 'flags',
        yield HWPUNIT16, 'columnspacing',
        yield HWPUNIT16, 'grid_vertical',
        yield HWPUNIT16, 'grid_horizontal',
        yield HWPUNIT, 'defaultTabStops',
        yield UINT16, 'numbering_shape_id',
        yield UINT16, 'starting_pagenum',
        yield UINT16, 'starting_picturenum',
        yield UINT16, 'starting_tablenum',
        yield UINT16, 'starting_equationnum',
        yield dict(type=UINT32, name='unknown1', version=(5, 0, 1, 7))
        yield dict(type=UINT32, name='unknown2', version=(5, 0, 1, 7))
    attributes = classmethod(attributes)


class SectionDefData(ControlData):
    parent_model_type = SectionDef

    def attributes():
        yield HexBytes(280), 'unknown'
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
                  12, 'same_widths')

    def attributes(cls):
        from hwp5.dataio import X_ARRAY
        from hwp5.dataio import ref_member_flag
        yield cls.Flags, 'flags'
        yield HWPUNIT16, 'spacing'

        def not_same_widths(context, values):
            ''' flags.same_widths == 0 '''
            return not values['flags'].same_widths

        yield dict(name='widths',
                   type=X_ARRAY(WORD, ref_member_flag('flags', 'count')),
                   condition=not_same_widths)
        yield UINT16, 'attr2'
        yield Border, 'splitter'
    attributes = classmethod(attributes)


class HeaderFooter(Control):
    ''' 4.2.10.3. 머리말/꼬리말 '''
    Places = Enum(BOTH_PAGES=0, EVEN_PAGE=1, ODD_PAGE=2)
    Flags = Flags(UINT32,
                  0, 1, Places, 'places')

    def attributes(cls):
        yield cls.Flags, 'flags'
    attributes = classmethod(attributes)

    class ParagraphList(ListHeader):
        def attributes():
            yield HWPUNIT, 'width'
            yield HWPUNIT, 'height'
            yield BYTE, 'textrefsbitmap'
            yield BYTE, 'numberrefsbitmap'
        attributes = staticmethod(attributes)


class Header(HeaderFooter):
    ''' 머리말 '''
    chid = CHID.HEADER


class HeaderParagraphList(HeaderFooter.ParagraphList):
    parent_model_type = Header


class Footer(HeaderFooter):
    ''' 꼬리말 '''
    chid = CHID.FOOTER


class FooterParagraphList(HeaderFooter.ParagraphList):
    parent_model_type = Footer


class Note(Control):
    ''' 4.2.10.4 미주/각주 '''
    def attributes():
        yield dict(type=UINT32, name='number', version=(5, 0, 0, 6))  # SPEC
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
                  12, 'superscript')

    def attributes(cls):
        yield cls.Flags, 'flags',
        yield UINT16, 'number',
    attributes = classmethod(attributes)


class AutoNumbering(NumberingControl):
    ''' 4.2.10.5. 자동 번호 '''
    chid = CHID.ATNO

    def attributes(cls):
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
                  5, 'pagenumber')

    def attributes(cls):
        yield cls.Flags, 'flags'
    attributes = classmethod(attributes)


class PageOddEven(Control):
    ''' 4.2.10.8 홀/짝수 조정 '''
    chid = CHID.PGCT
    OddEven = Enum(BOTH_PAGES=0, EVEN_PAGE=1, ODD_PAGE=2)
    Flags = Flags(UINT32,
                  0, 1, OddEven, 'pages')

    def attributes(cls):
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
                  8, 11, Position, 'position')

    def attributes(cls):
        yield cls.Flags, 'flags'
        yield WCHAR, 'usersymbol'
        yield WCHAR, 'prefix'
        yield WCHAR, 'suffix'
        yield WCHAR, 'dash'
    attributes = classmethod(attributes)


class IndexMarker(Control):
    ''' 4.2.10.10. 찾아보기 표식 '''
    chid = CHID.IDXM

    def attributes():
        yield BSTR, 'keyword1'
        yield BSTR, 'keyword2'
        yield UINT16, 'dummy'
    attributes = staticmethod(attributes)


class BookmarkControl(Control):
    ''' 4.2.10.11. 책갈피 '''
    chid = CHID.BOKM

    def attributes():
        if False:
            yield
    attributes = staticmethod(attributes)


class BookmarkControlData(ControlData):

    parent_model_type = BookmarkControl

    def attributes():
        yield UINT32, 'unknown1'
        yield UINT32, 'unknown2'
        yield UINT16, 'unknown3'
        yield BSTR, 'name'
    attributes = staticmethod(attributes)


class TCPSControl(Control):
    ''' 4.2.10.12. 글자 겹침 '''
    chid = CHID.TCPS

    def attributes():
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
    Align = Enum(BOTH=0, LEFT=1, RIGHT=2, CENTER=3, DISTRIBUTE=4,
                 DISTRIBUTE_SPACE=5)

    def attributes(cls):
        yield BSTR, 'maintext'
        yield BSTR, 'subtext'
        yield Flags(UINT32,
                    0, 31, cls.Position, 'position'), 'position'
        yield UINT32, 'fsizeratio'
        yield UINT32, 'option'
        yield UINT32, 'stylenumber'
        yield Flags(UINT32,
                    0, 31, cls.Align, 'align'), 'align'
    attributes = classmethod(attributes)


class HiddenComment(Control):
    ''' 4.2.10.14 숨은 설명 '''
    chid = CHID.TCMT

    def attributes():
        if False:
            yield
    attributes = staticmethod(attributes)


class Field(Control):
    ''' 4.2.10.15 필드 시작 '''

    Flags = Flags(UINT32,
                  0, 'editableInReadOnly',
                  11, 14, 'visitedType',
                  15, 'modified')

    def attributes(cls):
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


class FieldClickHereData(ControlData):
    parent_model_type = FieldClickHere


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
        assert tagid in tag_models, 'RecordModel for %s is missing!' % name
_check_tag_models()


def init_record_parsing_context(base, record):
    ''' Initialize a context to parse the given record

        the initializations includes followings:
        - context = dict(base)
        - context['record'] = record
        - context['stream'] = record payload stream

        :param base: the base context to be shallow-copied into the new one
        :param record: to be parsed
        :returns: new context
    '''

    return dict(base, record=record, stream=StringIO(record['payload']))


from hwp5.bintype import parse_model


def parse_models_with_parent(context_models):
    from .treeop import prefix_ancestors_from_level
    level_prefixed = ((model['level'], (context, model))
                      for context, model in context_models)
    root_item = (dict(), dict())
    ancestors_prefixed = prefix_ancestors_from_level(level_prefixed, root_item)
    for ancestors, (context, model) in ancestors_prefixed:
        context['parent'] = ancestors[-1]
        parse_model(context, model)
        yield context, model


def parse_models(context, records):
    for context, model in parse_models_intern(context, records):
        yield model


def parse_models_intern(context, records):
    context_models = ((init_record_parsing_context(context, record), record)
                      for record in records)
    context_models = parse_models_with_parent(context_models)
    for context, model in context_models:
        stream = context['stream']
        unparsed = stream.read()
        if unparsed:
            model['unparsed'] = unparsed
        yield context, model


def model_to_json(model, *args, **kwargs):
    ''' convert a model to json '''
    from .dataio import dumpbytes
    from hwp5.importhelper import importjson
    json = importjson()
    model = dict(model)
    model['type'] = model['type'].__name__
    record = model
    record['payload'] = list(dumpbytes(record['payload']))
    if 'unparsed' in model:
        model['unparsed'] = list(dumpbytes(model['unparsed']))
    if 'binevents' in model:
        del model['binevents']
    return json.dumps(model, *args, **kwargs)


def chain_iterables(iterables):
    for iterable in iterables:
        for item in iterable:
            yield item


from . import recordstream


class ModelStream(recordstream.RecordStream):

    def models(self, **kwargs):
        # prepare binmodel parsing context
        kwargs.setdefault('version', self.version)
        try:
            kwargs.setdefault('path', self.path)
        except AttributeError:
            pass
        treegroup = kwargs.get('treegroup', None)
        if treegroup is not None:
            records = self.records_treegroup(treegroup)  # TODO: kwargs
            models = parse_models(kwargs, records)
        else:
            groups = self.models_treegrouped(**kwargs)
            models = chain_iterables(groups)
        return models

    def models_treegrouped(self, **kwargs):
        ''' iterable of iterable of the models, grouped by the top-level tree
        '''
        kwargs.setdefault('version', self.version)
        for group_idx, records in enumerate(self.records_treegrouped()):
            kwargs['treegroup'] = group_idx
            yield parse_models(kwargs, records)

    def model(self, idx):
        return nth(self.models(), idx)

    def models_json(self, **kwargs):
        from .utils import JsonObjects
        models = self.models(**kwargs)
        return JsonObjects(models, model_to_json)

    def other_formats(self):
        d = super(ModelStream, self).other_formats()
        d['.models'] = self.models_json().open
        return d


class DocInfo(ModelStream):

    @property
    def idmappings(self):
        for model in self.models():
            if model['type'] is IdMappings:
                return model

    @property
    def facenames_by_lang(self):
        facenames = list(m for m in self.models()
                         if m['type'] is FaceName)
        languages = 'ko', 'en', 'cn', 'jp', 'other', 'symbol', 'user'
        facenames_by_lang = dict()
        offset = 0
        for lang in languages:
            n_fonts = self.idmappings['content'][lang + '_fonts']
            facenames_by_lang[lang] = facenames[offset:offset + n_fonts]
            offset += n_fonts
        return facenames_by_lang

    @property
    def charshapes(self):
        return (m for m in self.models()
                if m['type'] is CharShape)

    def get_charshape(self, charshape_id):
        return nth(self.charshapes, charshape_id)

    def charshape_lang_facename(self, charshape_id, lang):
        charshape = self.get_charshape(charshape_id)
        lang_facename_offset = charshape['content']['font_face'][lang]
        return self.facenames_by_lang[lang][lang_facename_offset]


class Sections(recordstream.Sections):

    section_class = ModelStream


class Hwp5File(recordstream.Hwp5File):

    docinfo_class = DocInfo
    bodytext_class = Sections


def create_context(file=None, **context):
    if file is not None:
        context['version'] = file.fileheader.version
    assert 'version' in context
    return context
