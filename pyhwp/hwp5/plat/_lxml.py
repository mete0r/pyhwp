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
from contextlib import contextmanager
import logging
import os.path
import shutil
import tempfile

from ..errors import ValidationFailed


logger = logging.getLogger(__name__)


def is_enabled():
    try:
        from lxml import etree  # noqa
    except ImportError:
        return False
    else:
        return True


def xslt(xsl_path, inp_path, out_path):
    ''' Transform XML with XSL

    :param xsl_path: stylesheet path
    :param inp_path: input path
    :param out_path: output path
    '''
    transform = xslt_compile(xsl_path)
    with file(out_path, 'w') as f:
        return transform(inp_path, f)


def xslt_compile(xsl_path, **params):
    xslt = XSLT(xsl_path, **params)
    return xslt.transform_into_stream


class XSLT:

    def __init__(self, xsl_path, **params):
        ''' Compile XSL Transform function.
        :param xsl_path: stylesheet path
        :returns: a transform function
        '''
        from lxml import etree

        with file(xsl_path) as xsl_file:
            xsl_doc = etree.parse(xsl_file)

        self.xsl_path = xsl_path
        self.etree_xslt = etree.XSLT(xsl_doc)
        self.params = dict((name, etree.XSLT.strparam(value))
                           for name, value in params.items())

    def transform(self, input, output):
        '''
        >>> T.transform('input.xml', 'output.xml')
        '''
        with file(input) as inp_file:
            with file(output, 'w') as out_file:
                return self._transform(inp_file, out_file)

    def transform_into_stream(self, input, output):
        '''
        >>> T.transform_into_stream('input.xml', sys.stdout)
        '''
        with file(input) as inp_file:
            return self._transform(inp_file, output)

    def _transform(self, input, output):
        from lxml import etree
        source = etree.parse(input)
        logger.info('_lxml.xslt(%s) start',
                    os.path.basename(self.xsl_path))
        result = self.etree_xslt(source, **self.params)
        logger.info('_lxml.xslt(%s) end',
                    os.path.basename(self.xsl_path))
        output.write(str(result))
        return dict()


def relaxng(rng_path, inp_path):
    relaxng = RelaxNG(rng_path)
    return relaxng.validate(inp_path)


def relaxng_compile(rng_path):
    ''' Compile RelaxNG file

    :param rng_path: RelaxNG path
    :returns: a validation function
    '''
    return RelaxNG(rng_path)


class RelaxNG:

    def __init__(self, rng_path):
        from lxml import etree

        with file(rng_path) as rng_file:
            rng = etree.parse(rng_file)

        self.rng_path = rng_path
        self.etree_relaxng = etree.RelaxNG(rng)

    @contextmanager
    def validating_output(self, output):
        fd, name = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'w+') as f:
                yield f
                f.seek(0)
                if not self.validate_stream(f):
                    raise ValidationFailed('RelaxNG')
                f.seek(0)
                shutil.copyfileobj(f, output)
        finally:
            try:
                os.unlink(name)
            except Exception, e:
                logger.warning('%s: can\'t unlink %s', e, name)

    def validate(self, input):
        from lxml import etree
        with file(input) as f:
            doc = etree.parse(f)
        return self._validate(doc)

    def validate_stream(self, input):
        from lxml import etree
        doc = etree.parse(input)
        return self._validate(doc)

    def _validate(self, doc):
        from os.path import basename
        logger.info('_lxml.relaxng(%s) start', basename(self.rng_path))
        try:
            valid = self.etree_relaxng.validate(doc)
        except Exception, e:
            logger.exception(e)
            raise
        else:
            if not valid:
                for error in self.etree_relaxng.error_log:
                    logger.error('%s', error)
            return valid
        finally:
            logger.info('_lxml.relaxng(%s) end', basename(self.rng_path))


def errlog_to_dict(error):
    return dict(message=error.message,
                filename=error.filename,
                line=error.line,
                column=error.column,
                domain=error.domain_name,
                type=error.type_name,
                level=error.level_name)
