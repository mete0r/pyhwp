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


def is_enabled():
    import sys
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
    return transform(inp_path, out_path)


def xslt_compile(xsl_path):
    from javax.xml.transform import URIResolver
    from javax.xml.transform import TransformerFactory
    from javax.xml.transform.stream import StreamSource
    from javax.xml.transform.stream import StreamResult
    from java.io import FileInputStream
    from java.io import FileOutputStream
    import os.path

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

    transformer = xslt_factory.newTransformer(xsl_source)

    def transform(inp_path, out_path):
        inp_path = os.path.abspath(inp_path)
        out_path = os.path.abspath(out_path)
        inp_fis = FileInputStream(inp_path)
        out_fos = FileOutputStream(out_path)
        inp_source = StreamSource(inp_fis)
        out_result = StreamResult(out_fos)
        transformer.transform(inp_source, out_result)
        return dict()
    return transform
