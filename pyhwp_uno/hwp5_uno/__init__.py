# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010 mete0r@sarangbang.or.kr
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

import uno
import unohelper
from unokit.services import css
from unokit.adapters import InputStreamFromFileLike
from unokit.adapters import OutputStreamToFileLike
from unokit.adapters import FileFromStream
from com.sun.star.io import XStreamListener
import logging


logger = logging.getLogger('hwp5.uno')


class OleStorageAdapter(object):

    def __init__(self, oless):
        ''' an OLESimpleStorage to hwp5 storage adapter.

        :param oless: an instance of OLESimpleStorage
        '''
        self.oless = oless

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
            return OleStorageAdapter(elem)
        else:
            elem.closeInput()
            return OleStorageStream(self.oless, name)


class OleStorageStream(object):

    def __init__(self, oless, name):
        self.oless = oless
        self.name = name

    def open(self):
        stream = self.oless.getByName(self.name)
        return FileFromStream(stream)


def HwpFileFromInputStream(inputstream):
    ''' Hwp5File from com.sun.star.io.InputStream '''
    olestorage = css.embed.OLESimpleStorage(inputstream)
    adapter = OleStorageAdapter(olestorage)
    from hwp5.xmlmodel import Hwp5File
    return Hwp5File(adapter)


def StorageFromInputStream(inputstream):
    factory = css.embed.StorageFactory()
    return factory.createInstanceWithArguments((inputstream, 1)) # com.sun.star.embed.ElementModes.READ


def XSLTTransformer(stylesheet_url, source_url, source_url_base):
    from com.sun.star.beans import NamedValue
    args = (NamedValue('StylesheetURL', stylesheet_url),
            NamedValue('SourceURL', source_url),
            NamedValue('SourceBaseURL', source_url_base))
    #return css.comp.documentconversion.LibXSLTTransformer(*args)
    return css.comp.JAXTHelper(*args)


def haveXSLTTransformer():
    transformer = XSLTTransformer('', '', '')
    return transformer is not None


class OneshotEvent(object):

    def __init__(self):
        import os
        pin, pout = os.pipe()
        self.pin = os.fdopen(pin, 'r')
        self.pout = os.fdopen(pout, 'w')

    def wait(self):
        self.pin.read()
        self.pin.close()

    def signal(self):
        self.pout.close()


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


def xslt_with_libreoffice(stylesheet_path):
    import os.path
    stylesheet_url = uno.systemPathToFileUrl(os.path.realpath(stylesheet_path))
    def transform(inp, out):
        transformer = XSLTTransformer(stylesheet_url, '', '')
        transformer.InputStream = InputStreamFromFileLike(inp, dontclose=True)
        transformer.OutputStream = OutputStreamToFileLike(out, dontclose=True)

        listener = XSLTListener()
        transformer.addListener(listener)

        transformer.start()
        import os.path
        xsl_name = os.path.basename(stylesheet_path)
        logger.info('xslt.soffice(%s) start', xsl_name)
        try:
            listener.event.wait()
        finally:
            logger.info('xslt.soffice(%s) end', xsl_name)

        transformer.removeListener(listener)
    return transform


def load_hwp5file_into_doc(hwp5file, doc, statusindicator=None):
    odtpkg = convert_hwp5file_into_odtpkg(hwp5file)
    logger.debug('hwp to odtpkg completed')

    load_odt_from_storage(doc, odtpkg, statusindicator)


def convert_hwp5file_into_odtpkg(hwp5file):
    from tempfile import TemporaryFile
    tmpfile = TemporaryFile()
    import os
    tmpfile2 = os.fdopen( os.dup(tmpfile.fileno()), 'r')

    from zipfile import ZipFile
    zf = ZipFile(tmpfile, 'w')
    from hwp5.hwp5odt import ODTPackage
    odtpkg = ODTPackage(zf)
    try:
        from hwp5.hwp5odt import Converter
        import hwp5.tools

        if haveXSLTTransformer():
            xslt = xslt_with_libreoffice
        else:
            # we use default xslt
            xslt = hwp5.tools.xslt

        # convert without RelaxNG validation
        convert = Converter(xslt)

        # Embed images: see #32 - https://github.com/mete0r/pyhwp/issues/32
        convert(hwp5file, odtpkg, embedimage=True)
    finally:
        odtpkg.close()

    tmpfile2.seek(0)
    odtpkg_stream = InputStreamFromFileLike(tmpfile2)
    odtpkg_storage = StorageFromInputStream(odtpkg_stream)
    return odtpkg_storage


def load_odt_from_storage(doc, storage, statusindicator=None):

    infoset = css.beans.PropertySet()
    uri = css.rdf.URI('/')

    # re-initialize the document metadata, loads the stream named
    # 'manifest.rdf' from the storage, and then loads all metadata streams
    # mentioned in the manifest.
    # (>= OOo 3.2)
    doc.loadMetadataFromStorage(storage, uri, None)
    # SfxBaseModel::loadMetadataFromStorage
    # -> sfx2::DocumentMetadataAccess::loadMetadataFromStorage
    # ---> initLoading
    # ---> collectFilesFromStorage

    Writer = css.comp.Writer

    meta_xml = InputSourceFromStorage(storage, 'meta.xml')
    if meta_xml:
        meta_importer = Writer.XMLOasisMetaImporter(infoset, statusindicator)
        let_document_import_xml(doc, meta_importer, meta_xml)

    # svx/inc/svx/xmlgrhlp.hxx
    # svx/source/xml/xmlgrhlp.cxx
    # svx/util/svx.component
    # new SvXMLGraphicImportExportHelper
    graphicresolver = css.comp.Svx.GraphicImportHelper(storage)
    objectresolver = None
    lateinitsettings = None
    filterargs = (infoset, statusindicator, graphicresolver, objectresolver, lateinitsettings)

    styles_xml = InputSourceFromStorage(storage, 'styles.xml')
    if styles_xml:
        styles_importer = Writer.XMLOasisStylesImporter(*filterargs)
        let_document_import_xml(doc, styles_importer, styles_xml)

    content_xml = InputSourceFromStorage(storage, 'content.xml')
    if content_xml:
        content_importer = Writer.XMLOasisContentImporter(*filterargs)
        let_document_import_xml(doc, content_importer, content_xml)


def InputSourceFromStorage(storage, streamname):
    if storage.hasByName(streamname):
        stream = storage.openStreamElement(streamname, 1) # READ
        return InputSourceFromStream(stream)


def InputSourceFromStream(stream):
    from com.sun.star.xml.sax import InputSource
    inputsource = InputSource()
    inputsource.sSystemId = ''
    inputsource.aInputStream = stream
    inputsource.sEncoding = 'utf-8'
    return inputsource


def let_document_import_xml(doc, filter, inputsource):
    filter.setTargetDocument(doc)
    parser = css.xml.sax.Parser()
    parser.setDocumentHandler(filter)
    parser.parseStream(inputsource)


def inputstream_is_hwp5file(inputstream):
    try:
        olestorage = css.embed.OLESimpleStorage(inputstream)
        adapter = OleStorageAdapter(olestorage)

        from hwp5.filestructure import storage_is_hwp5file
        return storage_is_hwp5file(adapter)
    except Exception, e:
        logger.exception(e)
        return False


def typedetect(inputstream):
    if inputstream_is_hwp5file(inputstream):
        return 'hwp5'
    return ''
