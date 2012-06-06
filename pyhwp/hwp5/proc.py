# -*- coding: utf-8 -*-
'''HWP format version 5 processor.

Usage:
    hwp5proc ls [--with-extra] <hwp5file>
    hwp5proc cat [--with-extra] <hwp5file> <stream>
    hwp5proc unpack [--with-extra] <hwp5file> [<out-directory>]
    hwp5proc version <hwp5file>
    hwp5proc -h | --help
    hwp5proc --version

Options:
    -h --help       Show this screen
    --version       Show version
    --with-extra    process with extra parsed items
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


def ls(args):
    from .xmlmodel import Hwp5File
    from .storage import ExtraItemStorage
    from .storage import printstorage
    hwpfile = Hwp5File(args['<hwp5file>'])
    if args['--with-extra']:
        hwpfile = ExtraItemStorage(hwpfile)
    printstorage(hwpfile)


def cat(args):
    from .xmlmodel import Hwp5File
    from .storage import ExtraItemStorage
    from .storage import open_storage_item
    import sys
    hwp5file = Hwp5File(args['<hwp5file>'])
    if args['--with-extra']:
        hwp5file = ExtraItemStorage(hwp5file)
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
    from .xmlmodel import Hwp5File
    from .storage import ExtraItemStorage
    from . import filestructure
    import os, os.path

    filename = args['<hwp5file>']
    hwp5file = Hwp5File(filename)
    if args['--with-extra']:
        hwp5file = ExtraItemStorage(hwp5file)

    outdir = args['<out-directory>']
    if outdir is None:
        outdir, ext = os.path.splitext(os.path.basename(filename))
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    filestructure.unpack(hwp5file, outdir)
