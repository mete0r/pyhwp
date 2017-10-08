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
''' Transform an HWPv5 file into an XML.

.. note::

   This command is experimental. Its output format is subject to change at any
   time.

Usage::

    hwp5proc xml [--embedbin]
                 [--no-xml-decl]
                 [--output=<file>]
                 [--format=<format>]
                 [--no-validate-wellformed]
                 [--loglevel=<loglevel>] [--logfile=<logfile>]
                 <hwp5file>
    hwp5proc xml --help

Options::

    -h --help               Show this screen
       --loglevel=<level>   Set log level.
       --logfile=<file>     Set log file.

       --embedbin           Embed BinData/* streams in the output XML.
       --no-xml-decl        Don't output <?xml ... ?> XML declaration.
       --output=<file>      Output filename.

    <hwp5file>              HWPv5 files (*.hwp)
    <format>                "flat", "nested" (default: "nested")

Example::

    $ hwp5proc xml samples/sample-5017.hwp > sample-5017.xml
    $ xmllint --format sample-5017.xml

With ``--embedbin`` option, you can embed base64-encoded ``BinData/*`` files in
the output XML.

Example::

    $ hwp5proc xml --embedbin samples/sample-5017.hwp > sample-5017.xml
    $ xmllint --format sample-5017.xml

'''
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from functools import partial
import logging

from ..utils import make_open_dest_file
from ..utils import wrap_open_dest_for_tty
from ..utils import wrap_open_dest
from ..utils import pager
from ..utils import syntaxhighlight
from ..utils import xmllint
from ..xmldump_flat import xmldump_flat
from ..xmlmodel import Hwp5File


logger = logging.getLogger(__name__)


def xmldump_nested(hwp5file, output, embedbin=False, xml_declaration=True):
    dump = hwp5file.xmlevents(embedbin=embedbin).dump
    dump = partial(dump, xml_declaration=xml_declaration)
    dump(output)


def main(args):
    ''' Transform <hwp5file> into an XML.
    '''

    fmt = args['--format'] or 'nested'
    if fmt == 'flat':
        xmldump = partial(
            xmldump_flat,
            xml_declaration=not args['--no-xml-decl']
        )
    elif fmt == 'nested':
        xmldump = partial(
            xmldump_nested,
            xml_declaration=not args['--no-xml-decl'],
            embedbin=args['--embedbin'],
        )

    open_dest = make_open_dest_file(args['--output'])
    open_dest = wrap_open_dest_for_tty(open_dest, [
        pager(),
        syntaxhighlight('application/xml'),
    ] + ([
        xmllint(format=True),
    ] if not args['--no-validate-wellformed'] else []))
    open_dest = wrap_open_dest(open_dest, [
        xmllint(encode='utf-8'),
        xmllint(c14n=True),
    ] if not args['--no-validate-wellformed'] else [])

    hwp5file = Hwp5File(args['<hwp5file>'])
    with open_dest() as output:
        xmldump(hwp5file, output)
