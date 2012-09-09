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
''' an xslt/relaxng implementation with external xsltproc / xmllint programs
'''
import logging


logger = logging.getLogger(__name__)


def xslt(xsl_filepath):
    ''' create an XSLT function with specified XSL stylesheet file.

    :param xsl_filepath: a XSL Stylesheet path in filesystem
    :returns: a transform function
    '''

    from hwp5.externprogs import external_transform
    import os
    xsltproc = os.environ.get('PYHWP_XSLTPROC', 'xsltproc')
    exttrans = external_transform(xsltproc, xsl_filepath, '-')
    def transform(*args):
        import os.path
        xsl_name = os.path.basename(xsl_filepath)
        try:
            logger.info('xslt.xsltproc(%s) start', xsl_name)
            return exttrans(*args)
        finally:
            logger.info('xslt.xsltproc(%s) end', xsl_name)
    transform.__doc__ = exttrans.__doc__
    return transform


def relaxng(rng_filepath):
    ''' RelaxNG validator

    :param rng_filepath: RelaxNG schema filepath
    :return: `validate(f)`

    `validate(f)`: validate XML stream against the given RelaxNG schema

    :param f: open file to an XML file
    :return: True if the XML is valid;
             False if `xmllint' program is not found
    :raises RelaxNGValidationFailed: if the XML is not valid

    >>> validate = relaxng(rng_filepath)
    >>> f = file('sample.xml', 'r')
    >>> validate(f)
    '''
    from hwp5.externprogs import external_transform
    from hwp5.externprogs import ProgramNotFound
    from hwp5.tools import RelaxNGValidationFailed

    import os
    xmllint = os.environ.get('PYHWP_XMLLINT', 'xmllint')
    exttransf = external_transform(xmllint, '--noout', '--relaxng',
                                   rng_filepath, '-')
    def transform(*args):
        import os.path
        rng_name = os.path.basename(rng_filepath)
        try:
            logger.info('relaxng.xmllint(%s) start', rng_name)
            return exttransf(*args)
        finally:
            logger.info('relaxng.xmllint(%s) end', rng_name)

    def validate(xml_file):
        from tempfile import TemporaryFile
        tmpf = TemporaryFile()
        try:
            retcode = transform(xml_file, tmpf)
            if retcode != 0:
                raise RelaxNGValidationFailed(tmpf.read())
            return True
        except ProgramNotFound:
            return False
        finally:
            tmpf.close()
    return validate
