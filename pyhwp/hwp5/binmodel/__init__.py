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

from hwp5 import recordstream
from hwp5.treeop import STARTEVENT
from hwp5.treeop import ENDEVENT
from hwp5.bintype import resolve_type_events
from hwp5.bintype import resolve_values_from_stream
from hwp5.dataio import ParseError
from hwp5.bintype import ERROREVENT
from hwp5.tagids import tagnames
from hwp5.importhelper import importStringIO
from hwp5.recordstream import nth
from hwp5.binmodel._shared import tag_models
from hwp5.binmodel._shared import RecordModel
from hwp5.binmodel._shared import BinStorageId
from hwp5.binmodel._shared import COLORREF
from hwp5.binmodel._shared import Margin
from hwp5.binmodel.controlchar import CHID
from hwp5.binmodel.controlchar import ControlChar
from hwp5.binmodel.tagid16_document_properties import DocumentProperties
from hwp5.binmodel.tagid17_id_mappings import IdMappings
from hwp5.binmodel.tagid18_bin_data import BinData
from hwp5.binmodel.tagid20_border_fill import BorderFill
from hwp5.binmodel.tagid19_face_name import FaceName
from hwp5.binmodel.tagid21_char_shape import CharShape
from hwp5.binmodel.tagid21_char_shape import LanguageStruct
from hwp5.binmodel.tagid22_tab_def import TabDef
from hwp5.binmodel.tagid23_numbering import Numbering
from hwp5.binmodel.tagid24_bullet import Bullet
from hwp5.binmodel.tagid25_para_shape import ParaShape
from hwp5.binmodel.tagid26_style import Style
from hwp5.binmodel.tagid27_doc_data import DocData
from hwp5.binmodel.tagid28_distribute_doc_data import DistributeDocData
from hwp5.binmodel.tagid30_compatible_document import CompatibleDocument
from hwp5.binmodel.tagid31_layout_compatibility import LayoutCompatibility
from hwp5.binmodel.tagid32_unknown import TagModel32
from hwp5.binmodel.tagid50_para_header import Paragraph
from hwp5.binmodel.tagid51_para_text import ParaText
from hwp5.binmodel.tagid51_para_text import ParaTextChunks
from hwp5.binmodel.tagid52_para_char_shape import ParaCharShape
from hwp5.binmodel.tagid53_para_line_seg import ParaLineSeg
from hwp5.binmodel.tagid53_para_line_seg import ParaLineSegList
from hwp5.binmodel.tagid53_para_line_seg import LineSeg
from hwp5.binmodel.tagid54_para_range_tag import ParaRangeTag
from hwp5.binmodel.tagid55_ctrl_header import Control
from hwp5.binmodel.controls.bookmark_control import BookmarkControl
from hwp5.binmodel.controls.columns_def import ColumnsDef
from hwp5.binmodel.controls.common_controls import CommonControl
from hwp5.binmodel.controls.dutmal import Dutmal
from hwp5.binmodel.controls.field import Field
from hwp5.binmodel.controls.field import FieldUnknown
from hwp5.binmodel.controls.field import FieldDate
from hwp5.binmodel.controls.field import FieldDocDate
from hwp5.binmodel.controls.field import FieldPath
from hwp5.binmodel.controls.field import FieldBookmark
from hwp5.binmodel.controls.field import FieldMailMerge
from hwp5.binmodel.controls.field import FieldCrossRef
from hwp5.binmodel.controls.field import FieldFormula
from hwp5.binmodel.controls.field import FieldClickHere
from hwp5.binmodel.controls.field import FieldClickHereData
from hwp5.binmodel.controls.field import FieldSummary
from hwp5.binmodel.controls.field import FieldUserInfo
from hwp5.binmodel.controls.field import FieldHyperLink
from hwp5.binmodel.controls.field import FieldMemo
from hwp5.binmodel.controls.field import FieldPrivateInfoSecurity
from hwp5.binmodel.controls.gshape_object_control import GShapeObjectControl
from hwp5.binmodel.controls.header_footer import HeaderFooter
from hwp5.binmodel.controls.header_footer import Header
from hwp5.binmodel.controls.header_footer import Footer
from hwp5.binmodel.controls.hidden_comment import HiddenComment
from hwp5.binmodel.controls.index_marker import IndexMarker
from hwp5.binmodel.controls.note import Note
from hwp5.binmodel.controls.note import FootNote
from hwp5.binmodel.controls.note import EndNote
from hwp5.binmodel.controls.numbering import AutoNumbering
from hwp5.binmodel.controls.numbering import NewNumbering
from hwp5.binmodel.controls.page_hide import PageHide
from hwp5.binmodel.controls.page_number_position import PageNumberPosition
from hwp5.binmodel.controls.page_odd_even import PageOddEven
from hwp5.binmodel.controls.section_def import SectionDef
from hwp5.binmodel.controls.table_control import TableControl
from hwp5.binmodel.controls.tcps_control import TCPSControl
from hwp5.binmodel.tagid56_list_header import ListHeader
from hwp5.binmodel.tagid56_list_header import TableCaption
from hwp5.binmodel.tagid56_list_header import TableCell
from hwp5.binmodel.tagid56_list_header import TextboxParagraphList
from hwp5.binmodel.tagid56_list_header import HeaderParagraphList
from hwp5.binmodel.tagid56_list_header import FooterParagraphList
from hwp5.binmodel.tagid57_page_def import PageDef
from hwp5.binmodel.tagid58_footnote_shape import FootnoteShape
from hwp5.binmodel.tagid59_page_border_fill import PageBorderFill
from hwp5.binmodel.tagid60_shape_component import ShapeComponent
from hwp5.binmodel.tagid61_table import TableBody
from hwp5.binmodel.tagid62_shape_component_line import ShapeLine
from hwp5.binmodel.tagid63_shape_component_rectangle import ShapeRectangle
from hwp5.binmodel.tagid64_shape_component_ellipse import ShapeEllipse
from hwp5.binmodel.tagid65_shape_component_arc import ShapeArc
from hwp5.binmodel.tagid66_shape_component_polygon import ShapePolygon
from hwp5.binmodel.tagid67_shape_component_curve import ShapeCurve
from hwp5.binmodel.tagid68_shape_component_ole import ShapeOLE
from hwp5.binmodel.tagid69_shape_component_picture import ShapePicture
from hwp5.binmodel.tagid70_shape_component_container import ShapeContainer
from hwp5.binmodel.tagid71_ctrl_data import ControlData
from hwp5.binmodel.tagid72_ctrl_eqedit import EqEdit
from hwp5.binmodel.tagid74_shape_component_textart import ShapeTextArt
from hwp5.binmodel.tagid75_form_object import FormObject
from hwp5.binmodel.tagid76_memo_shape import MemoShape
from hwp5.binmodel.tagid77_memo_list import MemoList
from hwp5.binmodel.tagid78_forbidden_char import ForbiddenChar
from hwp5.binmodel.tagid79_chart_data import ChartData
from hwp5.binmodel.tagid99_shape_component_unknown import ShapeUnknown
from hwp5.dataio import dumpbytes
from hwp5.treeop import prefix_ancestors_from_level
from hwp5.utils import JsonObjects
from hwp5.importhelper import importjson

# to suppress pyflake8 warning 'imported but not used'
RecordModel
BinStorageId
COLORREF
Margin
DocumentProperties
BinData
BorderFill
CharShape
LanguageStruct
TabDef
Numbering
Bullet
ParaShape
Style
DocData
DistributeDocData
CompatibleDocument
LayoutCompatibility
TagModel32
Paragraph
ParaText
ParaTextChunks
ParaCharShape
ParaLineSeg
ParaLineSegList
LineSeg
ParaRangeTag
Control
ListHeader
TableCaption
TableCell
TextboxParagraphList
PageDef
FootnoteShape
PageBorderFill
ShapeComponent
TableBody
ShapeLine
ShapeRectangle
ShapeEllipse
ShapeArc
ShapePolygon
ShapeCurve
ShapeOLE
ShapePicture
ShapeContainer
ControlData
EqEdit
ShapeTextArt
FormObject
MemoShape
MemoList
ForbiddenChar
ChartData
ShapeUnknown
CHID
ControlChar
BookmarkControl
ColumnsDef
CommonControl
Dutmal
Field
FieldUnknown
FieldDate
FieldDocDate
FieldPath
FieldBookmark
FieldMailMerge
FieldCrossRef
FieldFormula
FieldClickHere
FieldClickHereData
FieldSummary
FieldUserInfo
FieldHyperLink
FieldMemo
FieldPrivateInfoSecurity
GShapeObjectControl
HeaderFooter
Header
HeaderParagraphList
Footer
FooterParagraphList
HiddenComment
IndexMarker
Note
FootNote
EndNote
AutoNumbering
NewNumbering
PageHide
PageNumberPosition
PageOddEven
SectionDef
TableControl
TCPSControl


StringIO = importStringIO()


logger = logging.getLogger(__name__)


class UnknownTagModel(RecordModel):
    pass


class Text(object):
    pass


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


def parse_models_with_parent(context_models):
    level_prefixed = ((model['level'], (context, model))
                      for context, model in context_models)
    root_item = (dict(), dict())
    ancestors_prefixed = prefix_ancestors_from_level(level_prefixed, root_item)
    for ancestors, (context, model) in ancestors_prefixed:
        context['parent'] = ancestors[-1]
        parse_model(context, model)
        yield context, model


def parse_model(context, model):
    ''' HWPTAG로 모델 결정 후 기본 파싱 '''

    stream = context['stream']
    context['resolve_values'] = resolve_values_from_stream(stream)
    events = resolve_model_events(context, model)
    events = raise_on_errorevent(context, events)
    model['binevents'] = list(events)

    logger.debug('model: %s', model['type'].__name__)
    logger.debug('%s', model['content'])


def raise_on_errorevent(context, events):
    binevents = list()
    for ev, item in events:
        yield ev, item
        binevents.append((ev, item))
        if ev is ERROREVENT:
            e = item['exception']
            msg = 'can\'t parse %s' % item['type']
            pe = ParseError(msg)
            pe.cause = e
            pe.path = context.get('path')
            pe.treegroup = context.get('treegroup')
            pe.record = context.get('record')
            pe.offset = item.get('bin_offset')
            pe.binevents = binevents
            raise pe


def resolve_models(context, records):
    model_contexts = (dict(context, record=record, model=dict(record))
                      for record in records)

    level_prefixed = ((context['model']['level'], context)
                      for context in model_contexts)
    root_item = {}
    ancestors_prefixed = prefix_ancestors_from_level(level_prefixed, root_item)
    for ancestors, context in ancestors_prefixed:
        parent = ancestors[-1]
        context['parent'] = parent, parent.get('model', {})

        record_frame = context['record']
        context['type'] = RecordModel
        context['name'] = record_frame['tagname']
        yield STARTEVENT, context
        for x in resolve_model_events(context, context['model']):
            yield x
        event, item = x
        context['value'] = item
        yield ENDEVENT, context


def resolve_model_events(context, model):

    resolve_values = context['resolve_values']

    model['type'] = model_type = tag_models.get(model['tagid'],
                                                UnknownTagModel)

    for ev, item in resolve_type_events(model_type, context, resolve_values):
        yield ev, item

    model['content'] = item['value']

    extension_types = getattr(model['type'], 'extension_types', None)
    if extension_types:
        key = model['type'].get_extension_key(context, model)
        extension = extension_types.get(key)
        if extension is not None:
            # 예: Control -> TableControl로 바뀌는 경우,
            # Control의 member들은 이미 읽은 상태이고
            # CommonControl, TableControl에서 각각 정의한
            # 멤버들을 읽어들여야 함
            for cls in get_extension_mro(extension, model['type']):
                extension_type_events = resolve_type_events(cls, context,
                                                            resolve_values)
                for ev, item in extension_type_events:
                    yield ev, item
                content = item['value']
                model['content'].update(content)
            model['type'] = extension

    if 'parent' in context:
        parent = context['parent']
        parent_context, parent_model = parent
        parent_type = parent_model.get('type')
        parent_content = parent_model.get('content')

        on_child = getattr(parent_type, 'on_child', None)
        if on_child:
            on_child(parent_content, parent_context, (context, model))


def get_extension_mro(cls, up_to_cls=None):
    import inspect
    from itertools import takewhile
    mro = inspect.getmro(cls)
    mro = takewhile(lambda cls: cls is not up_to_cls, mro)
    mro = list(cls for cls in mro if 'attributes' in cls.__dict__)
    mro = reversed(mro)
    return mro


def model_to_json(model, *args, **kwargs):
    ''' convert a model to json '''
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
        models = self.models(**kwargs)
        return JsonObjects(models, model_to_json)

    def other_formats(self):
        d = super(ModelStream, self).other_formats()
        d['.models'] = self.models_json().open
        return d

    def parse_model_events(self):
        context = dict(version=self.version)

        def resolve_values_from_record(record):
            stream = StringIO(record['payload'])
            return resolve_values_from_stream(stream)

        for group_idx, records in enumerate(self.records_treegrouped()):
            context['treegroup'] = group_idx
            for x in resolve_models(context, records):
                event, item = x
                if item['type'] is RecordModel:
                    if event is STARTEVENT:
                        record_frame = item['record']
                        stream = StringIO(record_frame['payload'])
                        resolve_values = resolve_values_from_stream(stream)
                        item['stream'] = stream
                        item['resolve_values'] = resolve_values
                    elif event is ENDEVENT:
                        stream = item['stream']
                        item['leftover'] = {
                            'offset': stream.tell(),
                            'bytes': stream.read()
                        }
                yield x


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
