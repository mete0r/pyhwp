# -*- coding: utf-8 -*-
#
#                   GNU AFFERO GENERAL PUBLIC LICENSE
#                      Version 3, 19 November 2007
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010 mete0r@sarangbang.or.kr
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
'''Do various operations on HWPv5 files.

Usage::

    hwp5proc [-h] <command> [option] [<args>...]
    hwp5proc [--version]
    hwp5proc [--help]

    -h --help       Show help messages.
       --version    Show hwp5 package version.
'''


import logging


logger = logging.getLogger(__name__)


def rest_to_docopt(doc):
    ''' ReST to docopt conversion
    '''
    return doc.replace('::\n\n', ':\n').replace('``', '')


def init_logger(args):
    import os
    logger = logging.getLogger('hwp5')

    loglevel = args.get('--loglevel', None)
    if not loglevel:
        loglevel = os.environ.get('PYHWP_LOGLEVEL')
    if loglevel:
        levels = dict(debug=logging.DEBUG,
                      info=logging.INFO,
                      warning=logging.WARNING,
                      error=logging.ERROR,
                      critical=logging.CRITICAL)
        loglevel = loglevel.lower()
        loglevel = levels.get(loglevel, logging.WARNING)
        logger.setLevel(loglevel)

    logfile = args.get('--logfile', None)
    if not logfile:
        logfile = os.environ.get('PYHWP_LOGFILE')
    if logfile:
        logger.addHandler(logging.FileHandler(logfile))
    else:
        logger.addHandler(logging.StreamHandler())


def entrypoint(rest_doc):
    def wrapper(f):
        def main(argv):
            from docopt import docopt
            from hwp5 import __version__
            from hwp5.errors import InvalidHwp5FileError
            from hwp5.dataio import ParseError
            from hwp5.proc import rest_to_docopt
            from hwp5.proc import init_logger

            doc = rest_to_docopt(rest_doc)
            args = docopt(doc, version=__version__, argv=argv)
            init_logger(args)

            try:
                return f(args)
            except InvalidHwp5FileError, e:
                logger.error('%s', e)
                return 1
            except ParseError, e:
                e.print_to_logger(logger)
                return 1
        return main
    return wrapper


subcommands = ['version', 'header', 'summaryinfo', 'ls', 'cat', 'unpack',
               'records', 'models', 'find', 'xml', 'rawunz']

def main():
    from docopt import docopt
    from hwp5 import __version__

    doc = __doc__ + '''
Available commands::

    ''' + '\n    '.join(subcommands) + '''
See 'hwp5proc <command> --help' for more information on a specific command.

'''

    doc = rest_to_docopt(doc)

    args = docopt(doc, version=__version__, help=False)

    command = args['<command>']
    if command not in subcommands:
        print(doc.strip())
        return 1

    import sys
    i = sys.argv.index(command)
    argv = sys.argv[i:]

    mod = __import__('hwp5.proc.'+command, fromlist=['main'])
    return mod.main(argv)
