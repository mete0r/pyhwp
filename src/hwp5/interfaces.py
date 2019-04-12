# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2019 mete0r <mete0r@sarangbang.or.kr>
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

from zope.interface import Interface


class IXSLT(Interface):

    def transform(input, output):
        '''
        Transform input file to output file.

        :param str input:
            input filename.
        :param str output:
            output filename.

        >>> T.transform('input.xml', 'output.xml')
        '''

    def transform_into_stream(input, output_stream):
        '''
        Transform input file to output stream.

        :param str input:
            input filename.
        :param output_stream:
            output stream.
        :type output_stream:
            byte-oriented file-like object.

        >>> T.transform_into_stream('input.xml', sys.stdout.buffer)
        '''


class IXSLTFactory(Interface):

    def xslt_from_file(xsl_path):
        '''
        Create an XSL Transformer from a file.

        :param str xsl_path:
            .xsl file path
        :return:
            an instance of XSL Transformer
        :rtype:
            IXSLT

        >>> T = F.xslt_from_file('transform.xsl')
        '''
