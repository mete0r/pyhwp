from itertools import chain
from .treeop import STARTEVENT, ENDEVENT
from .treeop import build_subtree
from .treeop import tree_events, tree_events_multi
from .binmodel import FaceName, CharShape, SectionDef, ListHeader, Paragraph, Text
from .binmodel import TableControl, GShapeObjectControl, ShapeComponent
from .binmodel import TableBody, TableCell
from . import binmodel

import logging
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

def remove_redundant_facenames(event_prefixed_mac):
    ''' remove redundant FaceNames '''
    facenames = []
    removed_facenames = dict()
    facename_idx = 0
    for event, item in event_prefixed_mac:
        (model, attributes, context) = item
        if event == STARTEVENT and model == FaceName:
            if not attributes in facenames:
                facenames.append(attributes)
                yield event, item
            else:
                # suck this out from the event stream
                build_subtree(event_prefixed_mac)
                removed_facenames[facename_idx] = facenames.index(attributes)
            facename_idx += 1
        else:
            if event == STARTEVENT and model == CharShape:
                fface = attributes['font_face']
                fface2 = dict()
                for k, v in fface.iteritems():
                    if v in removed_facenames:
                        v = removed_facenames[v]
                    fface2[k] = v
                attributes['font_face'] = fface2
            yield event, item

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

def make_texts_linesegmented_and_charshaped(event_prefixed_mac):
    ''' lineseg/charshaped text chunks '''
    from .binmodel import ParaText, ParaLineSeg, ParaCharShape
    from .binmodel import ControlChar
    stack = [] # stack of ancestor Paragraphs
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
                if paratext is None:
                    paratext = ParaText, dict(chunks=[((0,0),'')]), dict(context)
                paratext_model, paratext_attributes, paratext_context = paratext
                chunks = ((range, None, chunk) for range, chunk in paratext_attributes['chunks'])
                charshapes = paracharshape[1]['charshapes']
                shaped_chunks = split_and_shape(chunks, make_ranged_shapes(charshapes))
                linesegs = ((lineseg['chpos'], lineseg) for lineseg in paralineseg[1]['linesegs'])
                lined_chunks = line_segmented(shaped_chunks, make_ranged_shapes(linesegs))
                for lineseg, line in lined_chunks:
                    yield STARTEVENT, (ParaLineSeg.LineSeg, lineseg, paralineseg[2])
                    for (startpos, endpos), (shape, none), chunk in line:
                        if isinstance(chunk, basestring):
                            textitem = (Text, dict(text=chunk, charshape_id=shape), paratext_context)
                            yield STARTEVENT, textitem
                            yield ENDEVENT, textitem
                        elif isinstance(chunk, dict):
                            ch = chr(chunk['code'])
                            if 'chid' in chunk:
                                chunk = ControlChar(ch, chunk['chid'],
                                                    chunk['param'])
                            else:
                                chunk = ControlChar(ch)
                            chunk_attributes = dict(name=chunk.name, code=chunk.code, kind=chunk.kind, charshape_id=shape)
                            if chunk.code in (0x9, 0xa, 0xd): # http://www.w3.org/TR/xml/#NT-Char
                                chunk_attributes['char'] = unichr(chunk.code)
                            ctrlch = (ControlChar, chunk_attributes, paratext_context)
                            yield STARTEVENT, ctrlch
                            yield ENDEVENT, ctrlch
                    yield ENDEVENT, (ParaLineSeg.LineSeg, lineseg, paralineseg[2])
                yield ENDEVENT, (model, attributes, context)
                stack.pop()
        #elif model in (ParaText, ParaCharShape):
        elif model in (ParaText, ParaCharShape, ParaLineSeg):
            if event == STARTEVENT:
                stack[-1][model] = model, attributes, context
        else:
            yield event, (model, attributes, context)

def wrap_section(sect_id, event_prefixed_mac):
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
                sectiondef, sectiondef_childs = build_subtree(event_prefixed_mac)
                attributes['section_id'] = sect_id
                yield STARTEVENT, sectiondef
                for k in tree_events_multi(sectiondef_childs):
                    yield k
                for evented_item in starting_buffer:
                    yield evented_item
                started = True
            else:
                starting_buffer.append((event, item))
    yield ENDEVENT, sectiondef

def make_extended_controls_inline(event_prefixed_mac, stack=None):
    ''' inline extended-controls into paragraph texts '''
    from .binmodel import ControlChar, Control
    if stack is None:
        stack = [] # stack of ancestor Paragraphs
    for event, item in event_prefixed_mac:
        model, attributes, context = item
        if model is Paragraph:
            if event == STARTEVENT:
                stack.append(dict())
                yield STARTEVENT, item
            else:
                yield ENDEVENT, item
                stack.pop()
        elif model is ControlChar:
            if event is STARTEVENT:
                if attributes['kind'] is ControlChar.EXTENDED:
                    control_subtree = stack[-1].get(Control).pop(0)
                    tev = tree_events(*control_subtree)
                    yield tev.next() # to evade the Control/STARTEVENT trigger in parse_models_pass3()
                    for k in make_extended_controls_inline(tev, stack):
                        yield k
                else:
                    yield STARTEVENT, item
                    yield ENDEVENT, item
        elif issubclass(model, Control) and event == STARTEVENT:
            control_subtree = build_subtree(event_prefixed_mac)
            stack[-1].setdefault(Control, []).append( control_subtree )
        else:
            yield event, item

def make_paragraphs_children_of_listheader(event_prefixed_mac, parentmodel=ListHeader, childmodel=Paragraph):
    ''' make paragraphs children of the listheader '''
    stack = []
    level = 0
    for event, item in event_prefixed_mac:
        model, attributes, context = item
        if event is STARTEVENT:
            level += 1
        if len(stack) > 0 and ((event is STARTEVENT and stack[-1][0] == level and model is not childmodel) or
                               (event is ENDEVENT and stack[-1][0]-1 == level)):
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
    from .binmodel import Field, ControlChar
    stack = []
    for event, item in event_prefixed_mac:
        (model, attributes, context) = item
        if issubclass(model, Field):
            if event is STARTEVENT:
                stack.append(item)
                yield event, item
            else:
                pass
        elif model is ControlChar and attributes['name'] == 'FIELD_END':
            if event is ENDEVENT:
                yield event, stack.pop()
        else:
            yield event, item

class TableRow: pass
def restructure_tablebody(event_prefixed_mac):
    from collections import deque
    stack = []
    for event, item in event_prefixed_mac:
        (model, attributes, context) = item
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
                    yield STARTEVENT, (TableRow, dict(), row_context)
            yield event, item
            if event is ENDEVENT:
                how = rowcols.popleft()
                if how & 2:
                    yield ENDEVENT, (TableRow, dict(), row_context)
        else:
            yield event, item


def prefix_binmodels_with_event(context, models):
    from .treeop import prefix_event
    level_prefixed = ((model['record']['level'],
                       (model['type'], model['content'], context))
                      for model in models)
    return prefix_event(level_prefixed)

def wrap_modelevents(wrapper_model, modelevents):
    from .treeop import STARTEVENT, ENDEVENT
    yield STARTEVENT, wrapper_model
    for mev in modelevents:
        yield mev
    yield ENDEVENT, wrapper_model


class ModelEventHandler(object):
    def startModel(self, model, attributes, **kwargs):
        raise NotImplementedError
    def endModel(self, model):
        raise NotImplementedError


def dispatch_model_events(handler, events):
    from .treeop import STARTEVENT, ENDEVENT
    for event, (model, attributes, context) in events:
        if event == STARTEVENT:
            handler.startModel(model, attributes, **context)
        elif event == ENDEVENT:
            handler.endModel(model)

def flatxml(hwpfile, logger, oformat):
    ''' convert hwpfile into a flat xml

    hwpfile - hwp file
    oformat - output formatter
    '''
    from .recordstream import read_records
    from .binmodel import parse_models
    from .binmodel import create_context
    context = create_context(hwpfile)

    class HwpDoc(object): pass
    class DocInfo(object): pass
    class BodyText(object): pass
    hwpdoc = HwpDoc, dict(version=hwpfile.fileheader.version), dict(context)
    docinfo = DocInfo, dict(), dict(context)
    docinfo_records = read_records(hwpfile.docinfo(), 'docinfo')
    docinfo_models = parse_models(context, docinfo_records)
    docinfo_events = prefix_binmodels_with_event(context, docinfo_models)
    docinfo_events = wrap_modelevents(docinfo, docinfo_events)

    docinfo_events = remove_redundant_facenames(docinfo_events)

    bodytext = BodyText, dict(), dict(context)
    bodytext_events = []
    for idx in hwpfile.list_bodytext_sections():
        section_records = read_records(hwpfile.bodytext(idx), 'bodytext/%d'%idx)
        section_models = parse_models(context, section_records)
        section_events = prefix_binmodels_with_event(context, section_models)

        section_events = make_texts_linesegmented_and_charshaped(section_events)
        section_events = make_extended_controls_inline(section_events)
        section_events = match_field_start_end(section_events)
        section_events = make_paragraphs_children_of_listheader(section_events)
        section_events = make_paragraphs_children_of_listheader(section_events, TableBody, TableCell)
        section_events = restructure_tablebody(section_events)

        section_events = wrap_section(idx, section_events)
        bodytext_events.append(section_events)
    bodytext_events = chain(*bodytext_events)
    bodytext_events = wrap_modelevents(bodytext, bodytext_events)

    hwpdoc_events = chain(docinfo_events, bodytext_events)
    hwpdoc_events = wrap_modelevents(hwpdoc, hwpdoc_events)

    # for easy references in styles
    hwpdoc_events = give_elements_unique_id(hwpdoc_events)

    oformat.startDocument()
    dispatch_model_events(oformat, hwpdoc_events)
    oformat.endDocument()


class ModelEventStream(binmodel.ModelStream):

    @property
    def eventgen_context(self):
        return dict(self.model_parsing_context)

    def modelevents(self):
        context = self.eventgen_context
        models = self.models()
        return prefix_binmodels_with_event(context, models)


class DocInfo(ModelEventStream):

    def events(self):
        docinfo = DocInfo, dict(), self.eventgen_context
        events = self.modelevents()
        events = wrap_modelevents(docinfo, events)
        return remove_redundant_facenames(events)


class Hwp5File(binmodel.Hwp5File):

    docinfo_class = DocInfo


def main():
    import sys
    import itertools
    from .filestructure import open

    from ._scriptutils import OptionParser, args_pop, open_or_exit
    op = OptionParser(usage='usage: %prog [options] filename')
    op.add_option('-f', '--format', dest='format', default='xml', help='output format: xml | nul [default: xml]')

    options, args = op.parse_args()

    filename = args_pop(args, 'filename')
    hwpfile = open_or_exit(open, filename)

    out = options.outfile

    class NulFormat(ModelEventHandler):
        def __init__(self, out): pass
        def startDocument(self): pass
        def endDocument(self): pass
        def startModel(self, model, attributes, **context): pass
        def endModel(self, model): pass
    from .xmlformat import XmlFormat

    formats = dict(xml=XmlFormat, nul=NulFormat)
    oformat = formats[options.format](out)

    from ._scriptutils import getlogger, loghandler, logformat_xml
    flatxml(hwpfile, logger, oformat)
    

if __name__ == '__main__':
    main()
