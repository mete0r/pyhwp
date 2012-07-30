# -*- coding: utf-8 -*-

import uno
import unohelper
from com.sun.star.io import XInputStream, XSeekable
from com.sun.star.io import XOutputStream
import logging


logger = logging.getLogger(__name__)


class InputStreamFromFileLike(unohelper.Base, XInputStream, XSeekable):
    def __init__(self, f):
        self.f = f

    def readBytes(self, aData, nBytesToRead):
        #logging.debug('InputStream.readBytes(%d)', nBytesToRead)
        data = self.f.read(nBytesToRead)
        return len(data), uno.ByteSequence(data)

    readSomeBytes = readBytes

    def skipBytes(self, nBytesToSkip):
        #logging.debug('InputStream.skipBytes(%d)', nBytesToSkip)
        self.f.read(nBytesToSkip)

    def available(self):
        #logging.debug('InputStream.available()')
        return 0

    def closeInput(self):
        #logging.debug('InputStream.close()')
        self.f.close()

    def seek(self, location):
        #logging.debug('InputStream.seek(%d)', location)
        self.f.seek(location)

    def getPosition(self):
        pos = self.f.tell()
        #logging.debug('InputStream.getPosition(): %d', pos)
        return pos

    def getLength(self):
        pos = self.f.tell()
        try:
            self.f.seek(0, 2)
            length = self.f.tell()
            #logging.debug('InputStream.getLength(): %d', length)
            return length
        finally:
            self.f.seek(pos)


class FileFromStream(object):
    def __init__(self, stream):
        self.stream = stream

        if hasattr(stream, 'readBytes'):
            def read(size=None):
                if size is None:
                    data = ''
                    while True:
                        bytes = uno.ByteSequence('')
                        n_read, bytes = stream.readBytes(bytes, 4096)
                        if n_read == 0:
                            return data
                        data += bytes.value
                bytes = uno.ByteSequence('')
                n_read, bytes = stream.readBytes(bytes, size)
                return bytes.value
            self.read = read

        if hasattr(stream, 'seek'):
            self.tell = stream.getPosition

            def seek(offset, whence=0):
                if whence == 0:
                    pass
                elif whence == 1:
                    offset += stream.getPosition()
                elif whence == 2:
                    offset += stream.getLength()
                stream.seek(offset)
            self.seek = seek

        if hasattr(stream, 'writeBytes'):
            def write(s):
                stream.writeBytes(uno.ByteSequence(s))
            self.write = write

            def flush():
                stream.flush()
            self.flush = flush

    def close(self):
        if hasattr(self.stream, 'closeInput'):
            self.stream.closeInput()
        elif hasattr(self.stream, 'closeOutput'):
            self.stream.closeOutput()


class FacMixin(object):

    def createInstance(self, name, *args):
        SM = self.context.ServiceManager
        if len(args) > 0:
            return SM.createInstanceWithArguments(name, args)
        else:
            return SM.createInstance(name)

    @property
    def storage_factory(self):
        return self.createInstance('com.sun.star.embed.StorageFactory')

    def StorageFromInputStream(self, inputstream):
        return self.storage_factory.createInstanceWithArguments( (inputstream, 1) ) # com.sun.star.embed.ElementModes.READ

    def OLESimpleStorage(self, *args):
        return self.createInstance('com.sun.star.embed.OLESimpleStorage', *args)

    def SequenceInputStream(self, s):
        return self.createInstance('com.sun.star.io.SequenceInputStream', uno.ByteSequence(s))

    def UriReferenceFactory(self):
        return self.context.ServiceManager.createInstanceWithContext('com.sun.star.uri.UriReferenceFactory', self.context)

    def rdf_URI_create(self, uri):
        return self.createInstance('com.sun.star.rdf.URI', uri)

    def createBaseURI(self, storage, baseuri, subdoc):
        return self.rdf_URI_create(baseuri+'/')

    def PropertySet(self):
        return self.createInstance('com.sun.star.beans.PropertySet')

    def GraphicObjectResolver(self, storage):
        # svx/inc/svx/xmlgrhlp.hxx
        # svx/source/xml/xmlgrhlp.cxx
        # svx/util/svx.component
        # new SvXMLGraphicImportExportHelper
        name = 'com.sun.star.comp.Svx.GraphicImportHelper'
        return self.createInstance(name, storage)

    def EmbeddedObjectResolver(self, storage, persist):
        # persist: an instance of SfxObjectShell (doc.GetPersist())
        # svx/inc/svx/xmleohlp.cxx
        # svx/source/xml/xmleohlp.cxx
        # pObjectHelper = SvXMLEmbeddedObjectHelper::Create(
        #                 xStorage, *pPersist,
        #                 EMBEDDEDOBJECTHELPER_MODE_READ,
        #                 sal_False );
        return None

    def saxParser(self):
        return self.createInstance('com.sun.star.xml.sax.Parser')

    def LibXSLTTransformer(self, stylesheet_url, source_url, source_url_base):
        from com.sun.star.beans import NamedValue
        args = (NamedValue('StylesheetURL', stylesheet_url),
                NamedValue('SourceURL', source_url),
                NamedValue('SourceBaseURL', source_url_base))
        return self.createInstance('com.sun.star.comp.documentconversion.LibXSLTTransformer',
                                   *args)

    def xsltproc_with_LibXSLTTransformer(self, stylesheet_path):
        import os.path
        stylesheet_url = uno.systemPathToFileUrl(os.path.realpath(stylesheet_path))
        import unohelper
        def transform(stdin=None, stdout=None):

            if stdin:
                inputstream = InputStreamFromFileLikeNonClosing(stdin)
            else:
                inputstream = p_outputstream = self.pipe()

            if stdout:
                outputstream = OutputStreamToFileLikeNonClosing(stdout)
            else:
                p_inputstream = outputstream = self.pipe()

            transformer = self.LibXSLTTransformer(stylesheet_url, '', '')
            transformer.setInputStream(inputstream)
            transformer.setOutputStream(outputstream)
            if stdin and stdout:
                import os
                pin, pout = os.pipe()
                pin = os.fdopen(pin, 'r')
                pout = os.fdopen(pout, 'w')
                from com.sun.star.io import XStreamListener
                class Listener(unohelper.Base, XStreamListener):
                    def __init__(self):
                        # workaround for a bug in LibXSLTTransformer:
                        #
                        # we should retain a reference to the LibXSLTTransformer
                        # while transforming is ongoing or the transformer
                        # will be disposed and the internal Reader thread crashes!
                        # (the Reader thread seems not retain the reference to the
                        # transformer instance.)
                        self.t = transformer
                    def started(self):
                        logger.debug('XSLT started')
                    def closed(self):
                        logger.debug('XSLT closed')
                        pout.close()
                        self.t = None
                    def terminated(self):
                        logger.debug('XSLT terminated')
                        pout.close()
                        self.t = None
                    def error(self, exception):
                        logger.debug('XSLT error')
                        logger.exception(exception)
                        pout.close()
                        self.t = None
                    def disposing(self, source):
                        logger.debug('XSLT disposing: %s', source)
                        pout.close()
                        self.t = None
                transformer.addListener(Listener())

            transformer.start()

            if stdin is None and stdout is None:
                return FileFromStream(p_inputstream), FileFromStream(p_outputstream)
            elif stdin is None:
                return FileFromStream(p_outputstream)
            elif stdout is None:
                return FileFromStream(p_inputstream)
            else:
                pin.read()
                pin.close()
                logger.debug('XSLT transform over!')

        return transform


class OutputStreamToFileLikeNonClosing(unohelper.Base, XOutputStream):
    def __init__(self, f):
        self.f = f

    def writeBytes(self, bytesequence):
        self.f.write(bytesequence.value)

    def flush(self):
        self.f.flush()

    def closeOutput(self):
        # non closing
        pass


class InputStreamFromFileLikeNonClosing(InputStreamFromFileLike):
    def closeInput(self):
        # non closing
        pass
