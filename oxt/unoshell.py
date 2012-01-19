# -*- coding: utf-8 -*-
import uno
localContext = uno.getComponentContext()
resolver = localContext.ServiceManager.createInstanceWithContext(
        'com.sun.star.bridge.UnoUrlResolver', localContext)
context = resolver.resolve('uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext')

from pyhwp import OleFileIO_from_OLESimpleStorage, File_Stream
from pyhwp import propseq_to_dict, dict_to_propseq
import pyhwp

class Fac(pyhwp.Fac):

    @property
    def desktop(self):
        return context.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', context)

    @property
    def desktop_model(self):
        return self.desktop.getCurrentComponent()

    @property
    def fileaccess(self):
        return context.ServiceManager.createInstance('com.sun.star.ucb.SimpleFileAccess')

    @property
    def typedetection(self):
        return context.ServiceManager.createInstanceWithContext('com.sun.star.document.TypeDetection', context)

    @property
    def typedetect(self):
        return TypeDetect(self.typedetection)

    @property
    def filterfac(self):
        return context.ServiceManager.createInstance('com.sun.star.document.FilterFactory')

    def open_filestream(self, path):
        import os.path
        url = uno.systemPathToFileUrl(os.path.realpath(path))
        return self.fileaccess.openFileRead(url)

    def OleFileIO(self, name):
        f = self.open_filestream(name)
        storage = self.OLESimpleStorage(f, True)
        return OleFileIO_from_OLESimpleStorage(storage)

    def open(self, path):
        fin = self.open_filestream(path)
        return File_Stream(fin)

    def HwpFileFromPath(self, path):
        inputstream = self.open_filestream(path)
        return self.HwpFileFromInputStream(inputstream)

    def MediaDescriptor(self, path):
        url = fileurl(path)
        return dict_to_propseq(dict(URL=url))

    def mktmpfile(self):
        return File_Stream(self.TempFile())

    def hwp5file_convert_to_odtpkg(self, hwp5file, path):
        tmpfile2 = self.hwp5file_convert_to_odtpkg_file(hwp5file)
        try:
            data = tmpfile2.read()
            print len(data)
            f = file(path, 'w')
            try:
                f.write(data)
            finally:
                f.close()
        finally:
            tmpfile2.close()

    def HwpXmlFileFromPath(self, path):
        inputstream = self.HwpXmlInputStreamFromPath(path)
        return File_Stream(inputstream)

    def HwpXmlInputStreamFromPath(self, path):
        hwpfile = self.HwpFileFromPath(path)

        tempfile = self.TempFile()
        tmpfile = File_Stream(tempfile)

        from hwp5.hwp5odt import generate_hwp5xml
        generate_hwp5xml(tmpfile, hwpfile)
        tmpfile.seek(0)
        return tempfile

    @property
    def hwpxmlfile(self):
        return self.HwpXmlFileFromPath('../samples/5017.hwp')

    @property
    def libXSLTTransformer_styles(self):
        from hwp5.hwp5odt import xsl
        return self.xsltproc(xsl.styles)

    @property
    def libXSLTTransformer_content(self):
        from hwp5.hwp5odt import xsl
        return self.xsltproc(xsl.content)

class TypeDetect(object):
    def __init__(self, typedetection):
        self.typedetection = typedetection

    @property
    def types(self):
        for name in self.typedetection.getElementNames():
            typ = propseq_to_dict(self.typedetection.getByName(name))
            if 'UINames' in typ:
                typ['UINames'] = propseq_to_dict(typ['UINames'])
            yield typ

    @property
    def type_names(self):
        names = list(t['Name'] for t in self.types)
        names.sort()
        return names

    def types_for_extension(self, ext):
        for t in self.types:
            extensions = t['Extensions']
            if isinstance(extensions, tuple) and ext in extensions:
                yield t

def fileurl(path):
    import os.path
    return uno.systemPathToFileUrl(os.path.realpath(path))

__import__('code').interact(banner='unoshell', local=dict(uno=uno,
                                                          context=context,
                                                          fileurl=fileurl,
                                                          fac=Fac(context)))
