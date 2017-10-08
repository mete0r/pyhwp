# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2015 mete0r <mete0r@sarangbang.or.kr>
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

    hwp5proc <command> [<args>...]
    hwp5proc [--version]
    hwp5proc [--help]
    hwp5proc [--help-commands]

       --version        Show version and copyright information.
    -h --help           Show help messages.
       --help-commands  Show available commands.

'''
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import logging
import os

from docopt import docopt

from .. import __version__
from ..dataio import ParseError
from ..errors import InvalidHwp5FileError
from ..plat import xsltproc
from ..plat import xmllint
from ..storage import ExtraItemStorage
from ..storage import open_storage_item
from ..storage.ole import OleStorage
from ..xmlmodel import Hwp5File


logger = logging.getLogger(__name__)


def rest_to_docopt(doc):
    ''' ReST to docopt conversion
    '''
    return doc.replace('::\n\n', ':\n').replace('``', '')


def init_with_environ():
    if 'PYHWP_XSLTPROC' in os.environ:
        xsltproc.executable = os.environ['PYHWP_XSLTPROC']
        xsltproc.enable()

    if 'PYHWP_XMLLINT' in os.environ:
        xmllint.executable = os.environ['PYHWP_XMLLINT']
        xmllint.enable()


def init_logger(args):
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
               'records', 'models', 'find', 'xml', 'rawunz',
               'diststream']


version = '''hwp5proc (pyhwp) %s
Copyright (C) 2010-2015 mete0r <mete0r@sarangbang.or.kr>
License AGPLv3+: GNU Affero GPL version 3 or any later
<http://gnu.org/licenses/agpl.txt>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Disclosure: This program has been developed in accordance with a public
document named "HWP Binary Specification 1.1" published by Hancom Inc.
<http://www.hancom.co.kr>.'''
version = version % __version__

help_commands = '''Available <command> values:

    ''' + '\n    '.join(subcommands) + '''

See 'hwp5proc <command> --help' for more information on a specific command.'''


def main():
    doc = __doc__
    doc = rest_to_docopt(doc)

    args = docopt(doc, version=version, help=False, options_first=True)

    if args['--help-commands']:
        print(doc + help_commands)
        return 0

    command = args['<command>']
    if command not in subcommands:
        print(doc.strip())
        return 1

    argv = [command] + args['<args>']
    mod = __import__('hwp5.proc.' + command, fromlist=['main'])
    return mod.main(argv)


def open_hwpfile(args):
    filename = args['<hwp5file>']
    if args['--ole']:
        hwpfile = OleStorage(filename)
    else:
        hwpfile = Hwp5File(filename)
        if args['--vstreams']:
            hwpfile = ExtraItemStorage(hwpfile)
    return hwpfile


def parse_recordstream_name(hwpfile, streamname):
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
