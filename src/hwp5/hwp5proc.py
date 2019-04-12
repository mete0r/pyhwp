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
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from argparse import ArgumentParser
import gettext
import logging
import os
import sys

from . import __version__
from .cli import init_logger
from .dataio import ParseError
from .errors import InvalidHwp5FileError


PY3 = sys.version_info.major == 3
logger = logging.getLogger(__name__)

locale_dir = os.path.join(os.path.dirname(__file__), 'locale')
locale_dir = os.path.abspath(locale_dir)
t = gettext.translation('hwp5proc', locale_dir, fallback=True)
if PY3:
    _ = t.gettext
else:
    _ = t.ugettext


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


def main():
    argparser = main_argparser()
    args = argparser.parse_args()
    init_logger(args)

    try:
        subcommand_fn = args.func
    except AttributeError:
        argparser.print_help()
        raise SystemExit(1)

    try:
        return subcommand_fn(args)
    except InvalidHwp5FileError as e:
        logger.error('%s', e)
        raise SystemExit(1)
    except ParseError as e:
        e.print_to_logger(logger)
        raise SystemExit(1)


def main_argparser():
    from .proc.version import version_argparser
    from .proc.header import header_argparser
    from .proc.summaryinfo import summaryinfo_argparser
    from .proc.ls import ls_argparser
    from .proc.cat import cat_argparser
    from .proc.unpack import unpack_argparser
    from .proc.records import records_argparser
    from .proc.models import models_argparser
    from .proc.find import find_argparser
    from .proc.xml import xml_argparser
    from .proc.rawunz import rawunz_argparser
    from .proc.diststream import diststream_argparser
    parser = ArgumentParser(
        prog='hwp5proc',
        description=_('Do various operations on HWPv5 files.'),
    )
    parser.add_argument(
        '--loglevel',
        help=_('Set log level.'),
    )
    parser.add_argument(
        '--logfile',
        help=_('Set log file.'),
    )
    subcommands = parser.add_subparsers(
        title=_('subcommands'),
        description=_('valid subcommands'),
    )
    version_argparser(subcommands, _)
    header_argparser(subcommands, _)
    summaryinfo_argparser(subcommands, _)
    ls_argparser(subcommands, _)
    cat_argparser(subcommands, _)
    unpack_argparser(subcommands, _)
    records_argparser(subcommands, _)
    models_argparser(subcommands, _)
    find_argparser(subcommands, _)
    xml_argparser(subcommands, _)
    rawunz_argparser(subcommands, _)
    diststream_argparser(subcommands, _)
    return parser
