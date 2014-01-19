# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2014 mete0r <mete0r@sarangbang.or.kr>
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

Example::

    $ hwp5proc xml samples/sample-5017.hwp > sample-5017.xml
    $ xmllint --format sample-5017.xml

With ``--embedbin`` option, you can embed base64-encoded ``BinData/*`` files in
the output XML.

Example::

    $ hwp5proc xml --embedbin samples/sample-5017.hwp > sample-5017.xml
    $ xmllint --format sample-5017.xml

'''
from __future__ import with_statement
from hwp5.proc import entrypoint


@entrypoint(__doc__)
def main(args):
    ''' Transform <hwp5file> into an XML.
    '''
    import sys
    from hwp5.xmlmodel import Hwp5File

    opts = dict()
    opts['embedbin'] = args['--embedbin']

    if args['--output']:
        output = open(args['--output'], 'w')
    else:
        output = sys.stdout

    if args['--no-xml-decl']:
        xml_declaration = False
    else:
        xml_declaration = True

    with output:
        hwp5file = Hwp5File(args['<hwp5file>'])
        hwp5file.xmlevents(**opts).dump(output,
                                        xml_declaration=xml_declaration)
