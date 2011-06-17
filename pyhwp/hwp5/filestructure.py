import os.path
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import zlib
from OleFileIO_PL import OleFileIO

from .utils import cached_property
from .dataio import INT32, UINT32, UINT16, Flags, Struct, ARRAY, N_ARRAY
from . import dataio

class BYTES(type):
    def __new__(mcs, size):
        return type.__new__(mcs, 'BYTES%d'%size, (str,), dict(size=size))
    def __init__(self, size):
        return type.__init__(self, None, None, None)
    def read(self, f, context=None):
        if self.size < 0:
            return f.read()
        else:
            return f.read(self.size)

class VERSION(tuple):
    def read(cls, f, context=None):
        version = f.read(4)
        return (ord(version[3]), ord(version[2]), ord(version[1]), ord(version[0]))
    read = classmethod(read)

class FileHeader(Struct):
    Flags = Flags(UINT32,
        0, 'compressed',
        1, 'password',
        2, 'distributable',
        3, 'script',
        4, 'drm',
        5, 'xmltemplate_storage',
        6, 'history',
        7, 'cert_signed',
        8, 'cert_encrypted',
        9, 'cert_signature_extra',
        10, 'cert_drm',
        11, 'ccl',
        )
    def attributes(cls, context):
        yield BYTES(32), 'signature'
        yield VERSION, 'version'
        yield cls.Flags, 'flags'
        yield BYTES(216), 'reserved'
    attributes = classmethod(attributes)

class TextField(unicode):
    def read(cls, f, context=None):
        unk0 = UINT32.read(f, None) # 1f
        assert unk0 == 0x1f
        size = UINT32.read(f, None)
        if size > 0:
            data = f.read(2*(size))
        else:
            data = ''
        if size & 1:
            f.read(2)
        return data.decode('utf-16le', 'replace')
    read = classmethod(read)

class SummaryInfo(Struct):
    def attributes(cls, context):
        if context['version'] < (5, 0, 1, 0):
            yield ARRAY(UINT32, 0230/4), '_unk0'
        else:
            yield ARRAY(UINT32, 0250/4), '_unk0'
        yield TextField, 'title'
        yield TextField, 'subject'
        yield TextField, 'author'
        yield TextField, 'datetime'
        yield TextField, 'keywords'
        yield TextField, 'etc'
        yield TextField, 'hidden_username'
        yield TextField, 'hidden_progversion'
        yield ARRAY(ARRAY(UINT16, 6), 3), '_unk1'
        #yield ARRAY(N_ARRAY(UINT32, UINT32), 2), '_unk2'
    attributes = classmethod(attributes)


def recode(backend_stream, backend_encoding, frontend_encoding, errors='strict'):
    import codecs
    enc = codecs.getencoder(frontend_encoding)
    dec = codecs.getdecoder(frontend_encoding)
    rd = codecs.getreader(backend_encoding)
    wr = codecs.getwriter(backend_encoding)
    return codecs.StreamRecoder(backend_stream, enc, dec, rd, wr, errors)

class File(OleFileIO):

    def list_streams(self):
        for e in self.listdir():
            yield os.path.join(*e)

    def list_bodytext_sections(self):
        l = []
        for name in self.list_streams():
            prefix = 'BodyText/Section'
            if name.startswith(prefix):
                l.append( int(name[len(prefix):]) )
        l.sort()
        return l

    def list_bindata(self):
        for name in self.list_streams():
            prefix = 'BinData/'
            if name.startswith(prefix):
                yield name[len(prefix):]

    def _fileheader(self):
        return self.openstream('FileHeader')

    def fileheader(self):
        attributes = FileHeader.read(self._fileheader())
        fileheader = FileHeader()
        fileheader.__dict__.update((name, type(attributes.get(name))) for type, name in FileHeader.attributes(dict()))
        return fileheader
    fileheader = cached_property(fileheader)

    def _summaryinfo(self):
        return self.openstream('\005HwpSummaryInformation')

    def summaryinfo(self):
        f = self._summaryinfo()
        context = dict(version=self.fileheader.version)
        summaryinfo = SummaryInfo.read(f, context)
        #print '#### %o'%f.tell()
        return summaryinfo
    summaryinfo = property(summaryinfo)

    def preview_text(self):
        charset = 'utf-8'
        return recode(self.openstream('PrvText'), 'utf-16le', charset)

    def preview_image(self):
        return self.openstream('PrvImage')

    def docinfo(self):
        strm = self.openstream('DocInfo')
        if self.fileheader.flags.compressed:
            strm = StringIO(zlib.decompress(strm.read(), -15)) # without gzip header
        return strm

    def bodytext(self, idx):
        try:
            sec = self.openstream('BodyText/Section'+str(idx))
        except IOError:
            raise IndexError(idx)
        if self.fileheader.flags.compressed:
            sec = StringIO(zlib.decompress(sec.read(), -15))
        return sec

    def viewtext(self, idx):
        try:
            sec = self.openstream('ViewText/Section'+str(idx))
        except IOError:
            raise IndexError(idx)
        return sec

    def viewtext_tail(self, idx):
        f = self.viewtext(idx)
        f.seek(4+256)
        return f

    def bindata(self, name):
        try:
            strm = self.openstream('BinData/%s'%name)
        except IOError:
            raise KeyError(name)
        if self.fileheader.flags.compressed:
            strm = StringIO(zlib.decompress(strm.read(), -15))
        return strm

    def script(self, name):
        try:
            strm = self.openstream('Scripts/%s'%name)
        except IOError:
            raise KeyError(name)
        if self.fileheader.flags.compressed:
            return StringIO(zlib.decompress(strm.read(), -15))
        return strm

    def pseudostream(self, name):
        args = name.split('/', 1)
        name = args.pop(0)
        pseudostream = getattr(self, name, None)
        if pseudostream:
            return pseudostream(*args)

def main():
    from ._scriptutils import OptionParser, args_pop
    op = OptionParser(usage='usage: %prog [options] filename <stream>')
    options, args = op.parse_args()

    filename = args_pop(args, 'filename')
    file = File(filename)

    if len(args) == 0:
        print 'FileHeader'
        print '----------'
        print 'signature:%s'%file.fileheader.signature
        print '  version: %d.%d.%d.%d'%file.fileheader.version
        print '    flags: 0x%x'%file.fileheader.flags
        for k, v in FileHeader.Flags.dictvalue(file.fileheader.flags).iteritems():
            print '%20s: %d'%(k, v)
        print ''
        print 'Pseudo streams'
        print '--------------'
        print '          _fileheader : synonym of FileHeader'
        print '         _summaryinfo : synonym of \\x05HwpSummaryInformation'
        print '         preview_text : PrvText (UTF-8)'
        print '        preview_image : synonym of PrvImage'
        print '              docinfo : DocInfo (uncompressed, record stream)'
        print '     bodytext/<index> : BodyText/Section<index> (uncompressed, record stream)'
        print '   bindata/<filename> : BIN/<filename> (uncompressed)'
        print '    script/<filename> : Scripts/<filename> (uncompressed)'
        print '     viewtext/<index> : ViewText/Section<index> (a record)'
        print 'viewtext_tail/<index> : tail part of ViewText/Section<index> (block data)'
        print ''
        print 'Raw streams'
        print '-----------'
        for name in file.list_streams():
            print name.encode('string_escape')
        print ''
        print 'SummaryInfo'
        print '-----------'
        for k, v in file.summaryinfo.iteritems():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            print '%20s: %s'%(k, v)
        return 0

    streamname = args_pop(args, '<stream>')
    if streamname == 'list':
        streamname = args_pop(args, 'bindata | bodytext')
        if streamname == 'bindata':
            for name in file.list_bindata():
                print name
        elif streamname == 'bodytext':
            for idx in file.list_bodytext_sections():
                print 'bodytext/%d'%idx
        return 0
    stream = file.pseudostream(streamname)
    if not stream:
        stream = file.openstream(streamname)
    import sys
    sys.stdout.write(stream.read())
