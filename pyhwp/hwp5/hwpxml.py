from .filestructure import VERSION
from .dataio import typed_struct_attributes, Struct, ARRAY, N_ARRAY, FlagsType, EnumType
from .dataio import HWPUNIT, HWPUNIT16, SHWPUNIT, hwp2pt, hwp2mm, hwp2inch
from .models import typed_model_attributes, COLORREF
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
        for k, v in t.dictvalue(value).iteritems():
            yield k, xmlattrval(v)
    elif t is COLORREF:
        yield name, xmlattrval( t(value) )
    elif t is VERSION:
        yield name, '.'.join(str(x) for x in value)
    elif t in (HWPUNIT, SHWPUNIT, HWPUNIT16):
        yield name, str(value)
    else:
        yield name, xmlattrval(value)

def xmlattrnames(attrs):
    for k, v in attrs:
        yield k.replace('_', '-'), v

def xmlattr_uniqnames(attrs):
    names = set([])
    for k, v in attrs:
        assert not k in names, 'name clashes: %s'%k
        yield k, v
        names.add(k)

def xmlattributes_for_plainvalues(plainvalues):
    return dict(xmlattr_uniqnames(chain(*(xmlattrnames(expanded_xmlattribute(ntv)) for ntv in plainvalues.iteritems()))))

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
    try:
        import logging
        typed_attributes, plainvalues = separate_plainvalues(context.get('logging', logging), typed_attributes)
        yield xmlgen.startElement, model.__name__, xmlattributes_for_plainvalues(plainvalues)
    except Exception, e:
        raise e
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

def main():
    import sys
    import logging
    import itertools
    from .filestructure import File
    from .models import STARTEVENT, ENDEVENT

    from optparse import OptionParser as OP
    op = OP(usage='usage: %prog [options] filename <record-stream> [<record-range>]\n\n<record-range> : <index> | <start-index>: | :<end-index> | <start-index>:<end-index>')
    op.add_option('', '--loglevel', dest='loglevel', default='warning', help='log level (debug, info, warning, error, critical)')

    options, args = op.parse_args()
    try:
        filename = args.pop(0)
    except IndexError:
        print 'the input filename is required'
        op.print_help()
        return -1

    file = File(filename)

    from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
    loglevels = dict(debug=DEBUG, info=INFO, warning=WARNING, error=ERROR, critical=CRITICAL)
    loglevel = loglevels[options.loglevel]

    logger = logging.getLogger()
    logger.setLevel(loglevels.get(options.loglevel, WARNING))
    loghandler = logging.StreamHandler(sys.stdout)
    loghandler.setFormatter(logging.Formatter('<!-- %(message)s -->'))
    logger.addHandler(loghandler)

    from xml.sax.saxutils import XMLGenerator
    xmlgen = XMLGenerator(sys.stdout, 'utf-8')
    from .models import ModelEventHandler, Text
    class XmlHandler(ModelEventHandler):
        def startDocument(self):
            xmlgen.startDocument()
        def startModel(self, model, attributes, **context):
            recordid = context.get('recordid', ('UNKNOWN', 'UNKNOWN', -1))
            hwptag = context.get('hwptag', '')
            if loglevel <= logging.INFO:
                xmlgen._write('<!-- rec:%d %s -->'%(recordid[2], hwptag))
            if model is Text:
                text = attributes.pop('text')
            else:
                text = None

            for x in startelement(context, xmlgen, (model, attributes)): x[0](*x[1:])

            if model is Text and text is not None:
                xmlgen.characters(text)
            if loglevel <= logging.INFO:
                unparsed = context.get('unparsed', '')
                if len(unparsed) > 0:
                    xmlgen._write('<!-- UNPARSED\n')
                    xmlgen._write(dataio.hexdump(unparsed, True))
                    xmlgen._write('\n-->')
        def endModel(self, model):
            xmlgen.endElement(model.__name__)
        def endDocument(self):
            xmlgen.endDocument()

    oformat = XmlHandler()

    def wrap_modelevents(wrapper_model, modelevents):
        yield STARTEVENT, wrapper_model
        for mev in modelevents:
            yield mev
        yield ENDEVENT, wrapper_model

    from .recordstream import read_records
    from .models import parse_models
    from .models import create_context
    from .models import dispatch_model_events
    context = create_context(file, logging=logger)

    class HwpDoc(object): pass
    class DocInfo(object): pass
    class BodyText(object): pass
    hwpdoc = HwpDoc, dict(filename=filename, version=file.fileheader.version), dict(context)
    docinfo = DocInfo, dict(), dict(context)
    docinfo_records = read_records(file.docinfo(), 'docinfo', filename)
    docinfo_events = wrap_modelevents(docinfo, parse_models(context, docinfo_records))

    bodytext = BodyText, dict(), dict(context)
    bodytext_events = []
    for idx in file.list_bodytext_sections():
        section_records = read_records(file.bodytext(idx), 'bodytext/%d'%idx, filename)
        section_events = parse_models(context, section_records)
        bodytext_events.append(section_events)
    bodytext_events = chain(*bodytext_events)
    bodytext_events = wrap_modelevents(bodytext, bodytext_events)

    hwpdoc_events = chain(docinfo_events, bodytext_events)
    hwpdoc_events = wrap_modelevents(hwpdoc, hwpdoc_events)

    oformat.startDocument()
    dispatch_model_events(oformat, hwpdoc_events)
    oformat.endDocument()

if __name__ == '__main__':
    main()
