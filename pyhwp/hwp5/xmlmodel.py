from .filestructure import VERSION
from .dataio import typed_struct_attributes, Struct, ARRAY, N_ARRAY, FlagsType, EnumType, WCHAR
from .dataio import HWPUNIT, HWPUNIT16, SHWPUNIT, hwp2pt, hwp2mm, hwp2inch
from .binmodel import typed_model_attributes, COLORREF, BinStorageId
from .binmodel import STARTEVENT, ENDEVENT
from .binmodel import FaceName, CharShape, SectionDef, ListHeader, Paragraph
from .binmodel import TableControl, GShapeObjectControl, ShapeComponent
from .binmodel import TableBody, TableCell
from .binmodel import Spaces
from itertools import chain

def xmlattrval(value):
    if isinstance(value, basestring):
        return value
    elif isinstance(type(value), EnumType):
        return type(value).name_for(value).lower()
    elif isinstance(value, type):
        return value.__name__
    else:
        return str(value)

def expanded_xmlattribute((name, (t, value))):
    if isinstance(t, FlagsType):
        yield name, hex(int(value))
        for k, v in t.dictvalue(t(value)).iteritems():
            yield k, xmlattrval(v)
    elif t is Spaces:
        for pos in ('left', 'right', 'top', 'bottom'):
            yield '-'.join([name, pos]), xmlattrval(value.get(pos))
    elif t is COLORREF:
        yield name, xmlattrval( t(value) )
    elif t is VERSION:
        yield name, '.'.join(str(x) for x in value)
    elif t in (HWPUNIT, SHWPUNIT, HWPUNIT16):
        yield name, str(value)
    elif t is WCHAR:
        if value == 0:
            yield name, u''
        else:
            yield name, unichr(value)
    elif t is BinStorageId:
        yield name, 'BIN%04X'%value
    else:
        yield name, xmlattrval(value)

def xmlattr_dashednames(attrs):
    for k, v in attrs:
        yield k.replace('_', '-'), v

def xmlattr_uniqnames(attrs):
    names = set([])
    for k, v in attrs:
        assert not k in names, 'name clashes: %s'%k
        yield k, v
        names.add(k)

def xmlattributes_for_plainvalues(context, plainvalues):
    ntvs = plainvalues.iteritems()
    ntvs = chain(*(expanded_xmlattribute(ntv) for ntv in ntvs))
    return dict(xmlattr_uniqnames(xmlattr_dashednames(ntvs)))

def separate_plainvalues(logging, typed_attributes):
    d = []
    p = dict()
    for named_item in typed_attributes:
        name, item = named_item
        t, value = item
        try:
            if t is Spaces:
                p[name] = item
            elif isinstance(value, dict):
                if not issubclass(t, Struct):
                    logging.warning('%s is not a Struct', name)
                d.append( named_item )
            elif isinstance(t, (ARRAY, N_ARRAY)) and issubclass(t.itemtype, Struct):
                d.append( named_item )
            else:
                p[name] = item
        except Exception, e:
            logging.error('%s', (name, t, value))
            logging.error('%s', t.__dict__)
            logging.exception(e)
            raise e
    return d, p

def startelement(context, xmlgen, (model, attributes)):
    if issubclass(model, Struct):
        typed_attributes = typed_struct_attributes(model, attributes, context)
    elif model is dict:
        typed_attributes = ((k, (type(v), v)) for k, v in attributes.iteritems())
    else:
        typed_attributes = typed_model_attributes(model, attributes, context)

    import logging
    typed_attributes, plainvalues = separate_plainvalues(context['logging'], typed_attributes)
    yield xmlgen.startElement, model.__name__, xmlattributes_for_plainvalues(context, plainvalues)
    for _name, (_type, _value) in typed_attributes:
        if isinstance(_value, dict):
            assert isinstance(_value, dict)
            _value = dict(_value)
            _value['attribute-name'] = _name
            for x in element(context, xmlgen, (_type, _value)): yield x
        else:
            assert isinstance(_value, (tuple, list)) and issubclass(_type.itemtype, Struct), (_value, _type)
            yield xmlgen.startElement, 'Array', {'name':_name}
            for _itemvalue in _value:
                for x in element(context, xmlgen, (_type.itemtype, _itemvalue)): yield x
            yield xmlgen.endElement, 'Array'

def element(context, xmlgen, (model, attributes)):
    for x in startelement(context, xmlgen, (model, attributes)): yield x
    yield xmlgen.endElement, model.__name__

from xml.sax.saxutils import XMLGenerator
from .binmodel import ModelEventHandler, Text
from .dataio import hexdump
class XmlFormat(ModelEventHandler):
    def __init__(self, out):
        self.xmlgen = XMLGenerator(out, 'utf-8')
    def startDocument(self):
        self.xmlgen.startDocument()
    def startModel(self, model, attributes, **context):
        context['logging'].debug('xmlmodel.XmlFormat: model: %s, %s', model.__name__, attributes)
        context['logging'].debug('xmlmodel.XmlFormat: context: %s', context)
        recordid = context.get('recordid', ('UNKNOWN', 'UNKNOWN', -1))
        hwptag = context.get('hwptag', '')
        context['logging'].info('xmlmodel.XmlFormat: rec:%d %s', recordid[2], hwptag)
        if model is Text:
            text = attributes.pop('text')
        else:
            text = None

        for x in startelement(context, self.xmlgen, (model, attributes)): x[0](*x[1:])

        if model is Text and text is not None:
            self.xmlgen.characters(text)

        unparsed = context.get('unparsed', '')
        if len(unparsed) > 0:
            context['logging'].debug('UNPARSED: %s', hexdump(unparsed, True))
    def endModel(self, model):
        self.xmlgen.endElement(model.__name__)
    def endDocument(self):
        self.xmlgen.endDocument()

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
                        elif isinstance(chunk, ControlChar):
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
                for k in tree_events_childs(sectiondef_childs):
                    yield k
                for evented_item in starting_buffer:
                    yield evented_item
                started = True
            else:
                starting_buffer.append((event, item))
    yield ENDEVENT, sectiondef

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


def flatxml(hwpfile, logger, oformat):
    ''' convert hwpfile into a flat xml

    hwpfile - hwp file
    oformat - output formatter
    '''
    from .recordstream import read_records
    from .binmodel import parse_models, wrap_modelevents
    from .binmodel import create_context
    from .binmodel import dispatch_model_events
    context = create_context(hwpfile, logging=logger)

    class HwpDoc(object): pass
    class DocInfo(object): pass
    class BodyText(object): pass
    hwpdoc = HwpDoc, dict(version=hwpfile.fileheader.version), dict(context)
    docinfo = DocInfo, dict(), dict(context)
    docinfo_records = read_records(hwpfile.docinfo(), 'docinfo')
    docinfo_events = wrap_modelevents(docinfo, parse_models(context, docinfo_records))

    docinfo_events = remove_redundant_facenames(docinfo_events)

    bodytext = BodyText, dict(), dict(context)
    bodytext_events = []
    for idx in hwpfile.list_bodytext_sections():
        section_records = read_records(hwpfile.bodytext(idx), 'bodytext/%d'%idx)
        section_events = parse_models(context, section_records)

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


def main():
    import sys
    import logging
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

    formats = dict(xml=XmlFormat, nul=NulFormat)
    oformat = formats[options.format](out)

    from ._scriptutils import getlogger, loghandler, logformat_xml
    if options.format == 'xml':
        logger = getlogger(options, loghandler(out, logformat_xml))
    else:
        logger = getlogger(options)
    flatxml(hwpfile, logger, oformat)
    

if __name__ == '__main__':
    main()
