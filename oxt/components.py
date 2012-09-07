# -*- coding: utf-8 -*-
#
#                   GNU AFFERO GENERAL PUBLIC LICENSE
#                      Version 3, 19 November 2007
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
import logging
import os


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


try:
    import uno
    import unohelper
    import unokit
    from unokit.util import propseq_to_dict
    from unokit.util import dict_to_propseq
    from unokit.util import xenumeration_list
    from unokit.adapters import InputStreamFromFileLike

    from com.sun.star.lang import XInitialization
    from com.sun.star.document import XFilter, XImporter, XExtendedFilterDetection
    from com.sun.star.task import XJobExecutor

    def log_exception(f):
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception, e:
                logger.exception(e)
                raise
        return wrapper

    g_ImplementationHelper = unohelper.ImplementationHelper()

    def implementation(component_name, *services):
        def decorator(cls):
            g_ImplementationHelper.addImplementation(cls, component_name, services)
            return cls
        return decorator


    @implementation('hwp5.Detector', 'com.sun.star.document.ExtendedTypeDetection')
    class Detector(unokit.Base, XExtendedFilterDetection):

        @log_exception
        @unokit.component_context
        def detect(self, mediadesc):
            from hwp5_uno import typedetect

            logger.info('hwp5.Detector detect()')

            desc = propseq_to_dict(mediadesc)
            for k, v in desc.items():
                logger.debug('\t%s: %s', k, v)

            inputstream = desc['InputStream']

            typename = typedetect(inputstream)

            logger.info('hwp5.Detector: %s detected.', typename)
            return typename, mediadesc


    @implementation('hwp5.Importer', 'com.sun.star.document.ImportFilter')
    class Importer(unokit.Base, XInitialization, XFilter, XImporter):

        @log_exception
        @unokit.component_context
        def initialize(self, args):
            logger.debug('Importer initialize: %s', args)

        @log_exception
        @unokit.component_context
        def setTargetDocument(self, target):
            logger.debug('Importer setTargetDocument: %s', target)
            self.target = target

        @log_exception
        @unokit.component_context
        def filter(self, mediadesc):
            from hwp5.dataio import ParseError
            from hwp5_uno import HwpFileFromInputStream
            from hwp5_uno import load_hwp5file_into_doc

            logger.debug('Importer filter')
            desc = propseq_to_dict(mediadesc)

            logger.debug('mediadesc: %s', str(desc.keys()))
            for k, v in desc.iteritems():
                logger.debug('%s: %s', k, str(v))

            statusindicator = desc.get('StatusIndicator')

            inputstream = desc['InputStream']
            hwpfile = HwpFileFromInputStream(inputstream)
            try:
                load_hwp5file_into_doc(hwpfile, self.target, statusindicator)
            except ParseError, e:
                e.print_to_logger(logger)
                return False
            except Exception, e:
                logger.exception(e)
                return False
            else:
                return True

        @unokit.component_context
        def cancel(self):
            logger.debug('Importer cancel')


    @implementation('hwp5.TestJob')
    class TestJob(unokit.Base, XJobExecutor):

        @unokit.component_context
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
            yield defaultTestLoader.loadTestsFromTestCase(DetectorTest)
            yield defaultTestLoader.loadTestsFromTestCase(ImporterTest)
            from hwp5_uno.tests import test_hwp5_uno
            yield defaultTestLoader.loadTestsFromModule(test_hwp5_uno)
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
            detector = svm.createInstanceWithContext('hwp5.Detector', context)
            typename, mediadesc2 = detector.detect(mediadesc)
            self.assertEquals('hwp5', typename)

    class ImporterTest(TestCase):

        def test_filter(self):
            context = uno.getComponentContext()
            f = file('fixtures/sample-5017.hwp', 'r')
            stream = InputStreamFromFileLike(f)
            mediadesc = dict_to_propseq(dict(InputStream=stream))

            svm = context.ServiceManager
            importer = svm.createInstanceWithContext('hwp5.Importer', context)
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
except Exception, e:
    logger.exception(e)
    raise
