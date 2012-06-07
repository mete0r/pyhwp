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
    hwp5proc rawunz
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
    elif args['rawunz']:
        rawunz(args)


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
