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

    def StorageFromStream(self, stream):
        return self.storage_factory.createInstanceWithArguments( (stream, 4) ) # com.sun.star.embed.ElementModes.READ

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

    def load_odt_from_storage(self, doc, storage, statusindicator=None):
        infoset = self.PropertySet()
        url = ''
        uri = self.createBaseURI(storage, url, '')
        doc.loadMetadataFromStorage(storage, uri, None)
        #self.readThroughComponent(storage, doc, 'meta.xml', 'com.sun.star.comp.Writer.XMLOasisMetaImporter', (infoset, None), '')
        graphicresolver = None
        objectresolver = None
        lateinitsettings = None
        filterargs = (infoset, statusindicator, graphicresolver, objectresolver, lateinitsettings)
        self.readThroughComponent(storage, doc, 'styles.xml', 'com.sun.star.comp.Writer.XMLOasisStylesImporter', filterargs, '')
        self.readThroughComponent(storage, doc, 'content.xml', 'com.sun.star.comp.Writer.XMLOasisContentImporter', filterargs, '')

    def saxParser(self):
        return self.context.ServiceManager.createInstance('com.sun.star.xml.sax.Parser')

    def WriterXMLImporter(self):
        return self.context.ServiceManager.createInstance('com.sun.star.comp.Writer.XMLImporter')

    def WriterXMLContentImporter(self):
        return self.context.ServiceManager.createInstance('com.sun.star.comp.Writer.XMLContentImporter')

    def TempFile(self):
        return self.context.ServiceManager.createInstance('com.sun.star.io.TempFile')

    def HwpFileFromInputStream(self, inputstream):
        olestorage = self.OLESimpleStorage(inputstream)
        olefile = OleFileIO_from_OLESimpleStorage(olestorage)
        from hwp5.filestructure import File
        return File(olefile)

    def TempStorage(self):
        tempfile = self.TempFile()
        return self.StorageFromStream(self.TempFile())

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
            from hwp5.hwp5odt import hwp5file_convert_to_odtpkg
            hwp5file_convert_to_odtpkg(hwp5file, odtpkg)
        finally:
            odtpkg.close()

        tmpfile2.seek(0)
        return tmpfile2

    def PropertySequence(self, **kwargs):
        return dict_to_propseq(kwargs)

    def flatxml(self, hwp5file):
        import tempfile
        from hwp5.hwp5odt import generate_hwp5xml
        from hwp5.hwp5odt import xsltproc, xsl

        hwp5xml_file = tempfile.TemporaryFile()
        generate_hwp5xml(hwp5xml_file, hwp5file)
        return hwp5xml_file

    def hwpfile_to_doc(self, hwpfile, doc):
        import tempfile
        from hwp5.hwp5odt import generate_hwp5xml
        from hwp5.hwp5odt import xsltproc, xsl

        hwpxml = tempfile.TemporaryFile()
        try:
            generate_hwp5xml(hwpxml, hwpfile)

            try:
                hwpxml.seek(0)
                content = tempfile.TemporaryFile()
                xsltproc(xsl.content)(hwpxml, content)

                content.seek(0)
                inputstream = InputStreamFromFileLike(content)
                self.parse_odt_content_stream_into_doc(inputstream, doc)
            finally:
                content.close()
        finally:
            hwpxml.close()

    def xslted_stream(self, xsltproc, xsl_filename, infile):
        transform = xsltproc(xsl_filename)

        import os
        i, o = os.pipe()
        pipein = os.fdopen(i, 'r')
        pipeout = os.fdopen(o, 'w')
        def run():
            logging.debug('XSLT starts...')
            transform(infile, pipeout)
            logging.debug('XSLT end')
            pipeout.close()
            logging.debug('XSLT pipeout closed')

        def detached_run(run):
            import threading
            t = threading.Thread(target=run)
            t.daemon = True
            logging.debug('XSLT thread starting...')
            t.start()

        detached_run(log_exception(run))
        return InputStreamFromFileLike(pipein)

    def hwp5xml_odt_content_stream(self, hwp5xml_file):
        from hwp5.hwp5odt import xsltproc, xsl
        return self.xslted_stream(xsltproc, xsl.content, hwp5xml_file)

    def parse_stream_into_doc(self, stream, dochandler, doc):
        from com.sun.star.xml.sax import InputSource
        inputsource = InputSource()
        inputsource.aInputStream = stream
        inputsource.sEncoding = 'utf-8'

        dochandler.setTargetDocument(doc)

        parser = self.saxParser()
        parser.setDocumentHandler(dochandler)
        parser.parseStream(inputsource)

    def parse_odt_content_stream_into_doc(self, stream, doc):
        return self.parse_stream_into_doc(stream, self.WriterXMLContentImporter(), doc)

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

    def SAXParser(self, dochandler):
        parser = self.saxParser()
        parser.setDocumentHandler(dochandler)
        def consume(stream):
            from com.sun.star.xml.sax import InputSource
            inputsource = InputSource()
            inputsource.aInputStream = stream
            inputsource.sEncoding = 'utf-8'
            parser.parseStream(inputsource)
        return consume

    def FlatXMLImporter(self, doc):
        handler = self.WriterXMLImporter()
        handler.setTargetDocument(doc)
        return self.SAXParser(handler)

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
        from com.sun.star.container import NoSuchElementException
        path_segments = path.split('/')
        stream = container_find_element(self.storage, path_segments)
        if stream is not None:
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

from com.sun.star.io import XInputStream, XSeekable
class InputStreamFromFileLike(unohelper.Base, XInputStream, XSeekable):
    def __init__(self, f):
        self.f = f

    def readBytes(self, aData, nBytesToRead):
        logging.debug('InputStream.readBytes(%d)', nBytesToRead)
        data = self.f.read(nBytesToRead)
        return len(data), uno.ByteSequence(data)

    readSomeBytes = readBytes

    def skipBytes(self, nBytesToSkip):
        logging.debug('InputStream.skipBytes(%d)', nBytesToSkip)
        data = self.f.read(nBytesToSkip)

    def available(self):
        logging.debug('InputStream.available()')
        return 0

    def closeInput(self):
        logging.debug('InputStream.close()')
        self.f.close()

    def seek(self, location):
        logging.debug('InputStream.seek(%d)', location)
        self.f.seek(location)

    def getPosition(self):
        pos = self.f.tell()
        logging.debug('InputStream.getPosition(): %d', pos)
        return pos

    def getLength(self):
        pos = self.f.tell()
        try:
            self.f.seek(0, 2)
            length = self.f.tell()
            logging.debug('InputStream.getLength(): %d', length)
            return length
        finally:
            self.f.seek(pos)

class ODTPackage(object):
    def __init__(self, storage):
        self.storage = storage

    def insert_stream(self, f, path, media_type):
        print path, media_type
        storage = self.storage
        WRITE = 4 # = com.sun.star.embed.ElementModes.WRITE

        path_segments = path.split('/')
        intermediates = path_segments[:-1]
        name = path_segments[-1]
        for segment in intermediates:
            storage = storage.openStorageElement(segment, WRITE)
        stream = storage.openStreamElement(name, WRITE)
        File_Stream(stream).write(f.read())

    def close(self):
        self.storage.commit()

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

        odtpkg_file = self.fac.hwp5file_convert_to_odtpkg_file(hwpfile)
        logging.debug('hwp to odtpkg completed')

        #odtpkg_stream = InputStreamFromFileLike(odtpkg_file)

        temp = self.fac.TempFile()
        File_Stream(temp).write(odtpkg_file.read())
        temp.seek(0)
        odtpkg_stream = temp

        odtpkg_storage = self.fac.StorageFromInputStream(odtpkg_stream)

        self.fac.load_odt_from_storage(self.target, odtpkg_storage, statusindicator)
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


