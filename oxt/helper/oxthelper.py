# -*- coding: utf-8 -*-

import uno
from unokit.adapters import InputStreamFromFileLike
from unokit.adapters import OutputStreamToFileLike
from unokit.adapters import FileFromStream
import logging


logger = logging.getLogger(__name__)


class FacMixin(object):

    def createInstance(self, name, *args):
        SM = self.context.ServiceManager
        if len(args) > 0:
            return SM.createInstanceWithArgumentsAndContext(name, args,
                                                            self.context)
        else:
            return SM.createInstanceWithContext(name, self.context)

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
        serviceName = 'com.sun.star.comp.JAXTHelper'
        serviceName = 'com.sun.star.comp.documentconversion.LibXSLTTransformer'
        return self.createInstance(serviceName, *args)

    def haveLibXSLTTransformer(self):
        transformer = self.LibXSLTTransformer('', '', '')
        return transformer is not None

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


class OutputStreamToFileLikeNonClosing(OutputStreamToFileLike):
    def closeOutput(self):
        # non closing
        pass


class InputStreamFromFileLikeNonClosing(InputStreamFromFileLike):
    def closeInput(self):
        # non closing
        pass
