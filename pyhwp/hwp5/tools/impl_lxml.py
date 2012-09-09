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
''' an xslt/relaxng implementation with lxml
'''
import logging


logger = logging.getLogger(__name__)


def xslt(xsl_filepath):
    ''' create an XSLT function with specified XSL stylesheet file.

    :param xsl_filepath: a XSL Stylesheet path in filesystem
    :returns: a transform function
    '''
    from hwp5.tools import ImplementationNotAvailable
    try:
        import lxml.etree
    except ImportError:
        raise ImplementationNotAvailable('lxml is not available')

    xsl_file = file(xsl_filepath)
    try:
        xsl = lxml.etree.parse(xsl_file)
    finally:
        xsl_file.close()

    xslt = lxml.etree.XSLT(xsl)

    def transform(infile, outfile):
        from os.path import basename
        inp = lxml.etree.parse(infile)
        logger.info('xslt.lxml(%s) start', basename(xsl_filepath))
        out = xslt(inp)
        logger.info('xslt.lxml(%s) end', basename(xsl_filepath))
        outfile.write(str(out))

    transform.lxml_xslt = xslt

    return transform


def relaxng(rng_filepath):
    from hwp5.tools import RelaxNGValidationFailed
    from hwp5.tools import ImplementationNotAvailable
    try:
        import lxml.etree
    except ImportError:
        raise ImplementationNotAvailable('lxml is not available')

    rng_file = file(rng_filepath)
    try:
        rng = lxml.etree.parse(rng_file)
    finally:
        rng_file.close()

    relaxng = lxml.etree.RelaxNG(rng)

    def validate(xml_file):
        from os.path import basename
        inp = lxml.etree.parse(xml_file)
        logger.info('relaxng.lxml(%s) start', basename(rng_filepath))
        valid = relaxng.validate(inp)
        logger.info('relaxng.lxml(%s) end', basename(rng_filepath))
        if valid:
            return True
        else:
            raise RelaxNGValidationFailed()

    validate.lxml_relaxng = relaxng

    return validate
