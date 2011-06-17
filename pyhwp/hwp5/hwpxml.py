from .filestructure import VERSION
from .dataio import typed_struct_attributes, Struct, ARRAY, N_ARRAY, FlagsType, EnumType, WCHAR
from .dataio import HWPUNIT, HWPUNIT16, SHWPUNIT, hwp2pt, hwp2mm, hwp2inch
from .models import typed_model_attributes, COLORREF, BinStorageId
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
        yield name, 'BIN%04d'%value
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
    for name, (t, value) in typed_attributes:
        try:
            if isinstance(value, dict):
                if not issubclass(t, Struct):
                    logging.warning('%s is not a Struct', name)
                d.append( (name, (t, value)) )
            elif isinstance(t, (ARRAY, N_ARRAY)) and issubclass(t.itemtype, Struct):
                d.append( (name, (t, value)) )
            else:
                p[name] = (t, value)
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
            _value['attribute-name'] = _name
            for x in element(context, xmlgen, (_type, _value)): yield x
        else:
            assert isinstance(_value, (tuple, list)) and issubclass(_type.itemtype, Struct), (_value, _type)
            yield xmlgen.startElement, 'ListAttribute', {'attribute-name':_name}
            for _itemvalue in _value:
                for x in element(context, xmlgen, (_type.itemtype, _itemvalue)): yield x
            yield xmlgen.endElement, 'ListAttribute'

def element(context, xmlgen, (model, attributes)):
    for x in startelement(context, xmlgen, (model, attributes)): yield x
    yield xmlgen.endElement, model.__name__

from xml.sax.saxutils import XMLGenerator
from .models import ModelEventHandler, Text
from .dataio import hexdump
class XmlFormat(ModelEventHandler):
    def __init__(self, out):
        self.xmlgen = XMLGenerator(out, 'utf-8')
    def startDocument(self):
        self.xmlgen.startDocument()
    def startModel(self, model, attributes, **context):
        context['logging'].debug('hwpxml.XmlFormat: model: %s, %s', model.__name__, attributes)
        context['logging'].debug('hwpxml.XmlFormat: context: %s', context)
        recordid = context.get('recordid', ('UNKNOWN', 'UNKNOWN', -1))
        hwptag = context.get('hwptag', '')
        context['logging'].info('hwpxml.XmlFormat: rec:%d %s', recordid[2], hwptag)
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


def flatxml(hwpfile, logger, oformat):
    ''' convert hwpfile into a flat xml

    hwpfile - hwp file
    oformat - output formatter
    '''
    from .recordstream import read_records
    from .models import parse_models, wrap_modelevents
    from .models import create_context
    from .models import dispatch_model_events
    context = create_context(hwpfile, logging=logger)

    class HwpDoc(object): pass
    class DocInfo(object): pass
    class BodyText(object): pass
    hwpdoc = HwpDoc, dict(version=hwpfile.fileheader.version), dict(context)
    docinfo = DocInfo, dict(), dict(context)
    docinfo_records = read_records(hwpfile.docinfo(), 'docinfo')
    docinfo_events = wrap_modelevents(docinfo, parse_models(context, docinfo_records))

    bodytext = BodyText, dict(), dict(context)
    bodytext_events = []
    for idx in hwpfile.list_bodytext_sections():
        section_records = read_records(hwpfile.bodytext(idx), 'bodytext/%d'%idx)
        section_events = parse_models(context, section_records)
        bodytext_events.append(section_events)
    bodytext_events = chain(*bodytext_events)
    bodytext_events = wrap_modelevents(bodytext, bodytext_events)

    hwpdoc_events = chain(docinfo_events, bodytext_events)
    hwpdoc_events = wrap_modelevents(hwpdoc, hwpdoc_events)

    oformat.startDocument()
    dispatch_model_events(oformat, hwpdoc_events)
    oformat.endDocument()


def main():
    import sys
    import logging
    import itertools
    from .filestructure import File

    from ._scriptutils import OptionParser, args_pop
    op = OptionParser(usage='usage: %prog [options] filename')
    op.add_option('-f', '--format', dest='format', default='xml', help='output format: xml | nul [default: xml]')

    options, args = op.parse_args()

    filename = args_pop(args, 'filename')
    hwpfile = File(filename)

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
