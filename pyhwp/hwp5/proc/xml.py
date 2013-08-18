# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2013 mete0r <mete0r@sarangbang.or.kr>
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

Usage::

    hwp5proc xml [--embedbin]
                 [--xml-stylesheet=<xsl-url>]
                 [--xslt-params=<xslt-params>]
                 [--loglevel=<loglevel>] [--logfile=<logfile>]
                 <hwp5file>
    hwp5proc xml --help

Options::

    -h --help               Show this screen
       --loglevel=<level>   Set log level.
       --logfile=<file>     Set log file.

       --embedbin           Embed BinData/* streams in the output XML.

    <hwp5file>              HWPv5 files (*.hwp)
    <xsl-url>               url for <?xml-stylesheet?> Processing Instruction.
    <xslt-params>           <?xslt-param?> processing instructions.
                            Format: <name>:<value>[,<name>:<value>...]

Example::

    $ hwp5proc xml samples/sample-5017.hwp > sample-5017.xml
    $ xmllint --format sample-5017.xml

With ``--embedbin`` option, you can embed base64-encoded ``BinData/*`` files in
the output XML.

Example::

    $ hwp5proc xml --embedbin samples/sample-5017.hwp > sample-5017.xml
    $ xmllint --format sample-5017.xml

'''
from hwp5.proc import entrypoint


@entrypoint(__doc__)
def main(args):
    ''' Transform <hwp5file> into an XML.
    '''
    import sys
    from hwp5.xmlmodel import Hwp5File

    opts = dict()
    opts['embedbin'] = args['--embedbin']

    xml_declaration = True

    if args['--xml-stylesheet'] or args['--xslt-params']:
        xml_stylesheet = args['--xml-stylesheet']
        xslt_params = args['--xslt-params']
        xslt_params = list(parse_xslt_params(xslt_params))

        xml_declaration = False
        sys.stdout.write('<?xml version="1.0" encoding="utf-8"?>\n')

        for name, value in xslt_params:
            sys.stdout.write('<?xslt-param name="%s" select="\'%s\'"?>\n' %
                             (name, value))
        if xml_stylesheet:
            sys.stdout.write('<?xml-stylesheet type="text/xsl" href="%s"?>\n' %
                             xml_stylesheet)

    hwp5file = Hwp5File(args['<hwp5file>'])
    hwp5file.xmlevents(**opts).dump(sys.stdout,
                                    xml_declaration=xml_declaration)


def parse_xslt_params(s):
    if s:
        for token in s.split(','):
            name, value = token.split(':', 1)
            yield name, value
