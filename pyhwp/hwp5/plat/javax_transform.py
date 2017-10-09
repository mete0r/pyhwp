# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2017 mete0r <mete0r@sarangbang.or.kr>
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
from contextlib import closing
import io
import logging
import os.path
import sys


logger = logging.getLogger(__name__)


def is_enabled():
    if not sys.platform.startswith('java'):
        logger.info('%s: disabled', __name__)
        return False
    try:
        import javax.xml.transform
        javax
    except ImportError:
        logger.info('%s: disabled', __name__)
        return False
    else:
        logger.info('%s: enabled', __name__)
        return True


def xslt(xsl_path, inp_path, out_path):
    transform = xslt_compile(xsl_path)
    with io.open(out_path, 'wb') as f:
        return transform(inp_path, f)


class XSLT:

    def __init__(self, xsl_path, **params):
        from javax.xml.transform import URIResolver
        from javax.xml.transform import TransformerFactory
        from javax.xml.transform.stream import StreamSource
        from java.io import FileInputStream

        xsl_path = os.path.abspath(xsl_path)
        xsl_base = os.path.dirname(xsl_path)

        xsl_fis = FileInputStream(xsl_path)

        xsl_source = StreamSource(xsl_fis)

        class BaseURIResolver(URIResolver):

            def __init__(self, base):
                self.base = base

            def resolve(self, href, base):
                path = os.path.join(self.base, href)
                path = os.path.abspath(path)
                fis = FileInputStream(path)
                return StreamSource(fis)

        uri_resolver = BaseURIResolver(xsl_base)

        xslt_factory = TransformerFactory.newInstance()
        xslt_factory.setURIResolver(uri_resolver)

        self.transformer = xslt_factory.newTransformer(xsl_source)
        for k, v in params.items():
            self.transformer.setParameter(k, unicode(v))

    def transform(self, input, output):
        '''
        >>> T.transform('input.xml', 'output.xml')
        '''
        from java.io import FileInputStream
        from java.io import FileOutputStream
        out_path = os.path.abspath(output)
        inp_path = os.path.abspath(input)
        with closing(FileInputStream(inp_path)) as inp_fis:
            with closing(FileOutputStream(out_path)) as out_fos:
                return self._transform(inp_fis, out_fos)

    def transform_into_stream(self, input, output):
        '''
        >>> T.transform('input.xml', sys.stdout)
        '''
        from java.io import FileInputStream
        inp_path = os.path.abspath(input)
        with closing(FileInputStream(inp_path)) as inp_fis:
            out_fos = wrap_filelike_outputstream(output)
            return self._transform(inp_fis, out_fos)

    def _transform(self, input, output):
        from javax.xml.transform.stream import StreamSource
        from javax.xml.transform.stream import StreamResult
        inp_source = StreamSource(input)
        out_result = StreamResult(output)
        self.transformer.transform(inp_source, out_result)
        return dict()


def xslt_compile(xsl_path, **params):
    xslt = XSLT(xsl_path, **params)
    return xslt.transform_into_stream


def wrap_filelike_inputstream(f):
    from org.python.core import FilelikeInputStream
    return FilelikeInputStream(f)


def wrap_filelike_outputstream(f):
    from java.io import OutputStream

    class FilelikeOutputStream(OutputStream):

        def write(self, *args):
            if len(args) == 1:
                # byte
                ch = chr(args[0] & 0xff)
                f.write(ch)
            if len(args) == 3:
                # array.array, offset, length
                array, offset, length = args
                buf = array.tostring()
                f.write(buf[offset:offset+length])
            else:
                logger.debug('%r', args)
                self.super__write(*args)

        def flush(self):
            f.flush()

        def close(self):
            pass
    return FilelikeOutputStream()
