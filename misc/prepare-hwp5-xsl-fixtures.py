# -*- coding: utf-8 -*-
from __future__ import with_statement
import os.path
import logging


logger = logging.getLogger('hwp5.xsltests')


def find_hwp5files(dir):
    import glob
    return glob.glob(os.path.join(dir, '*.hwp'))


def main():
    doc = ''' convert fixture hwp5 files into *.xml

    Usage:
        prepare [--fixtures-dir=<dir>] [--out-dir=<dir>]
        prepare --help

    Options:
        -h --help               Show this screen
           --fixtures-dir=<dir> Fixture directory
           --out-dir=<dir>      Output directory
    '''
    from docopt import docopt
    from hwp5.xmlmodel import Hwp5File

    args = docopt(doc, version='0.0')

    logging.getLogger().addHandler(logging.StreamHandler())
    logging.getLogger('hwp5.xsltests').setLevel(logging.INFO)

    if args['--fixtures-dir']:
        fixture_dir = args['--fixtures-dir']
    else:
        import hwp5
        hwp5_pkgdir = os.path.dirname(hwp5.__file__)
        fixture_dir = os.path.join(hwp5_pkgdir, 'tests', 'fixtures')

    out_dir = args['--out-dir']

    for path in find_hwp5files(fixture_dir):
        name = os.path.basename(path)
        rootname = os.path.splitext(name)[0]
        out_path = rootname + '.xml'
        if out_dir is not None:
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            out_path = os.path.join(out_dir, out_path)

        logger.info('%s', out_path)

        opts = {}
        try:
            hwp5file = Hwp5File(path)
            with file(out_path, 'w') as f:
                hwp5file.xmlevents(**opts).dump(f)
        except Exception, e:
            logger.exception(e)


if __name__ == '__main__':
    import sys
    sys.exit(main())
