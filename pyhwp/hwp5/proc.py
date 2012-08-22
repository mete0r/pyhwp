# -*- coding: utf-8 -*-
'''Do various operations on HWPv5 files.

Usage::

    hwp5proc version <hwp5file>
    hwp5proc header <hwp5file>
    hwp5proc summaryinfo <hwp5file>
    hwp5proc ls [--vstreams | --ole] <hwp5file>
    hwp5proc cat [--vstreams | --ole] <hwp5file> <stream>
    hwp5proc unpack [--vstreams | --ole] <hwp5file> [<out-directory>]
    hwp5proc records [--simple | --json | --raw] [--treegroup=<treegroup> | --range=<range>] [<hwp5file> <record-stream>]
    hwp5proc models [--simple | --json] [--treegroup=<treegroup>] [<hwp5file> <record-stream> | -V <version>]
    hwp5proc find [--model=<model-name> | --tag=<hwptag>] [--incomplete] [--dump] <hwp5files>...
    hwp5proc xml [--embedbin] <hwp5file>
    hwp5proc rawunz
    hwp5proc -h | --help
    hwp5proc --version

Options::

    -h --help       Show this screen
    --version       Show version
    --vstreams      Process with virtual streams (i.e. parsed/converted form
                    of real streams)
    --ole           Treat <hwpfile> as an OLE Compound File. As a result,
                    some streams will be presented as-is. (i.e. not decompressed)
    --simple        print records as simple tree
    --json          print records as json
    --raw           print records as is
    --model=<model-name> filter with record model name
    --tag=<hwptag>  filter with record HWPTAG
    --incomplete    filter with incompletely parsed content
    --dump          dump record
    -V              HWPv5 format version [default: 5.0.0.0]


``hwp5proc version``
--------------------
Print HWP file format version of <hwp5file>.


``hwp5proc header``
------------------------
Print FileHeader of <hwp5file>.


``hwp5proc summaryinfo``
------------------------
Print summary information of <hwp5file>.


``hwp5proc ls``
---------------
List streams in the <hwp5file>.

Example: List without virtual streams::

    $ hwp5proc ls sample/sample-5017.hwp

    \\x05HwpSummaryInformation
    BinData/BIN0002.jpg
    BinData/BIN0002.png
    BinData/BIN0003.png
    BodyText/Section0
    DocInfo
    DocOptions/_LinkDoc
    FileHeader
    PrvImage
    PrvText
    Scripts/DefaultJScript
    Scripts/JScriptVersion

Example: List virtual streams too::

    $ hwp5proc ls --vstreams sample/sample-5017.hwp

    \\x05HwpSummaryInformation
    \\x05HwpSummaryInformation.txt
    BinData/BIN0002.jpg
    BinData/BIN0002.png
    BinData/BIN0003.png
    BodyText/Section0
    BodyText/Section0.models
    BodyText/Section0.records
    BodyText/Section0.xml
    BodyText.xml
    DocInfo
    DocInfo.models
    DocInfo.records
    DocInfo.xml
    DocOptions/_LinkDoc
    FileHeader
    FileHeader.txt
    PrvImage
    PrvText
    PrvText.utf8
    Scripts/DefaultJScript
    Scripts/JScriptVersion


``hwp5proc cat``
----------------

Extract out the specified stream in the <hwp5file> to the standard output.

Example::

    $ hwp5proc cat --vstreams samples/sample-5017.hwp FileHeader.txt

    ccl: 0
    cert_drm: 0
    cert_encrypted: 0
    cert_signature_extra: 0
    cert_signed: 0
    compressed: 1
    distributable: 0
    drm: 0
    history: 0
    password: 0
    script: 0
    signature: HWP Document File
    version: 5.0.1.7
    xmltemplate_storage: 0

    $ hwp5proc cat samples/sample-5017.hwp BinData/BIN0002.jpg > BIN0002.jpg


``hwp5proc unpack``
-------------------
Extract out streams in the specified <hwp5file> to a directory.

Example::

    $ hwp5proc unpack samples/sample-5017.hwp
    $ ls sample-5017

Example::

    $ hwp5proc unpack --vstreams samples/sample-5017.hwp
    $ cat sample-5017/PrvText.utf8


``hwp5proc records``
--------------------
Print records in the specified <record-stream>.

Example::

    $ hwp5proc records samples/sample-5017.hwp DocInfo

Example::

    $ hwp5proc records samples/sample-5017.hwp DocInfo 0-2

Example::

    $ hwp5proc records --raw samples/sample-5017.hwp DocInfo 0-2 > tmp.rec
    $ hwp5proc records < tmp.rec

Example::

    $ hwp5proc unpack samples/sample-5017.hwp
    $ hwp5proc records < sample-5017/DocInfo


``hwp5proc models``
-------------------
Print parsed binary models in the specified <record-stream>.

Example::

    $ hwp5proc models --tree samples/sample-5017.hwp BodyText/Section0

Example::

    $ hwp5proc models samples/sample-5017.hwp BodyText/Section0

Example::

    $ hwp5proc cat samples/sample-5017.hwp BodyText/Section0 > Section0.bin
    $ hwp5proc models < Section0.bin
    $ hwp5proc models -V 5.0.1.7 < Section0.bin


``hwp5proc find``
-----------------
Find models with specified predicates.

Example: Find paragraphs::

    $ hwp5proc find --model=Paragraph samples/*.hwp
    $ hwp5proc find --tag=HWPTAG_PARA_TEXT samples/*.hwp
    $ hwp5proc find --tag=66 samples/*.hwp

Example: Find and dump records of HWPTAG_LIST_HEADER which is parsed
incompletely::

    $ hwp5proc find --tag=HWPTAG_LIST_HEADER --incomplete --dump samples/*.hwp


``hwp5proc xml``
----------------
Transform <hwp5file> into an XML.

Example::

    $ hwp5proc xml samples/sample-5017.hwp > sample-5017.xml
    $ xmllint --format sample-5017.xml

'''

import logging


logger = logging.getLogger(__name__)

def rest_to_docopt(doc):
    ''' ReST to docopt conversion
    '''
    return doc.replace('::\n\n', ':\n').replace('``', '')

def main():
    import sys
    from docopt import docopt
    from hwp5 import __version__
    from hwp5.errors import InvalidHwp5FileError

    doc = rest_to_docopt(__doc__)
    args = docopt(doc, version=__version__)
    logging.getLogger('hwp5').addHandler(logging.StreamHandler())

    from hwp5.dataio import ParseError
    try:
        if args['version']:
            version(args)
        elif args['header']:
            header(args)
        elif args['summaryinfo']:
            summaryinfo(args)
        elif args['records']:
            records(args)
        elif args['models']:
            models(args)
        elif args['find']:
            find(args)
        elif args['xml']:
            xml(args)
        elif args['ls']:
            ls(args)
        elif args['cat']:
            cat(args)
        elif args['unpack']:
            unpack(args)
        elif args['rawunz']:
            rawunz(args)
    except ParseError, e:
        e.print_to_logger(logger)
    except InvalidHwp5FileError, e:
        logger.error('%s', e)
        sys.exit(1)


def version(args):
    ''' Print HWP file format version of <hwp5file>.
    '''
    from .xmlmodel import Hwp5File
    hwp5file = Hwp5File(args['<hwp5file>'])
    h = hwp5file.fileheader
    #print h.signature.replace('\x00', ''),
    print '%d.%d.%d.%d' % h.version


def header(args):
    ''' Pring HWP file header.
    '''
    from hwp5.filestructure import Hwp5File
    hwp5file = Hwp5File(args['<hwp5file>'])
    f = hwp5file.header.open_text()
    try:
        try:
            for line in f:
                print line,
        finally:
            f.close()
    finally:
        hwp5file.close()


def summaryinfo(args):
    ''' Print summary information of <hwp5file>.
    '''
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
    from .storage.ole import OleStorage
    filename = args['<hwp5file>']
    if args['--ole']:
        hwpfile = OleStorage(filename)
    else:
        hwpfile = Hwp5File(filename)
        if args['--vstreams']:
            hwpfile = ExtraItemStorage(hwpfile)
    return hwpfile


def ls(args):
    ''' List streams in the <hwp5file>.
    '''
    from .storage import printstorage
    hwpfile = open_hwpfile(args)
    printstorage(hwpfile)


def cat(args):
    ''' Extract out the specified stream in the <hwp5file> to the standard output.
    '''
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
    ''' Extract out streams in the specified <hwp5file> to a directory.
    '''
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


def parse_recordstream_name(hwpfile, streamname):
    from .storage import open_storage_item
    if streamname == 'docinfo':
        return hwpfile.docinfo
    segments = streamname.split('/')
    if len(segments) == 2:
        if segments[0] == 'bodytext':
            try:
                idx = int(segments[1])
                return hwpfile.bodytext.section(idx)
            except ValueError:
                pass
    return open_storage_item(hwpfile, streamname)


def records(args):
    ''' Print records in the specified <record-stream>.
    '''
    import sys
    filename = args['<hwp5file>']
    if filename:
        from .recordstream import Hwp5File
        hwpfile = Hwp5File(filename)
        streamname = args['<record-stream>']
        stream = parse_recordstream_name(hwpfile, streamname)
    else:
        from .storage import Open2Stream
        from .recordstream import RecordStream
        stream = RecordStream(Open2Stream(lambda: sys.stdin), None)

    opts = dict()
    rng = args['--range']
    if rng:
        rng = rng.split('-', 1)
        rng = tuple(int(x) for x in rng)
        opts['range'] = rng
    treegroup = args['--treegroup']
    if treegroup is not None:
        opts['treegroup'] = int(treegroup)

    if args['--simple']:
        for record in stream.records(**opts):
            print '  '*record['level'], record['tagname']
    elif args['--raw']:
        from hwp5.recordstream import dump_record
        for record in stream.records(**opts):
            dump_record(sys.stdout, record)
    else:
        stream.records_json(**opts).dump(sys.stdout)


def models(args):
    ''' Print parsed binary models in the specified <record-stream>.
    '''
    import sys
    filename = args['<hwp5file>']
    if filename:
        from .binmodel import Hwp5File
        streamname = args['<record-stream>']
        hwpfile = Hwp5File(filename)
        stream = parse_recordstream_name(hwpfile, streamname)
    else:
        version = args['<version>'] or '5.0.0.0'
        version = version.split('.')
        version = tuple(int(x) for x in version)

        from .storage import Open2Stream
        from .binmodel import ModelStream
        stream = ModelStream(Open2Stream(lambda: sys.stdin), version)

    opts = dict()

    treegroup = args['--treegroup']
    if treegroup is not None:
        opts['treegroup'] = int(treegroup)

    if args['--simple']:
        for model in stream.models(**opts):
            print '    '*model['level']+model['type'].__name__
    else:
        stream.models_json(**opts).dump(sys.stdout)


def find(args):
    filenames = args['<hwp5files>']
    from hwp5.dataio import ParseError
    from hwp5.binmodel import Hwp5File

    conditions = []
    if args['--model']:
        def with_model_name(model):
            return args['--model'] == model['type'].__name__
        conditions.append(with_model_name)

    if args['--tag']:
        tag = args['--tag']
        try:
            tag = int(tag)
        except ValueError:
            pass
        else:
            from hwp5.tagids import tagnames
            tag = tagnames[tag]

        def with_tag(model):
            return model['tagname'] == tag
        conditions.append(with_tag)

    if args['--incomplete']:
        def with_incomplete(model):
            return 'unparsed' in model
        conditions.append(with_incomplete)

    def flat_models(hwp5file, **kwargs):
        for model in hwp5file.docinfo.models(**kwargs):
            model['stream'] = 'DocInfo'
            yield model

        for section in hwp5file.bodytext:
            for model in hwp5file.bodytext[section].models(**kwargs):
                model['stream'] = 'BodyText/'+section
                yield model

    for filename in filenames:
        try:
            hwp5file = Hwp5File(filename)

            def with_filename(models):
                for model in models:
                    model['filename'] = filename
                    yield model

            models = flat_models(hwp5file)
            models = with_filename(models)

            for model in models:
                if all(condition(model) for condition in conditions):
                    print '{0}:{1}({2}): {3}'.format(model['filename'],
                                                     model['stream'],
                                                     model['seqno'],
                                                     model['type'].__name__)
                    if args['--dump']:
                        from hwp5.binmodel import model_to_json
                        print model_to_json(model, sort_keys=True, indent=2)
        except ParseError, e:
            logger.error('---- On processing %s:', filename)
            e.print_to_logger(logger)


def xml(args):
    ''' Transform <hwp5file> into an XML.
    '''
    import sys
    from .xmlmodel import Hwp5File

    opts = dict()
    opts['embedbin'] = args['--embedbin']

    hwp5file = Hwp5File(args['<hwp5file>'])
    hwp5file.xmlevents(**opts).dump(sys.stdout)


def rawunz(args):
    ''' Uncompress(raw-zlib) the standard input to the standard output '''
    import sys
    from .zlib_raw_codec import StreamReader
    stream = StreamReader(sys.stdin)
    while True:
        buf = stream.read(64)
        if len(buf) == 0:
            break
        sys.stdout.write(buf)
