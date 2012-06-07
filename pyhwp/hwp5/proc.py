# -*- coding: utf-8 -*-
'''HWP format version 5 processor.

Usage:
    hwp5proc ls [--with-extra | --ole] <hwp5file>
    hwp5proc cat [--with-extra | --ole] <hwp5file> <stream>
    hwp5proc unpack [--with-extra | --ole] <hwp5file> [<out-directory>]
    hwp5proc version <hwp5file>
    hwp5proc summaryinfo <hwp5file>
    hwp5proc records [<hwp5file> <record-stream>]
    hwp5proc models [<hwp5file> <record-stream> | -V <version>]
    hwp5proc xml <hwp5file>
    hwp5proc -h | --help
    hwp5proc --version

Options:
    -h --help       Show this screen
    --version       Show version
    --with-extra    process with extra parsed items
    --ole           treat <hwpfile> as an OLE Compound File
    -V              HWPv5 version [default: 5.0.0.0]
'''

import logging


logger = logging.getLogger(__name__)


def main():
    from docopt import docopt
    from pkg_resources import get_distribution
    dist = get_distribution('pyhwp')
    args = docopt(__doc__, version=dist.version)
    if args['version']:
        version(args)
    elif args['summaryinfo']:
        summaryinfo(args)
    elif args['records']:
        records(args)
    elif args['models']:
        models(args)
    elif args['xml']:
        xml(args)
    elif args['ls']:
        ls(args)
    elif args['cat']:
        cat(args)
    elif args['unpack']:
        unpack(args)


def version(args):
    from .xmlmodel import Hwp5File
    hwp5file = Hwp5File(args['<hwp5file>'])
    h = hwp5file.fileheader
    #print h.signature.replace('\x00', ''),
    print '%d.%d.%d.%d' % h.version


def summaryinfo(args):
    from .xmlmodel import Hwp5File
    hwpfile = Hwp5File(args['<hwp5file>'])
    try:
        f = hwpfile.summaryinfo.open_text()
        try:
            for line in f:
                print line,
        finally:
            f.close()
    finally:
        hwpfile.close()


def open_hwpfile(args):
    from .xmlmodel import Hwp5File
    from .storage import ExtraItemStorage
    from .filestructure import OleStorage
    filename = args['<hwp5file>']
    if args['--ole']:
        hwpfile = OleStorage(filename)
    else:
        hwpfile = Hwp5File(filename)
        if args['--with-extra']:
            hwpfile = ExtraItemStorage(hwpfile)
    return hwpfile


def ls(args):
    from .storage import printstorage
    hwpfile = open_hwpfile(args)
    printstorage(hwpfile)


def cat(args):
    from .storage import open_storage_item
    import sys
    hwp5file = open_hwpfile(args)
    stream = open_storage_item(hwp5file, args['<stream>'])
    f = stream.open()
    try:
        while True:
            data = f.read(4096)
            if data:
                sys.stdout.write(data)
            else:
                return
    finally:
        if hasattr(f, 'close'):
            f.close()


def unpack(args):
    from . import storage
    import os, os.path

    filename = args['<hwp5file>']
    hwp5file = open_hwpfile(args)

    outdir = args['<out-directory>']
    if outdir is None:
        outdir, ext = os.path.splitext(os.path.basename(filename))
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    storage.unpack(hwp5file, outdir)


def records(args):
    filename = args['<hwp5file>']
    if filename:
        from .recordstream import Hwp5File
        from .recordstream import parse_recordstream_name
        hwpfile = Hwp5File(filename)
        streamname = args['<record-stream>']
        stream = parse_recordstream_name(hwpfile, streamname)
        records = stream.records()
    else:
        from .recordstream import read_records
        import sys
        filename = 'STDIN'
        streamname = 'STDIN'
        bytestream = sys.stdin
        records = read_records(bytestream, streamname, filename)

    # TODO: range
    #from itertools import islice as ranged_records
    #record_range = args_pop_range(args)
    #if record_range:
    #    records = ranged_records(records, *record_range)

    def initlevel(records):
        level = None
        for rec in records:
            if level is None:
                level = rec['level']
            rec['level'] -= level
            #logger.info('### record level : %d', rec.level)
            yield rec
    records = initlevel(records)

    from .recordstream import link_records
    records = link_records(records)

    def count_tagids(records):
        occurrences = dict()
        for rec in records:
            tagname = rec['tagname']
            occurrences.setdefault(tagname, 0)
            occurrences[tagname] += 1
            yield rec
        for tag, count in occurrences.iteritems():
            logger.info('%30s: %d', tag, count)
    records = count_tagids(records)

    class RecordFormatter(object):
        def __init__(self, out):
            self.out = out

        def write(self, rec):
            raise NotImplementedError

    from .recordstream import encode_record_header
    class RawFormat(RecordFormatter):
        def write(self, rec):
            bytes = encode_record_header(rec) + rec['payload']
            self.out.write(bytes)

    from . import dataio
    class HexFormat(RecordFormatter):
        def __init__(self, out):
            out = dataio.IndentedOutput(out, 0)
            super(HexFormat, self).__init__(out)
            self.p = dataio.Printer(out)

        def write(self, rec):
            self.out.level = rec['level']
            self.p.prints((rec['seqno'], rec['tagid'], rec['tagname'],
                           rec['size']))
            self.p.prints(dataio.hexdump(rec['payload'], True))
            self.out.write('-' * 80 + '\n')

    class NulFormat(RecordFormatter):
        def write(self, rec):
            pass

    formats = dict(hex=HexFormat, raw=RawFormat, nul=NulFormat)
    # TODO
    fmt = 'hex'
    import sys
    oformat = formats[fmt](sys.stdout)

    for rec in records:
        oformat.write(rec)


def models(args):
    import sys
    filename = args['<hwp5file>']
    if filename:
        from .binmodel import Hwp5File
        from .recordstream import parse_recordstream_name
        streamname = args['<record-stream>']
        hwpfile = Hwp5File(filename)
        stream = parse_recordstream_name(hwpfile, streamname)
        models = stream.models()
    else:
        filename = 'STDIN'
        streamname = 'STDIN'
        bytestream = sys.stdin
        version = args['<version>'] or '5.0.0.0'
        version = version.split('.')

        from .recordstream import read_records
        from .binmodel import create_context
        from .binmodel import parse_models
        context = create_context(version=version)
        records = read_records(bytestream, streamname, filename)
        models = parse_models(context, records)


    def statistics(models):
        occurrences = dict()
        for model in models:
            model_type = model['type']
            occurrences.setdefault(model_type, 0)
            occurrences[model_type] += 1
            yield model
        for model_type, count in occurrences.iteritems():
            logger.info('%30s: %d', model_type.__name__, count)
    models = statistics(models)

    from .binmodel import generate_models_json_array
    for s in generate_models_json_array(models, indent=2, sort_keys=True):
        sys.stdout.write(s)


def xml(args):
    import sys
    from .xmlmodel import Hwp5File
    from .xmlmodel import ModelEventHandler

    hwp5file = Hwp5File(args['<hwp5file>'])

    class NulFormat(ModelEventHandler):
        def __init__(self, out): pass
        def startDocument(self): pass
        def endDocument(self): pass
        def startModel(self, model, attributes, **context): pass
        def endModel(self, model): pass
    from .xmlformat import XmlFormat

    formats = dict(xml=XmlFormat, nul=NulFormat)
    # TODO
    fmt = 'xml'
    oformat = formats[fmt](sys.stdout)
    hwp5file.flatxml(oformat)
