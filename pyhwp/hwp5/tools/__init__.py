# -*- coding: utf-8 -*-
#
#                    GNU AFFERO GENERAL PUBLIC LICENSE
#                       Version 3, 19 November 2007
#
#    pyhwp : hwp file format parser in python
#    Copyright (C) 2010 mete0r@sarangbang.or.kr
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import logging


logger = logging.getLogger(__name__)


class RelaxNGValidationFailed(Exception):
    pass


class ImplementationNotAvailable(Exception):
    pass


def xslt(xsl_filepath):
    ''' create an XSLT function with specified XSL stylesheet file.

    :param xsl_filepath: a XSL Stylesheet path in filesystem
    :returns: a transform function
    '''
    for impl in xslt.implementations:
        try:
            return impl(xsl_filepath)
        except ImplementationNotAvailable, e:
            logger.info('xslt: %s', e)
    import impl_extern
    logger.info('xslt: using external program as fallback')
    return impl_extern.xslt(xsl_filepath)


xslt.implementations = []


def relaxng(rng_filepath):
    ''' create an RelaxNG validator function with specified RelaxNG file.

    :param rng_filepath: RelaxNG schema filepath
    :return: `validate(f)`

    `validate(f)`: validate XML stream against the given RelaxNG schema

    :param f: open file to an XML file
    :return: True if the XML is valid
    :raises RelaxNGValidationFailed: if the XML is not valid
    '''
    for impl in relaxng.implementations:
        try:
            return impl(rng_filepath)
        except ImplementationNotAvailable, e:
            logger.info('relaxng: %s', e)
    import impl_extern
    logger.info('relaxng: using external program as fallback')
    return impl_extern.relaxng(rng_filepath)


relaxng.implementations = []


from hwp5.tools import impl_lxml
xslt.implementations[0:0] = [impl_lxml.xslt]
relaxng.implementations[0:0] = [impl_lxml.relaxng]
