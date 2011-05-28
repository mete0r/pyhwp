import os.path
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import zlib
from OleFileIO_PL import OleFileIO

from .utils import cached_property
from .dataio import UINT32, BYTES, VERSION
from . import dataio

class FileHeader(object):
    Flags = dataio.Flags(UINT32, (
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
        ))
    def attributes(cls, context):
        yield BYTES(32), 'signature'
        yield VERSION, 'version'
        yield cls.Flags, 'flags'
        yield BYTES(216), 'reserved'
    attributes = classmethod(attributes)

    def parse(cls, f):
        from .models import parse_model_attributes
        return parse_model_attributes(cls, dict(), None, f)
    parse = classmethod(parse)


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

    def open_fileheader(self):
        return self.openstream('FileHeader')

    def parse_fileheader(self):
        type, attributes = FileHeader.parse(self.open_fileheader())
        fileheader = FileHeader()
        fileheader.__dict__.update((name, type(attributes.get(name))) for type, name in FileHeader.attributes(dict()))
        return fileheader
    fileheader = cached_property(parse_fileheader)

    def preview_text(self, charset='utf-8'):
        import locale
        return recode(self.openstream('PrvText'), 'utf-16le', charset)

    def preview_image(self):
        return self.openstream('PrvImage')

    def summaryinfo(self):
        return self.openstream('\005HwpSummaryInformation')

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

    def bindata(self, name):
        try:
            strm = self.openstream('BinData/%s'%name)
        except IOError:
            raise KeyError(name)
        if self.fileheader.flags.compressed:
            strm = StringIO(zlib.decompress(strm.read(), -15))
        return strm

def pop_arg(args, name):
    try:
        return args.pop(0)
    except IndexError:
        raise Exception('%s is required'%name)

def main():
    from optparse import OptionParser as OP
    op = OP(usage='usage: %prog [options] filename <stream-specifier>')
    options, args = op.parse_args()

    filename = pop_arg(args, 'filename')
    file = File(filename)

    if len(args) == 0:
        op.print_help()
        print ''
        print 'Available <stream-specifier>s:'
        print ''
        print 'DECODED STREAMS'
        print '---------------'
        print 'bindata <filename> : BIN/<filename> (uncompressed)'
        print 'docinfo : DocInfo (uncompressed, record stream)'
        print 'bodytext <index> : BodyText/Section<index> (uncompressed, record stream)'
        print 'preview_image'
        print 'preview_text [charset] : (default charset=utf-8)'
        print ''
        print 'RAW STREAMS'
        print '-----------'
        for name in file.list_streams():
            print name
        return 0

    stream = pop_arg(args, 'stream')
    try:
        method = getattr(file, stream)
    except AttributeError:
        stream = file.openstream(stream)
    else:
        stream = method(*args)
    import sys
    sys.stdout.write(stream.read())
