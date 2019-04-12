# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2015 mete0r <mete0r@sarangbang.or.kr>
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
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from collections import deque
from itertools import chain
from pprint import pformat
from tempfile import TemporaryFile
import base64
import logging
import sys

from . import binmodel
from . import filestructure
from .binmodel.controls import SectionDef
from .binmodel.controls import TableControl
from .binmodel.controls import GShapeObjectControl
from .binmodel import BinData
from .binmodel import ListHeader
from .binmodel import Paragraph
from .binmodel import Text
from .binmodel import ShapeComponent
from .binmodel import TableBody
from .binmodel import TableCell
from .binmodel import ParaText
from .binmodel import ParaLineSeg
from .binmodel import ParaCharShape
from .binmodel import LineSeg
from .binmodel import ParaRangeTag
from .binmodel import Field
from .binmodel import ControlChar
from .binmodel import Control
from .charsets import tokenize_unicode_by_lang
from .dataio import Struct
from .filestructure import VERSION
from .treeop import STARTEVENT, ENDEVENT
from .treeop import prefix_event
from .treeop import build_subtree
from .treeop import tree_events
from .treeop import tree_events_multi
from .xmlformat import startelement
from .xmlformat import xmlevents_to_bytechunks


PY3 = sys.version_info.major == 3
if PY3:
    basestring = str
    unichr = chr


logger = logging.getLogger(__name__)


def give_elements_unique_id(event_prefixed_mac):
    paragraph_id = 0
    table_id = 0
    gshape_id = 0
    shape_id = 0
    for event, item in event_prefixed_mac:
        (model, attributes, context) = item
        if event == STARTEVENT:
            if model == Paragraph:
                attributes['paragraph_id'] = paragraph_id
                paragraph_id += 1
            elif model == TableControl:
                attributes['table_id'] = table_id
                table_id += 1
            elif model == GShapeObjectControl:
                attributes['gshape_id'] = gshape_id
                gshape_id += 1
            elif model == ShapeComponent:
                attributes['shape_id'] = shape_id
                shape_id += 1
        yield event, item


def make_ranged_shapes(shapes):
    last = None
    for item in shapes:
        if last is not None:
            yield (last[0], item[0]), last[1]
        last = item
    yield (item[0], 0x7fffffff), item[1]


def split_and_shape(chunks, ranged_shapes):
    try:
        (chunk_start, chunk_end), chunk_attr, chunk = next(chunks)
    except StopIteration:
        return
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
                prev = ((chunk_start, shape_end),
                        chunk[:shape_end - chunk_start])
                nexT = ((shape_end, chunk_end),
                        chunk[shape_end - chunk_start:])
                (chunk_start, chunk_end), chunk = prev
            else:
                nexT = None

            assert chunk_end <= shape_end       # by (2)
            yield (chunk_start, chunk_end), (shape, chunk_attr), chunk

            if nexT is not None:
                (chunk_start, chunk_end), chunk = nexT
                continue

            try:
                (chunk_start, chunk_end), chunk_attr, chunk = next(chunks)
            except StopIteration:
                return


def line_segmented(chunks, ranged_linesegs):
    prev_lineseg = None
    line = None
    for ((chunk_start, chunk_end),
         (lineseg, chunk_attr),
         chunk) in split_and_shape(chunks, ranged_linesegs):
        if lineseg is not prev_lineseg:
            if line is not None:
                yield prev_lineseg, line
            line = []
        line.append(((chunk_start, chunk_end), chunk_attr, chunk))
        prev_lineseg = lineseg
    if line is not None:
        yield prev_lineseg, line


def make_texts_linesegmented_and_charshaped(event_prefixed_mac):
    ''' lineseg/charshaped text chunks '''

    stack = []  # stack of ancestor Paragraphs
    for event, item in event_prefixed_mac:
        model, attributes, context = item
        if model is Paragraph:
            if event == STARTEVENT:
                stack.append(dict())
                yield STARTEVENT, item
            else:
                paratext = stack[-1].get(ParaText)
                paracharshape = stack[-1].get(ParaCharShape)
                paralineseg = stack[-1].get(ParaLineSeg)
                # TODO: RangeTags are not used for now
                # pararangetag = stack[-1].get(ParaRangeTag)
                if paratext is None:
                    paratext = (ParaText,
                                dict(chunks=[((0, 0), '')]),
                                dict(context))
                for x in merge_paragraph_text_charshape_lineseg(paratext,
                                                                paracharshape,
                                                                paralineseg):
                    yield x

                yield ENDEVENT, (model, attributes, context)
                stack.pop()
        elif model in (ParaText, ParaCharShape, ParaLineSeg, ParaRangeTag):
            if event == STARTEVENT:
                stack[-1][model] = model, attributes, context
        else:
            yield event, (model, attributes, context)


def merge_paragraph_text_charshape_lineseg(paratext, paracharshape,
                                           paralineseg):

    paratext_model, paratext_attributes, paratext_context = paratext

    chunks = ((range, None, chunk)
              for range, chunk in paratext_attributes['chunks'])
    charshapes = paracharshape[1]['charshapes']
    shaped_chunks = split_and_shape(chunks, make_ranged_shapes(charshapes))

    if paralineseg:
        paralineseg_content = paralineseg[1]
        paralineseg_context = paralineseg[2]
    else:
        # 배포용 문서의 더미 BodyText 에는 LineSeg 정보가 없음
        # (see https://github.com/mete0r/pyhwp/issues/33)
        # 더미 LineSeg를 만들어 준다
        lineseg = dict(chpos=0, y=0, height=0, height2=0, height85=0,
                       space_below=0, x=0, width=0, a8=0, flags=0)
        paralineseg_content = dict(linesegs=[lineseg])
        paralineseg_context = dict()
    linesegs = ((lineseg['chpos'], lineseg)
                for lineseg in paralineseg_content['linesegs'])
    lined_shaped_chunks = line_segmented(shaped_chunks,
                                         make_ranged_shapes(linesegs))
    for lineseg_content, shaped_chunks in lined_shaped_chunks:
        lineseg = (LineSeg, lineseg_content, paralineseg_context)
        chunk_events = range_shaped_textchunk_events(paratext_context,
                                                     shaped_chunks)
        for x in wrap_modelevents(lineseg, chunk_events):
            yield x


def range_shaped_textchunk_events(paratext_context, range_shaped_textchunks):
    for (startpos, endpos), (shape, none), chunk in range_shaped_textchunks:
        if isinstance(chunk, basestring):
            textitem = (Text,
                        dict(text=chunk, charshape_id=shape),
                        paratext_context)
            yield STARTEVENT, textitem
            yield ENDEVENT, textitem
        elif isinstance(chunk, dict):
            code = chunk['code']
            uch = unichr(code)
            name = ControlChar.get_name_by_code(code)
            kind = ControlChar.kinds[uch]
            chunk_attributes = dict(name=name,
                                    code=code,
                                    kind=kind,
                                    charshape_id=shape)
            if code in (0x9, 0xa, 0xd):  # http://www.w3.org/TR/xml/#NT-Char
                chunk_attributes['char'] = uch
            ctrlch = (ControlChar, chunk_attributes, paratext_context)
            yield STARTEVENT, ctrlch
            yield ENDEVENT, ctrlch


def wrap_section(event_prefixed_mac, sect_id=None):
    ''' wrap a section with SectionDef '''
    starting_buffer = list()
    started = False
    sectiondef = None
    for event, item in event_prefixed_mac:
        if started:
            yield event, item
        else:
            model, attributes, context = item
            if model is SectionDef and event is STARTEVENT:
                sectiondef, sectdef_child = build_subtree(event_prefixed_mac)
                if sect_id is not None:
                    attributes['section_id'] = sect_id
                yield STARTEVENT, sectiondef
                for k in tree_events_multi(sectdef_child):
                    yield k
                for evented_item in starting_buffer:
                    yield evented_item
                started = True
            else:
                starting_buffer.append((event, item))
    yield ENDEVENT, sectiondef


class ColumnSet:
    pass


def wrap_columns(event_prefixed_mac):

    stack = []

    for event, item in event_prefixed_mac:
        model, attributes, context = item

        if model is Paragraph:
            if event is STARTEVENT:

                split = attributes['split']
                split = Paragraph.SplitFlags(split)

                if split.new_columnsdef:
                    if stack[-1][0] is ColumnSet:
                        yield ENDEVENT, stack.pop()

                    columns = (ColumnSet, {}, {})
                    stack.append(columns)
                    yield STARTEVENT, columns

        else:
            if event is STARTEVENT:
                stack.append(item)
            else:
                if model != stack[-1][0]:
                    assert stack[-1][0] is ColumnSet
                    yield ENDEVENT, stack.pop()
                stack.pop()

        yield event, item


def make_extended_controls_inline(event_prefixed_mac, stack=None):
    ''' inline extended-controls into paragraph texts '''
    if stack is None:
        stack = []  # stack of ancestor Paragraphs
    for event, item in event_prefixed_mac:
        model, attributes, context = item
        if model is Paragraph:
            for x in meci_paragraph(event, stack, item):
                yield x
        elif model is ControlChar:
            for x in meci_controlchar(event, stack, item, attributes):
                yield x
        elif issubclass(model, Control) and event == STARTEVENT:
            control_subtree = build_subtree(event_prefixed_mac)
            paragraph = stack[-1]
            paragraph_controls = paragraph.setdefault(Control, [])
            paragraph_controls.append(control_subtree)
        else:
            yield event, item


def meci_paragraph(event, stack, item):
    if event == STARTEVENT:
        stack.append(dict())
        yield STARTEVENT, item
    else:
        yield ENDEVENT, item
        stack.pop()


def meci_controlchar(event, stack, item, attributes):
    if event is STARTEVENT:
        if attributes['kind'] is ControlChar.EXTENDED:
            paragraph = stack[-1]
            paragraph_controls = paragraph.get(Control)
            control_subtree = paragraph_controls.pop(0)
            tev = tree_events(*control_subtree)
            # to evade the Control/STARTEVENT trigger
            # in parse_models_pass3()
            yield next(tev)

            for k in make_extended_controls_inline(tev, stack):
                yield k
        else:
            yield STARTEVENT, item
            yield ENDEVENT, item


def make_paragraphs_children_of_listheader(event_prefixed_mac,
                                           parentmodel=ListHeader,
                                           childmodel=Paragraph):
    ''' make paragraphs children of the listheader '''
    stack = []
    level = 0
    for event, item in event_prefixed_mac:
        model, attributes, context = item
        if event is STARTEVENT:
            level += 1
        if len(stack) > 0 and ((event is STARTEVENT
                                and stack[-1][0] == level
                                and model is not childmodel) or
                               (event is ENDEVENT
                                and stack[-1][0] - 1 == level)):
            lh_level, lh_item = stack.pop()
            yield ENDEVENT, lh_item

        if issubclass(model, parentmodel):
            if event is STARTEVENT:
                stack.append((level, item))
                yield event, item
            else:
                pass
        else:
            yield event, item

        if event is ENDEVENT:
            level -= 1


def match_field_start_end(event_prefixed_mac):
    stack = []
    for event, item in event_prefixed_mac:
        (model, attributes, context) = item
        if issubclass(model, Field):
            for x in mfse_field(event, stack, item):
                yield x
        elif model is LineSeg:
            for x in mfse_lineseg(event, stack, item):
                yield x
        elif model is ControlChar and attributes['name'] == 'FIELD_END':
            for x in mfse_field_end(event, stack, item):
                yield x
        else:
            yield event, item


def mfse_field(event, stack, item):
    if event is STARTEVENT:
        stack.append(item)
        yield event, item
    else:
        pass


def mfse_lineseg(event, stack, item):
    if event is ENDEVENT:
        # fields still not closed; temporarily close them
        for field_item in reversed(stack):
            yield ENDEVENT, field_item
        yield event, item
    elif event is STARTEVENT:
        yield event, item
        # fields temporarily closed; open them again
        for field_item in stack:
            yield STARTEVENT, field_item


def mfse_field_end(event, stack, item):
    if event is ENDEVENT:
        if len(stack) > 0:
            yield event, stack.pop()
        else:
            logger.warning('unmatched field end')


class TableRow:
    pass


ROW_OPEN = 1
ROW_CLOSE = 2


def restructure_tablebody(event_prefixed_mac):
    ''' Group table columns in each rows and wrap them with TableRow. '''
    stack = []
    for event, item in event_prefixed_mac:
        (model, attributes, context) = item
        if model is TableBody:
            for x in rstbody_tablebody(event, stack, item, attributes,
                                       context):
                yield x
        elif model is TableCell:
            for x in rstbody_tablecell(event, stack, item):
                yield x
        else:
            yield event, item


def rstbody_tablebody(event, stack, item, attributes, context):
    if event is STARTEVENT:
        rowcols = deque()
        for cols in attributes.pop('rowcols'):
            if cols == 1:
                rowcols.append(ROW_OPEN | ROW_CLOSE)
            else:
                rowcols.append(ROW_OPEN)
                for i in range(0, cols - 2):
                    rowcols.append(0)
                rowcols.append(ROW_CLOSE)
        stack.append((context, rowcols))
        yield event, item
    else:
        yield event, item
        stack.pop()


def rstbody_tablecell(event, stack, item):
    table_context, rowcols = stack[-1]
    row_context = dict(table_context)
    if event is STARTEVENT:
        how = rowcols[0]
        if how & ROW_OPEN:
            yield STARTEVENT, (TableRow, dict(), row_context)
    yield event, item
    if event is ENDEVENT:
        how = rowcols.popleft()
        if how & ROW_CLOSE:
            yield ENDEVENT, (TableRow, dict(), row_context)


def tokenize_text_by_lang(event_prefixed_mac):
    ''' Group table columns in each rows and wrap them with TableRow. '''
    for event, item in event_prefixed_mac:
        (model, attributes, context) = item
        if model is Text:
            if event is STARTEVENT:
                charshape_id = attributes['charshape_id']
                for lang, text in tokenize_unicode_by_lang(attributes['text']):
                    token = (Text, {
                        'charshape_id': charshape_id,
                        'lang': lang,
                        'text': text,
                    }, context)
                    yield STARTEVENT, token
                    yield ENDEVENT, token
        else:
            yield event, item


def embed_bindata(event_prefixed_mac, bindata):
    for event, item in event_prefixed_mac:
        (model, attributes, context) = item
        if event is STARTEVENT and model is BinData:
            if attributes['flags'].storage is BinData.StorageType.EMBEDDING:
                name = ('BIN%04X' % attributes['bindata']['storage_id']
                        + '.'
                        + attributes['bindata']['ext'])
                bin_stream = bindata[name].open()
                try:
                    binary = bin_stream.read()
                finally:
                    bin_stream.close()
                b64 = base64.b64encode(binary)
                b64 = b64.decode('ascii')
                truncated = []
                while b64:
                    if len(b64) > 64:
                        truncated.append(b64[:64])
                        b64 = b64[64:]
                    else:
                        truncated.append(b64)
                        b64 = ''
                b64 = '\n'.join(truncated)
                b64 = '\n' + b64 + '\n'
                attributes['bindata']['<text>'] = b64
                attributes['bindata']['inline'] = 'true'
        yield event, item


def prefix_binmodels_with_event(context, models):
    level_prefixed = ((model['level'],
                       (model['type'], model['content'], context))
                      for model in models)
    return prefix_event(level_prefixed)


def wrap_modelevents(wrapper_model, modelevents):
    yield STARTEVENT, wrapper_model
    for mev in modelevents:
        yield mev
    yield ENDEVENT, wrapper_model


def modelevents_to_xmlevents(modelevents):
    for event, (model, attributes, context) in modelevents:
        try:
            if event is STARTEVENT:
                for x in startelement(context, (model, attributes)):
                    yield x
            elif event is ENDEVENT:
                yield ENDEVENT, model.__name__
        except:
            logger.error('model: %s', pformat({
                'event': event,
                'model': model,
                'attributes': attributes,
                'context': context
            }))
            raise


class XmlEvents(object):

    def __init__(self, events):
        self.events = events

    def __iter__(self):
        return modelevents_to_xmlevents(self.events)

    def bytechunks(self, xml_declaration=True, **kwargs):
        encoding = kwargs.get('xml_encoding', 'utf-8')
        if xml_declaration:
            yield '<?xml version="1.0" encoding="{}"?>\n'.format(
                encoding
            ).encode(
                encoding
            )
        bytechunks = xmlevents_to_bytechunks(self, encoding)
        for chunk in bytechunks:
            yield chunk

    def dump(self, outfile, **kwargs):
        bytechunks = self.bytechunks(**kwargs)
        for chunk in bytechunks:
            outfile.write(chunk)
        if hasattr(outfile, 'flush'):
            outfile.flush()

    def open(self, **kwargs):
        tmpfile = TemporaryFile()
        try:
            self.dump(tmpfile, **kwargs)
        except:
            tmpfile.close()
            raise

        tmpfile.seek(0)
        return tmpfile


class XmlEventsMixin(object):

    def xmlevents(self, **kwargs):
        return XmlEvents(self.events(**kwargs))


class ModelEventStream(binmodel.ModelStream, XmlEventsMixin):

    def modelevents(self, **kwargs):
        models = self.models(**kwargs)

        # prepare modelevents context
        kwargs.setdefault('version', self.version)
        return prefix_binmodels_with_event(kwargs, models)

    def other_formats(self):
        d = super(ModelEventStream, self).other_formats()
        d['.xml'] = self.xmlevents().open
        return d


class HwpSummaryInfo(filestructure.HwpSummaryInfo, XmlEventsMixin):

    def events(self, **context):
        generator = PropertySetStreamModelEventsGenerator(context)
        events = generator.generateModelEvents(self.propertySetStream)
        element = HwpSummaryInfo, {}, context
        return wrap_modelevents(element, events)


class PropertySetStreamModelEventsGenerator(object):

    def __init__(self, context):
        self.context = context

    def generateModelEvents(self, stream):
        return self.getPropertySetStreamEvents(stream)

    def getPropertySetStreamEvents(self, stream):
        from .msoleprops import PropertySetStream
        sectionEvents = [
            self.getPropertySetEvents(propertyset)
            for propertyset in stream.propertysets
        ]
        events = chain(*sectionEvents)

        content = dict(
            byte_order='{:04x}'.format(
                stream.byteOrder,
            ),
            version=str(stream.version),
            system_identifier='{:08x}'.format(
                stream.systemIdentifier,
            ),
            clsid=str(stream.clsid)
        )
        element = PropertySetStream, content, self.context
        return wrap_modelevents(element, events)

    def getPropertySetEvents(self, propertyset):
        from .msoleprops import PropertySet
        propertyEvents = [
            self.getPropertyEvents(property)
            for property in sorted(
                propertyset.properties,
                key=lambda property: property.desc.offset
            )
        ]
        events = chain(*propertyEvents)

        content = dict(
            fmtid=propertyset.fmtid,
            offset=propertyset.desc.offset,
        )
        element = PropertySet, content, self.context
        return wrap_modelevents(element, events)

    def getPropertyEvents(self, property):
        from .msoleprops import PID_DICTIONARY
        from .msoleprops import Property
        content = dict(
            id=property.desc.id,
            offset=property.desc.offset,
        )
        if property.idLabel is not None:
            content['id_label'] = property.idLabel
        if property.type is not None:
            content['type'] = str(property.type.vt_type.__name__)
            content['type_code'] = '0x{:04x}'.format(property.type.code)
        if property.id == PID_DICTIONARY.id:
            events = self.getDictionaryEvents(property.value)
        else:
            events = ()
            content['value'] = property.value
        element = Property, content, self.context
        return wrap_modelevents(element, events)

    def getDictionaryEvents(self, dictionary):
        events = list(self.getDictionaryEntryEvents(entry)
                      for entry in dictionary.entries)
        return chain(*events)

    def getDictionaryEntryEvents(self, entry):
        from .msoleprops import DictionaryEntry
        content = dict(
            id=entry.id,
            name=entry.name,
        )
        element = DictionaryEntry, content, self.context
        return wrap_modelevents(element, ())


class DocInfo(ModelEventStream):

    def events(self, **kwargs):
        docinfo = DocInfo, dict(), dict()
        events = self.modelevents(**kwargs)
        if 'embedbin' in kwargs:
            events = embed_bindata(events, kwargs['embedbin'])
        events = wrap_modelevents(docinfo, events)
        return events


class Section(ModelEventStream):

    def events(self, **kwargs):
        events = self.modelevents(**kwargs)

        events = make_texts_linesegmented_and_charshaped(events)
        events = make_extended_controls_inline(events)
        events = match_field_start_end(events)
        events = make_paragraphs_children_of_listheader(events)
        events = make_paragraphs_children_of_listheader(events, TableBody,
                                                        TableCell)
        events = restructure_tablebody(events)
        events = tokenize_text_by_lang(events)

        section_idx = kwargs.get('section_idx')
        events = wrap_section(events, section_idx)
        events = wrap_columns(events)

        return events


class Sections(binmodel.Sections, XmlEventsMixin):

    section_class = Section

    def events(self, **kwargs):
        bodytext_events = []
        for idx in self.section_indexes():
            kwargs['section_idx'] = idx
            section = self.section(idx)
            events = section.events(**kwargs)
            bodytext_events.append(events)

        class BodyText(object):
            pass
        bodytext_events = chain(*bodytext_events)
        bodytext = BodyText, dict(), dict()
        return wrap_modelevents(bodytext, bodytext_events)

    def other_formats(self):
        d = super(Sections, self).other_formats()
        d['.xml'] = self.xmlevents().open
        return d


class HwpDoc(Struct):

    def attributes():
        yield VERSION, 'version'
    attributes = staticmethod(attributes)


class Hwp5File(binmodel.Hwp5File, XmlEventsMixin):

    summaryinfo_class = HwpSummaryInfo
    docinfo_class = DocInfo
    bodytext_class = Sections

    def events(self, **kwargs):
        if 'embedbin' in kwargs and kwargs['embedbin'] and 'BinData' in self:
            kwargs['embedbin'] = self['BinData']
        else:
            kwargs.pop('embedbin', None)

        events = chain(self.summaryinfo.events(**kwargs),
                       self.docinfo.events(**kwargs),
                       self.text.events(**kwargs))

        hwpdoc = HwpDoc, dict(version=self.header.version), dict()
        events = wrap_modelevents(hwpdoc, events)

        # for easy references in styles
        events = give_elements_unique_id(events)

        return events
