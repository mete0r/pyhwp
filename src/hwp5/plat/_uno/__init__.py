# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2015 mete0r <mete0r@sarangbang.or.kr>
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
import io
import logging
import os.path
import sys

from ...errors import InvalidOleStorageError


PY3 = sys.version_info.major == 3
if PY3:
    basestring = str


logger = logging.getLogger(__name__)

enabled = False


def is_enabled():
    if 'PYHWP_PLAT_UNO' in os.environ:
        PYHWP_PLAT_UNO = os.environ['PYHWP_PLAT_UNO'].strip()
        try:
            forced = bool(int(PYHWP_PLAT_UNO))
            logger.debug('%s: forced to be %s by PYHWP_PLAT_UNO', __name__,
                         'enabled' if forced else 'disabled')
            return forced
        except:
            logger.warning('PYHWP_PLAT_UNO=%s (invalid)', PYHWP_PLAT_UNO)
    logger.debug('%s: is %s', __name__, 'enabled' if enabled else 'disabled')
    return enabled


def enable():
    import uno
    import unohelper

    g = globals()
    g['uno'] = uno
    g['unohelper'] = unohelper
    g['enabled'] = True
    logger.info('%s: enabled.', __name__)


def disable():
    global enabled
    enabled = False
    logger.info('%s: disabled.', __name__)


def XSLTTransformer(context, stylesheet_url, source_url, source_url_base):
    from com.sun.star.beans import NamedValue
    from hwp5.plat._uno.services import css
    args = (NamedValue('StylesheetURL', stylesheet_url),
            NamedValue('SourceURL', source_url),
            NamedValue('SourceBaseURL', source_url_base))
    select = os.environ.get('PYHWP_PLAT_UNO_XSLT', 'libxslt')
    logger.debug('PYHWP_PLAT_UNO_XSLT = %s', select)
    if select == 'jaxthelper':
        logger.debug('%s.xslt: using css.comp.JAXTHelper', __name__)
        return css.comp.JAXTHelper(context, *args)
    else:
        logger.debug('%s.xslt: using %s', __name__,
                     'css.comp.documentconversion.LibXSLTTransformer')
        return css.comp.documentconversion.LibXSLTTransformer(context, *args)


class OneshotEvent(object):

    def __init__(self):
        pin, pout = os.pipe()
        self.pin = os.fdopen(pin, 'r')
        self.pout = os.fdopen(pout, 'w')

    def wait(self):
        self.pin.read()
        self.pin.close()

    def signal(self):
        self.pout.close()


class XSLT(object):

    def __init__(self, context):
        self.context = context

    def __call__(self, xsl_path, inp_path, out_path):
        import uno
        import unohelper
        from hwp5.plat._uno import ucb
        from hwp5.plat._uno.adapters import OutputStreamToFileLike
        xsl_path = os.path.abspath(xsl_path)
        xsl_url = uno.systemPathToFileUrl(xsl_path)

        inp_path = os.path.abspath(inp_path)
        inp_url = uno.systemPathToFileUrl(inp_path)
        inp_stream = ucb.open_url(self.context, inp_url)

        out_path = os.path.abspath(out_path)
        with io.open(out_path, 'wb') as out_file:
            out_stream = OutputStreamToFileLike(out_file, dontclose=True)

            from com.sun.star.io import XStreamListener

            class XSLTListener(unohelper.Base, XStreamListener):
                def __init__(self):
                    self.event = OneshotEvent()

                def started(self):
                    logger.info('XSLT started')

                def closed(self):
                    logger.info('XSLT closed')
                    self.event.signal()

                def terminated(self):
                    logger.info('XSLT terminated')
                    self.event.signal()

                def error(self, exception):
                    logger.error('XSLT error: %s', exception)
                    self.event.signal()

                def disposing(self, source):
                    logger.info('XSLT disposing: %s', source)
                    self.event.signal()

            listener = XSLTListener()
            transformer = XSLTTransformer(self.context, xsl_url, '', '')
            transformer.InputStream = inp_stream
            transformer.OutputStream = out_stream
            transformer.addListener(listener)

            transformer.start()
            xsl_name = os.path.basename(xsl_path)
            logger.info('xslt.soffice(%s) start', xsl_name)
            try:
                listener.event.wait()
            finally:
                logger.info('xslt.soffice(%s) end', xsl_name)

            transformer.removeListener(listener)
            return dict()


def xslt(xsl_path, inp_path, out_path):
    import uno
    context = uno.getComponentContext()
    xslt = XSLT(context)
    return xslt(xsl_path, inp_path, out_path)


def oless_from_filename(filename):
    inputstream = inputstream_from_filename(filename)
    return oless_from_inputstream(inputstream)


def inputstream_from_filename(filename):
    f = io.open(filename, 'rb')
    from hwp5.plat._uno.adapters import InputStreamFromFileLike
    return InputStreamFromFileLike(f)


def oless_from_inputstream(inputstream):
    import uno
    context = uno.getComponentContext()
    sm = context.ServiceManager
    name = 'com.sun.star.embed.OLESimpleStorage'
    args = (inputstream, )
    return sm.createInstanceWithArgumentsAndContext(name, args, context)


class OleStorage(object):

    def __init__(self, stg):
        ''' an OLESimpleStorage to hwp5 storage adapter.

        :param stg: a filename or an instance of OLESimpleStorage
        '''
        if isinstance(stg, basestring):
            self.oless = oless_from_filename(stg)
            try:
                self.oless.getElementNames()
            except:
                errormsg = 'Not a valid OLE2 Compound Binary File.'
                raise InvalidOleStorageError(errormsg)
        else:
            # TODO assert stg is an instance of OLESimpleStorage
            self.oless = stg

    def __iter__(self):
        return iter(self.oless.getElementNames())

    def __getitem__(self, name):
        from com.sun.star.container import NoSuchElementException
        try:
            elem = self.oless.getByName(name)
        except NoSuchElementException:
            raise KeyError(name)
        services = elem.SupportedServiceNames
        if 'com.sun.star.embed.OLESimpleStorage' in services:
            return OleStorage(elem)
        else:
            elem.closeInput()
            return OleStorageStream(self.oless, name)

    def close(self):
        return
        # TODO
        # if this is root, close underlying olefile
        if self.path == '':
            # old version of OleFileIO has no close()
            if hasattr(self.olefile, 'close'):
                self.olefile.close()


class OleStorageStream(object):

    def __init__(self, oless, name):
        self.oless = oless
        self.name = name

    def open(self):
        from hwp5.plat._uno.adapters import FileFromStream
        stream = self.oless.getByName(self.name)
        return FileFromStream(stream)
