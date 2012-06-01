# -*- coding: utf-8 -*-
import logging
import os
import os.path
try:
    homepath = os.environ['HOME']
    logpath = os.path.join(homepath, 'pyhwp.oxt.log')
    logging.basicConfig(filename=logpath, level=logging.DEBUG)
except KeyError:
    pass

def log_exception(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception, e:
            logging.exception(e)
            raise
    return wrapper

import uno
import unohelper

from com.sun.star.lang import XInitialization
from com.sun.star.document import XFilter, XImporter, XExtendedFilterDetection
from com.sun.star.task import XJobExecutor

g_ImplementationHelper = unohelper.ImplementationHelper()

def implementation(component_name, *services):
    def decorator(cls):
        g_ImplementationHelper.addImplementation(cls, component_name, services)
        return cls
    return decorator

class Fac(object):
    def __init__(self, context):
        self.context = context

    @property
    def storage_factory(self):
        return self.context.ServiceManager.createInstance('com.sun.star.embed.StorageFactory')

    def StorageFromInputStream(self, inputstream):
        return self.storage_factory.createInstanceWithArguments( (inputstream, 1) ) # com.sun.star.embed.ElementModes.READ

    def OLESimpleStorage(self, *args):
        return self.context.ServiceManager.createInstanceWithArguments('com.sun.star.embed.OLESimpleStorage', args)

    def SequenceInputStream(self, s):
        return self.context.ServiceManager.createInstanceWithArguments('com.sun.star.io.SequenceInputStream',
                (uno.ByteSequence(s),) )

    def UriReferenceFactory(self):
        return self.context.ServiceManager.createInstanceWithContext('com.sun.star.uri.UriReferenceFactory', self.context)

    def rdf_URI_create(self, uri):
        return self.context.ServiceManager.createInstanceWithArguments('com.sun.star.rdf.URI', (uri, ))

    def createBaseURI(self, storage, baseuri, subdoc):
        return self.rdf_URI_create(baseuri+'/')

    def readThroughComponent(self, storage, doc, streamname, filtername, filterargs, name):
        stream = storage.openStreamElement(streamname, 1) # READ
        return self.readStreamThroughComponent(stream, doc, filtername, filterargs, name)

    def readStreamThroughComponent(self, stream, doc, filtername, filterargs, name):
        from com.sun.star.xml.sax import InputSource
        inputsource = InputSource()
        inputsource.sSystemId = name
        inputsource.aInputStream = stream
        inputsource.sEncoding = 'utf-8'

        parser = self.saxParser()
        filter = self.context.ServiceManager.createInstanceWithArguments(filtername, filterargs)
        filter.setTargetDocument(doc)
        parser.setDocumentHandler(filter)
        parser.parseStream(inputsource)
        return True

    def PropertySet(self):
        return self.context.ServiceManager.createInstance('com.sun.star.beans.PropertySet')

    def GraphicObjectResolver(self, storage):
        return self.context.ServiceManager.createInstanceWithArguments('com.sun.star.comp.Svx.GraphicImportHelper', (storage,))

    def load_odt_from_storage(self, doc, storage, statusindicator=None):
        infoset = self.PropertySet()
        url = ''
        uri = self.createBaseURI(storage, url, '')
        doc.loadMetadataFromStorage(storage, uri, None)
        #self.readThroughComponent(storage, doc, 'meta.xml', 'com.sun.star.comp.Writer.XMLOasisMetaImporter', (infoset, None), '')
        graphicresolver = self.GraphicObjectResolver(storage)
        objectresolver = None
        lateinitsettings = None
        filterargs = (infoset, statusindicator, graphicresolver, objectresolver, lateinitsettings)
        self.readThroughComponent(storage, doc, 'styles.xml', 'com.sun.star.comp.Writer.XMLOasisStylesImporter', filterargs, '')
        self.readThroughComponent(storage, doc, 'content.xml', 'com.sun.star.comp.Writer.XMLOasisContentImporter', filterargs, '')

    def load_hwp5file_into_doc(self, hwp5file, doc, statusindicator=None):
        odtpkg_file = self.hwp5file_convert_to_odtpkg_file(hwp5file)
        logging.debug('hwp to odtpkg completed')

        odtpkg_stream = InputStreamFromFileLike(odtpkg_file)

        odtpkg_storage = self.StorageFromInputStream(odtpkg_stream)

        self.load_odt_from_storage(doc, odtpkg_storage, statusindicator)

    def saxParser(self):
        return self.context.ServiceManager.createInstance('com.sun.star.xml.sax.Parser')

    def HwpFileFromInputStream(self, inputstream):
        olestorage = self.OLESimpleStorage(inputstream)
        olefile = OleFileIO_from_OLESimpleStorage(olestorage)
        from hwp5.filestructure import File
        return File(olefile)

    def LibXSLTTransformer(self, stylesheet_url, source_url, source_url_base):
        from com.sun.star.beans import NamedValue
        args = (NamedValue('StylesheetURL', stylesheet_url),
                NamedValue('SourceURL', source_url),
                NamedValue('SourceBaseURL', source_url_base))
        return self.context.ServiceManager.createInstanceWithArguments('com.sun.star.comp.documentconversion.LibXSLTTransformer', args)

    def xsltproc_with_LibXSLTTransforrmer(self, stylesheet_path):
        stylesheet_url = uno.systemPathToFileUrl(os.path.realpath(stylesheet_path))
        import unohelper
        from com.sun.star.io import XOutputStream
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
                        print 'XSLT started'
                    def closed(self):
                        print 'XSLT closed'
                        pout.close()
                        self.t = None
                    def terminated(self):
                        print 'XSLT terminated'
                        pout.close()
                        self.t = None
                    def error(self, exception):
                        print 'XSLT error:', exception
                        print exception
                        pout.close()
                        self.t = None
                    def disposing(self, source):
                        print 'XSLT disposing:', source
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
                print 'XSLT transform over!'

        return transform

    def hwp5file_convert_to_odtpkg_file(self, hwp5file):
        from tempfile import TemporaryFile
        tmpfile = TemporaryFile()
        import os
        tmpfile2 = os.fdopen( os.dup(tmpfile.fileno()), 'r')

        from zipfile import ZipFile
        zf = ZipFile(tmpfile, 'w')
        from hwp5.hwp5odt import ODTPackage
        odtpkg = ODTPackage(zf)
        try:
            from hwp5.hwp5odt import hwp5file_to_odtpkg_converter

            # TODO Libreoffice 3.2 does not have LibXSLTTransformer yet
            # we use default xsltproc which uses external `xsltproc' program
            #xsltproc = self.xsltproc_with_LibXSLTTransformer
            from hwp5.hwp5odt import xsltproc

            hwp5file_convert_to_odtpkg = hwp5file_to_odtpkg_converter(xsltproc)
            hwp5file_convert_to_odtpkg(hwp5file, odtpkg)
        finally:
            odtpkg.close()

        tmpfile2.seek(0)
        return tmpfile2


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
        if hasattr(self.stream, 'closeOutput'):
            self.stream.closeOutput()

def container_recurse_elements(parent, parent_path_segments):
    for name in parent.getElementNames():
        elem = parent.getByName(name)

        path_segments = parent_path_segments + [name]
        yield path_segments

        if hasattr(elem, 'getElementNames'):
            for x in container_recurse_elements(elem, path_segments):
                yield x

def container_find_element(parent, path_segments):
    if len(path_segments) == 0:
        return parent

    if not hasattr(parent, 'getByName'):
        return None

    from com.sun.star.container import NoSuchElementException
    child_name = path_segments[0]
    try:
        child = parent.getByName(child_name)
    except NoSuchElementException:
        return None
    return container_find_element(child, path_segments[1:])

class OleFileIO_from_OLESimpleStorage(object):
    def __init__(self, storage):
        self.storage = storage

    def exists(self, name):
        return self.storage.hasByName(name)

    def listdir(self):
        for x in container_recurse_elements(self.storage, []):
            yield x

    def openstream(self, path):
        path_segments = path.split('/')
        stream = container_find_element(self.storage, path_segments)
        if stream is not None:
            return FileFromStream(stream)

def unofy_value(value):
    if isinstance(value, dict):
        value = dict_to_propseq(value)
    elif isinstance(value, list):
        value = tuple(value)
    return value

def xenumeration_generator(xenum):
    while xenum.hasMoreElements():
        yield xenum.nextElement()

def xenumeration_list(xenum):
    return list(xenumeration_generator(xenum))

def dict_to_propseq(d):
    from com.sun.star.beans import PropertyValue
    DIRECT_VALUE = uno.Enum('com.sun.star.beans.PropertyState', 'DIRECT_VALUE')
    return tuple(PropertyValue(k, 0, unofy_value(v), DIRECT_VALUE) for k, v in d.iteritems())

def propseq_to_dict(propvalues):
    return dict((p.Name, p.Value) for p in propvalues)

from com.sun.star.io import XInputStream, XSeekable
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

@implementation('pyhwp.Detector', 'com.sun.star.document.ExtendedTypeDetection')
class Detector(unohelper.Base, XExtendedFilterDetection):
    def __init__(self, ctx):
        self.ctx = ctx
        self.fac = Fac(ctx)

    @log_exception
    def detect(self, mediadesc):
        logging.debug('Detector detect()')
        desc = propseq_to_dict(mediadesc)

        #for k, v in desc.iteritems():
        #    logging.debug('Detector detect: %s: %s', k, str(v))

        inputstream = desc['InputStream']
        try:
            olestorage = self.fac.OLESimpleStorage(inputstream)
            olefile = OleFileIO_from_OLESimpleStorage(olestorage)

            from hwp5.filestructure import get_fileheader

            if not olefile.exists('FileHeader'):
                return '', mediadesc

            fileheader = get_fileheader(olefile)
            logging.debug('signature: %s', fileheader.signature)
            logging.debug('version: %s', fileheader.version)
            if fileheader.version[0] != 5:
                return '', mediadesc

            logging.debug('TypeName: %s', 'writer_pyhwp_HWPv5')
            return 'writer_pyhwp_HWPv5', mediadesc
        except Exception, e:
            logging.exception(e)
            return '', mediadesc


@implementation('pyhwp.Importer', 'com.sun.star.document.ImportFilter')
class Importer(unohelper.Base, XInitialization, XFilter, XImporter):

    @log_exception
    def __init__(self, ctx):
        self.ctx = ctx
        self.fac = Fac(ctx)

    @log_exception
    def initialize(self, args):
        logging.debug('Importer initialize: %s', args)

    @log_exception
    def setTargetDocument(self, target):
        logging.debug('Importer setTargetDocument: %s', target)
        self.target = target

    @log_exception
    def filter(self, mediadesc):
        logging.debug('Importer filter')
        desc = propseq_to_dict(mediadesc)

        logging.debug('mediadesc: %s', str(desc.keys()))
        for k, v in desc.iteritems():
            logging.debug('%s: %s', k, str(v))

        statusindicator = desc.get('StatusIndicator')

        inputstream = desc['InputStream']
        hwpfile = self.fac.HwpFileFromInputStream(inputstream)
        self.fac.load_hwp5file_into_doc(hwpfile, self.target, statusindicator)
        return True

    def cancel(self):
        logging.debug('Importer cancel')


@implementation('pyhwp.TestJob', 'com.sun.star.task.XJobExecutor')
class TestJob(unohelper.Base, XJobExecutor):
    def __init__(self, ctx):
        self.ctx = ctx

    def trigger(self, args):
        logging.debug('testjob %s', args)

        wd = args

        import os
        original_wd = os.getcwd()
        try:
            os.chdir(wd)

            from unittest import TextTestRunner
            testrunner = TextTestRunner()

            from unittest import TestSuite
            testrunner.run(TestSuite(self.tests()))
        finally:
            os.chdir(original_wd)

    def tests(self):
        from unittest import defaultTestLoader
        yield defaultTestLoader.loadTestsFromTestCase(DetectorTest)
        yield defaultTestLoader.loadTestsFromTestCase(ImporterTest)
        from hwp5.tests import test_suite
        yield test_suite()


from unittest import TestCase
class DetectorTest(TestCase):

    def test_detect(self):
        context = uno.getComponentContext()

        f = file('fixtures/sample-5017.hwp', 'r')
        stream = InputStreamFromFileLike(f)
        mediadesc = dict_to_propseq(dict(InputStream=stream))

        svm = context.ServiceManager
        detector = svm.createInstanceWithContext('pyhwp.Detector', context)
        typename, mediadesc2 = detector.detect(mediadesc)
        self.assertEquals('writer_pyhwp_HWPv5', typename)

class ImporterTest(TestCase):

    def test_filter(self):
        context = uno.getComponentContext()
        f = file('fixtures/sample-5017.hwp', 'r')
        stream = InputStreamFromFileLike(f)
        mediadesc = dict_to_propseq(dict(InputStream=stream))

        svm = context.ServiceManager
        importer = svm.createInstanceWithContext('pyhwp.Importer', context)
        desktop = svm.createInstanceWithContext('com.sun.star.frame.Desktop',
                                                context)
        doc = desktop.loadComponentFromURL('private:factory/swriter', '_blank',
                                           0, ())

        importer.setTargetDocument(doc)
        importer.filter(mediadesc)

        text = doc.getText()

        paragraphs = text.createEnumeration()
        paragraphs = xenumeration_list(paragraphs)
        for paragraph_ix, paragraph in enumerate(paragraphs):
            logging.info('Paragraph %s', paragraph_ix)
            logging.debug('%s', paragraph)

            services = paragraph.SupportedServiceNames
            if 'com.sun.star.text.Paragraph' in services:
                portions = xenumeration_list(paragraph.createEnumeration())
                for portion_ix, portion in enumerate(portions):
                    logging.info('Portion %s: %s', portion_ix,
                                 portion.TextPortionType)
                    if portion.TextPortionType == 'Text':
                        logging.info('- %s', portion.getString())
                    elif portion.TextPortionType == 'Frame':
                        logging.debug('%s', portion)
                        textcontent_name = 'com.sun.star.text.TextContent'
                        en = portion.createContentEnumeration(textcontent_name)
                        contents = xenumeration_list(en)
                        for content in contents:
                            logging.debug('content: %s', content)
                            content_services = content.SupportedServiceNames
                            if ('com.sun.star.drawing.GraphicObjectShape' in
                                content_services):
                                logging.info('graphic url: %s',
                                             content.GraphicURL)
                                logging.info('graphic stream url: %s',
                                             content.GraphicStreamURL)
            if 'com.sun.star.text.TextTable' in services:
                pass
            else:
                pass

        paragraph_portions = paragraphs[0].createEnumeration()
        paragraph_portions = xenumeration_list(paragraph_portions)
        self.assertEquals(u'한글 ', paragraph_portions[0].getString())

        paragraph_portions = paragraphs[16].createEnumeration()
        paragraph_portions = xenumeration_list(paragraph_portions)
        contents = paragraph_portions[1].createContentEnumeration('com.sun.star.text.TextContent')
        contents = xenumeration_list(contents)
        self.assertEquals('vnd.sun.star.Package:bindata/BIN0003.png',
                          contents[0].GraphicStreamURL)

        graphics = doc.getGraphicObjects()
        graphics = xenumeration_list(graphics.createEnumeration())
        logging.debug('graphic: %s', graphics)

        frames = doc.getTextFrames()
        frames = xenumeration_list(frames.createEnumeration())
        logging.debug('frames: %s', frames)
