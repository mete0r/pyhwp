# -*- coding: utf-8 -*-
import logging
import os
import os.path


# initialize logging system
logger = logging.getLogger('hwp5')

loglevel = os.environ.get('PYHWP_OXT_LOGLEVEL')
if loglevel:
    loglevel = dict(DEBUG=logging.DEBUG,
                    INFO=logging.INFO,
                    WARNING=logging.WARNING,
                    ERROR=logging.ERROR,
                    CRITICAL=logging.CRITICAL).get(loglevel.upper(),
                                                   logging.WARNING)
    logger.setLevel(loglevel)
del loglevel

filename = os.environ.get('PYHWP_OXT_LOGFILE')
if filename:
    logger.addHandler(logging.FileHandler(filename))
del filename


def log_exception(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception, e:
            logger.exception(e)
            raise
    return wrapper

import uno
import unohelper
from oxthelper import FacMixin, FileFromStream, InputStreamFromFileLike

from com.sun.star.lang import XInitialization
from com.sun.star.document import XFilter, XImporter, XExtendedFilterDetection
from com.sun.star.task import XJobExecutor

g_ImplementationHelper = unohelper.ImplementationHelper()

def implementation(component_name, *services):
    def decorator(cls):
        g_ImplementationHelper.addImplementation(cls, component_name, services)
        return cls
    return decorator

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

@implementation('pyhwp.Detector', 'com.sun.star.document.ExtendedTypeDetection')
class Detector(unohelper.Base, XExtendedFilterDetection, FacMixin):
    def __init__(self, ctx):
        self.context = ctx

    @log_exception
    def detect(self, mediadesc):
        logger.debug('Detector detect()')
        desc = propseq_to_dict(mediadesc)

        #for k, v in desc.iteritems():
        #    logger.debug('Detector detect: %s: %s', k, str(v))

        inputstream = desc['InputStream']
        try:
            olestorage = self.OLESimpleStorage(inputstream)
            adapter = OleStorageAdapter(olestorage)

            from hwp5.filestructure import storage_is_hwp5file
            if not storage_is_hwp5file(adapter):
                return '', mediadesc
            logger.debug('TypeName: %s', 'writer_pyhwp_HWPv5')
            return 'writer_pyhwp_HWPv5', mediadesc
        except Exception, e:
            logger.exception(e)
            return '', mediadesc


@implementation('pyhwp.Importer', 'com.sun.star.document.ImportFilter')
class Importer(unohelper.Base, XInitialization, XFilter, XImporter, FacMixin):

    @log_exception
    def __init__(self, ctx):
        self.context = ctx

    @log_exception
    def initialize(self, args):
        logger.debug('Importer initialize: %s', args)

    @log_exception
    def setTargetDocument(self, target):
        logger.debug('Importer setTargetDocument: %s', target)
        self.target = target

    @log_exception
    def filter(self, mediadesc):
        from hwp5.dataio import ParseError

        logger.debug('Importer filter')
        desc = propseq_to_dict(mediadesc)

        logger.debug('mediadesc: %s', str(desc.keys()))
        for k, v in desc.iteritems():
            logger.debug('%s: %s', k, str(v))

        statusindicator = desc.get('StatusIndicator')

        inputstream = desc['InputStream']
        hwpfile = self.HwpFileFromInputStream(inputstream)
        try:
            self.load_hwp5file_into_doc(hwpfile, self.target, statusindicator)
        except ParseError, e:
            e.print_to_logger(logger)
            return False
        except Exception, e:
            logger.exception(e)
            return False
        else:
            return True

    def cancel(self):
        logger.debug('Importer cancel')

    def HwpFileFromInputStream(self, inputstream):
        olestorage = self.OLESimpleStorage(inputstream)
        adapter = OleStorageAdapter(olestorage)
        from hwp5.xmlmodel import Hwp5File
        return Hwp5File(adapter)

    def load_hwp5file_into_doc(self, hwp5file, doc, statusindicator=None):
        odtpkg_file = self.hwp5file_convert_to_odtpkg_file(hwp5file)
        logger.debug('hwp to odtpkg completed')

        odtpkg_stream = InputStreamFromFileLike(odtpkg_file)

        odtpkg_storage = self.StorageFromInputStream(odtpkg_stream)

        self.load_odt_from_storage(doc, odtpkg_storage, statusindicator)

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
            from hwp5.hwp5odt import Converter

            if self.haveLibXSLTTransformer():
                xsltproc = self.xsltproc_with_LibXSLTTransformer
            else:
                # TODO Libreoffice 3.2 does not have LibXSLTTransformer yet
                # we use default xsltproc which uses external `xsltproc' program
                from hwp5.tools import xsltproc

            # convert without RelaxNG validation
            convert = Converter(xsltproc)

            # Embed images: see #32 - https://github.com/mete0r/pyhwp/issues/32
            convert(hwp5file, odtpkg, embedimage=True)
        finally:
            odtpkg.close()

        tmpfile2.seek(0)
        return tmpfile2

    def load_odt_from_storage(self, doc, storage, statusindicator=None):
        infoset = self.PropertySet()
        url = ''
        uri = self.createBaseURI(storage, url, '')

        # SfxBaseModel::loadMetadataFromStorage
        # -> sfx2::DocumentMetadataAccess::loadMetadataFromStorage
        # ---> initLoading
        # ---> collectFilesFromStorage
        doc.loadMetadataFromStorage(storage, uri, None)

        # currently hwp5odt does not produce meta.xml
        #emptyargs = (infoset, statusindicator)
        #self.readThroughComponent(storage, doc, 'meta.xml', 'com.sun.star.comp.Writer.XMLOasisMetaImporter', emptyargs, '')

        graphicresolver = self.GraphicObjectResolver(storage)
        objectresolver = None
        lateinitsettings = None
        filterargs = (infoset, statusindicator, graphicresolver, objectresolver, lateinitsettings)
        self.readThroughComponent(storage, doc, 'styles.xml', 'com.sun.star.comp.Writer.XMLOasisStylesImporter', filterargs, '')
        self.readThroughComponent(storage, doc, 'content.xml', 'com.sun.star.comp.Writer.XMLOasisContentImporter', filterargs, '')

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


@implementation('pyhwp.TestJob', 'com.sun.star.task.XJobExecutor')
class TestJob(unohelper.Base, XJobExecutor):
    def __init__(self, ctx):
        self.ctx = ctx

    def trigger(self, args):
        logger.debug('testjob %s', args)

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
        yield defaultTestLoader.loadTestsFromTestCase(OleStorageAdapterTest)
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
            logger.info('Paragraph %s', paragraph_ix)
            logger.debug('%s', paragraph)

            services = paragraph.SupportedServiceNames
            if 'com.sun.star.text.Paragraph' in services:
                portions = xenumeration_list(paragraph.createEnumeration())
                for portion_ix, portion in enumerate(portions):
                    logger.info('Portion %s: %s', portion_ix,
                                 portion.TextPortionType)
                    if portion.TextPortionType == 'Text':
                        logger.info('- %s', portion.getString())
                    elif portion.TextPortionType == 'Frame':
                        logger.debug('%s', portion)
                        textcontent_name = 'com.sun.star.text.TextContent'
                        en = portion.createContentEnumeration(textcontent_name)
                        contents = xenumeration_list(en)
                        for content in contents:
                            logger.debug('content: %s', content)
                            content_services = content.SupportedServiceNames
                            if ('com.sun.star.drawing.GraphicObjectShape' in
                                content_services):
                                logger.info('graphic url: %s',
                                             content.GraphicURL)
                                logger.info('graphic stream url: %s',
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
        self.assertEquals('image/x-vclgraphic', contents[0].Bitmap.MimeType)
        #self.assertEquals('vnd.sun.star.Package:bindata/BIN0003.png',
        #                  contents[0].GraphicStreamURL)

        graphics = doc.getGraphicObjects()
        graphics = xenumeration_list(graphics.createEnumeration())
        logger.debug('graphic: %s', graphics)

        frames = doc.getTextFrames()
        frames = xenumeration_list(frames.createEnumeration())
        logger.debug('frames: %s', frames)


class OleStorageAdapterTest(TestCase, FacMixin):

    context = uno.getComponentContext()

    def get_adapter(self):
        f = file('fixtures/sample-5017.hwp', 'r')
        inputstream = InputStreamFromFileLike(f)
        oless = self.OLESimpleStorage(inputstream)
        return OleStorageAdapter(oless)

    def test_iter(self):
        adapter = self.get_adapter()

        self.assertTrue('FileHeader' in adapter)
        self.assertTrue('DocInfo' in adapter)
        self.assertTrue('BodyText' in adapter)

    def test_getitem(self):
        adapter = self.get_adapter()

        bodytext = adapter['BodyText']
        self.assertTrue('Section0' in bodytext)

        from hwp5.filestructure import HwpFileHeader
        from hwp5.filestructure import HWP5_SIGNATURE

        fileheader = adapter['FileHeader']
        fileheader = HwpFileHeader(fileheader)
        self.assertEquals((5, 0, 1, 7), fileheader.version)
        self.assertEquals(HWP5_SIGNATURE, fileheader.signature)

        # reopen (just being careful)
        fileheader = adapter['FileHeader']
        fileheader = HwpFileHeader(fileheader)
        self.assertEquals((5, 0, 1, 7), fileheader.version)
        self.assertEquals(HWP5_SIGNATURE, fileheader.signature)
