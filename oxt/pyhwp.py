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

    def OLESimpleStorage(self, *args):
        return self.context.ServiceManager.createInstanceWithArguments('com.sun.star.embed.OLESimpleStorage', args)

    def SequenceInputStream(self, s):
        return self.context.ServiceManager.createInstanceWithArguments('com.sun.star.io.SequenceInputStream',
                (uno.ByteSequence(s),) )

    def saxParser(self):
        return self.context.ServiceManager.createInstance('com.sun.star.xml.sax.Parser')

    def WriterXMLImporter(self):
        return self.context.ServiceManager.createInstance('com.sun.star.comp.Writer.XMLImporter')

    def parse_fodt_stream_into_doc(self, stream, doc):
        from com.sun.star.xml.sax import InputSource
        inputsource = InputSource()
        inputsource.aInputStream = stream
        inputsource.sEncoding = 'utf-8'

        dochandler = self.WriterXMLImporter()
        dochandler.setTargetDocument(doc)

        parser = self.saxParser()
        parser.setDocumentHandler(dochandler)
        parser.parseStream(inputsource)

class File_Stream(object):
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

    def close(self):
        if hasattr(stream, 'closeInput'):
            self.stream.closeInput()

class OleFileIO_from_OLESimpleStorage(object):
    def __init__(self, storage):
        self.storage = storage

    def exists(self, name):
        return self.storage.hasByName(name)

    def openstream(self, name):
        from com.sun.star.container import NoSuchElementException
        try:
            stream = self.storage.getByName(name)
        except NoSuchElementException:
            return None
        else:
            return File_Stream(stream)

def unofy_value(value):
    if isinstance(value, dict):
        value = dict_to_propseq(value)
    elif isinstance(value, list):
        value = tuple(value)
    return value

def dict_to_propseq(d):
    from com.sun.star.beans import PropertyValue
    DIRECT_VALUE = uno.Enum('com.sun.star.beans.PropertyState', 'DIRECT_VALUE')
    return tuple(PropertyValue(k, 0, unofy_value(v), DIRECT_VALUE) for k, v in d.iteritems())

def propseq_to_dict(propvalues):
    return dict((p.Name, p.Value) for p in propvalues)

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
        olestorage = self.fac.OLESimpleStorage(inputstream)
        olefile = OleFileIO_from_OLESimpleStorage(olestorage)
        from hwp5.filestructure import File
        hwpfile = File(olefile)

        xmldata = '''<?xml version="1.0" encoding="utf-8"?>
<office:document xmlns:office="http://openoffice.org/2000/office"
    xmlns:text="http://openoffice.org/2000/text"
    office:class="text">
    <office:body>
        <text:p>Hello world!</text:p>
    </office:body>
</office:document>
'''
        fodt_stream = self.fac.SequenceInputStream(xmldata)
        self.fac.parse_fodt_stream_into_doc(fodt_stream, self.target)
        return True

    def cancel(self):
        logging.debug('Importer cancel')

@implementation('pyhwp.HelloWorld', 'com.sun.star.task.Job')
class HelloWorldJob(unohelper.Base, XJobExecutor):
    def __init__(self, ctx):
        self.ctx = ctx

    @log_exception
    def trigger(self, args):

        logging.debug('args: '+str(args))

        packman = self.ctx.getValueByName('/singletons/com.sun.star.deployment.PackageInformationProvider')
        oxt_location = packman.getPackageLocation('pyhwp')
        logging.debug('location: %s', oxt_location)
        oxt_path = uno.fileUrlToSystemPath(oxt_location)
        logging.debug('oxt path: %s', oxt_path)

        desktop = self.ctx.ServiceManager.createInstanceWithContext(
                'com.sun.star.frame.Desktop', self.ctx)

        model = desktop.getCurrentComponent()

        text = model.Text

        cursor = text.createTextCursor()

        import sys

        for path in sys.path:
            text.insertString(cursor, path+'\n', False)

        import hwp5
        import pkg_resources
        xslpath = pkg_resources.resource_filename('hwp5', 'xsl/odt-content.xsl')
        logging.debug('odt-content.xsl: %s', xslpath)

        text.insertString(cursor, 'hello world', False)


