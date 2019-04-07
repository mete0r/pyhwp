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
import gettext
import logging
import os
import sys

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


PY3 = sys.version_info.major == 3
logger = logging.getLogger(__name__)

locale_dir = os.path.join(os.path.dirname(__file__), '..', 'locale')
locale_dir = os.path.abspath(locale_dir)
t = gettext.translation('hwp5proc', locale_dir, fallback=True)
if PY3:
    _ = t.gettext
else:
    _ = t.ugettext


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
    try:
        from colorlog import ColoredFormatter
    except ImportError:
        formatter = None
    else:
        formatter = ColoredFormatter(
            '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
            datefmt=None, reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red'
            }
        )

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
        handler = logging.FileHandler(logfile)
    else:
        handler = logging.StreamHandler()
    if formatter:
        handler.setFormatter(formatter)
    logger.addHandler(handler)


subcommands = [
    'version',
    'header',
    'summaryinfo',
    'ls',
    'cat',
    'unpack',
    'records',
    'models',
    'find',
    'xml',
    'rawunz',
    'diststream',
]


program = 'hwp5proc (pyhwp) {version}'.format(version=__version__)

copyright = 'Copyright (C) 2010-2015 mete0r <mete0r@sarangbang.or.kr>'

license = _('''License AGPLv3+: GNU Affero GPL version 3 or any later
<http://gnu.org/licenses/agpl.txt>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.''')

disclosure = _('''Disclosure: This program has been developed in accordance with a public
document named "HWP Binary Specification 1.1" published by Hancom Inc.
<http://www.hancom.co.kr>.''')  # noqa

version = '''{program}
{copyright}
{license}
{disclosure}'''.format(
    program=program,
    copyright=copyright,
    license=license,
    disclosure=disclosure,
)


def print_subcommands():
    print(_('Available <command> values:'))
    print('')
    for subcommand in subcommands:
        print('    {}'.format(subcommand))
    print('')
    print(_('See \'hwp5proc <command> --help\' '
            'for more information on a specific command.'))


def main():
    doc = __doc__
    doc = rest_to_docopt(doc)

    args = docopt(doc, version=version, help=False, options_first=True)

    if args['--help-commands']:
        print(doc)
        print_subcommands()
        return 0

    command = args['<command>']
    if command is None:
        print(doc.strip())
        return 1

    if command not in subcommands:
        message = _('Unknown command: {}')
        message = message.format(command)
        message = '\n{}\n\n'.format(message)
        sys.stderr.write(message)
        print_subcommands()
        return 1

    argv = [command] + args['<args>']
    mod = __import__('hwp5.proc.' + command, fromlist=['main'])
    main = mod.main
    doc = rest_to_docopt(mod.__doc__)
    args = docopt(doc, version=__version__, argv=argv)
    init_logger(args)

    try:
        return main(args)
    except InvalidHwp5FileError as e:
        logger.error('%s', e)
        raise SystemExit(1)
    except ParseError as e:
        e.print_to_logger(logger)
        raise SystemExit(1)


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
