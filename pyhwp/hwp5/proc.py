# -*- coding: utf-8 -*-
'''Do various operations on HWPv5 files.

Usage::

    hwp5proc version <hwp5file>
    hwp5proc summaryinfo <hwp5file>
    hwp5proc ls [--vstreams | --ole] <hwp5file>
    hwp5proc cat [--vstreams | --ole] <hwp5file> <stream>
    hwp5proc unpack [--vstreams | --ole] <hwp5file> [<out-directory>]
    hwp5proc records [<hwp5file> <record-stream>]
    hwp5proc models [<hwp5file> <record-stream> | -V <version>]
    hwp5proc xml <hwp5file>
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
    -V              HWPv5 format version [default: 5.0.0.0]


``hwp5proc version``
--------------------
Print HWP file format version of <hwp5file>.


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

    $ hwp5proc unpack samples/sample-5017.hwp
    $ hwp5proc records < sample-5017/DocInfo


``hwp5proc models``
-------------------
Print parsed binary models in the specified <record-stream>.

Example::

    $ hwp5proc models samples/sample-5017.hwp BodyText/Section0

Example::

    $ hwp5proc models samples/sample-5017.hwp BodyText/Section0 > Section0.bin
    $ hwp5proc models < Section0.bin
    $ hwp5proc models -V 5.0.1.7 < Section0.bin


``hwp5proc xml``
----------------
Transform <hwp5file> into an XML.

Example::

    $ hwp5proc xml samples/sample-5017.hwp > sample-5017.xml
    $ xmllint --format sample-5017.xml

'''

import logging


logger = logging.getLogger(__name__)


def main():
    from docopt import docopt
    from pkg_resources import get_distribution

    # ReST to docopt conversion
    doc = __doc__.replace('::\n\n', ':\n').replace('``', '')

    dist = get_distribution('pyhwp')
    args = docopt(doc, version=dist.version)
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
    elif args['rawunz']:
        rawunz(args)


def version(args):
    ''' Print HWP file format version of <hwp5file>.
    '''
    from .xmlmodel import Hwp5File
    hwp5file = Hwp5File(args['<hwp5file>'])
    h = hwp5file.fileheader
    #print h.signature.replace('\x00', ''),
    print '%d.%d.%d.%d' % h.version


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
    from .filestructure import OleStorage
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
    stream.records_json().dump(sys.stdout)


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

        from .storage import Open2Stream
        from .binmodel import ModelStream
        stream = ModelStream(Open2Stream(lambda: sys.stdin), version)
    stream.models_json().dump(sys.stdout)


def xml(args):
    ''' Transform <hwp5file> into an XML.
    '''
    import sys
    from .xmlmodel import Hwp5File

    hwp5file = Hwp5File(args['<hwp5file>'])
    hwp5file.xmlevents().dump(sys.stdout)


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
