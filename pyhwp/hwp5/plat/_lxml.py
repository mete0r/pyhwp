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
from __future__ import with_statement
import logging


logger = logging.getLogger(__name__)


try:
    from lxml import etree
    etree
except ImportError:
    is_enabled = lambda: False
else:
    is_enabled = lambda: True


def xslt(xsl_path, inp_path, out_path):
    ''' Transform XML with XSL

    :param xsl_path: stylesheet path
    :param inp_path: input path
    :param out_path: output path
    '''
    transform = xslt_compile(xsl_path)
    return transform(inp_path, out_path)


def xslt_compile(xsl_path):
    ''' Compile XSL Transform function.
    :param xsl_path: stylesheet path
    :returns: a transform function
    '''
    from lxml import etree

    with file(xsl_path) as xsl_file:
        xsl_doc = etree.parse(xsl_file)

    xslt = etree.XSLT(xsl_doc)

    def transform(inp_path, out_path):
        ''' Transform XML with %r.

        :param inp_path: input path
        :param out_path: output path
        ''' % xsl_path
        with file(inp_path) as inp_file:
            with file(out_path, 'w') as out_file:
                from os.path import basename
                inp = etree.parse(inp_file)
                logger.info('_lxml.xslt(%s) start', basename(xsl_path))
                out = xslt(inp)
                logger.info('_lxml.xslt(%s) end', basename(xsl_path))
                out_file.write(str(out))
                return dict()
    return transform


def relaxng(rng_path, inp_path):
    validate = relaxng_compile(rng_path)
    return validate(inp_path)


def relaxng_compile(rng_path):
    ''' Compile RelaxNG file

    :param rng_path: RelaxNG path
    :returns: a validation function
    '''

    rng_file = file(rng_path)
    try:
        rng = etree.parse(rng_file)
    finally:
        rng_file.close()

    relaxng = etree.RelaxNG(rng)

    def validate(inp_path):
        ''' Validate XML against %r
        ''' % rng_path
        from os.path import basename
        with file(inp_path) as f:
            inp = etree.parse(f)
        logger.info('_lxml.relaxng(%s) start', basename(rng_path))
        try:
            valid = relaxng.validate(inp)
        except Exception, e:
            logger.exception(e)
            raise
        else:
            if not valid:
                for error in relaxng.error_log:
                    logger.error('%s', error)
            return valid
        finally:
            logger.info('_lxml.relaxng(%s) end', basename(rng_path))
    return validate


def errlog_to_dict(error):
    return dict(message=error.message,
                filename=error.filename,
                line=error.line,
                column=error.column,
                domain=error.domain_name,
                type=error.type_name,
                level=error.level_name)
