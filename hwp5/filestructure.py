import os.path
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import zlib
from OleFileIO_PL import OleFileIO

from .utils import cached_property
from .dataio import fixup_parse, UINT32, BYTES, VERSION
from . import dataio

class FileHeader:
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
    def getFields(self):
        yield BYTES(32), 'signature'
        yield VERSION, 'version'
        yield self.Flags, 'flags'
        yield BYTES(216), 'reserved'
fixup_parse(FileHeader)

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

    def open_previewtext(self):
        return self.openstream('PrvText')

    def open_previewimage(self):
        return self.openstream('PrvImage')

    def open_summaryinfo(self):
        return self.openstream('\005HwpSummaryInformation')

    def open_fileheader(self):
        return self.openstream('FileHeader')

    def read_previewtext(self):
        return self.open_previewtext().read().decode('utf-16')
    previewtext = cached_property(read_previewtext)

    def read_previewimage(self):
        return self.open_previewimage().read()
    previewimage = cached_property(read_previewimage)

    def read_summaryinfo(self):
        return self.open_summaryinfo().read()
    summaryinfo = cached_property(read_summaryinfo)

    def parse_fileheader(self):
        return FileHeader.parse(self.open_fileheader())
    fileheader = cached_property(parse_fileheader)

    def open_docinfo(self):
        strm = self.openstream('DocInfo')
        if self.fileheader.flags.compressed:
            strm = StringIO(zlib.decompress(strm.read(), -15)) # without gzip header
        return strm

    def decode_docinfo(self):
        return decode_record_stream(self.open_docinfo())

    def open_bodytext_section(self, idx):
        try:
            sec = self.openstream('BodyText/Section'+str(idx))
        except IOError:
            raise IndexError(idx)
        if self.fileheader.flags.compressed:
            sec = StringIO(zlib.decompress(sec.read(), -15))
        return sec

    def decode_bodytext_section(self, idx):
        return decode_record_stream(self.open_bodytext_section(idx))

    def open_bindata(self, name):
        try:
            strm = self.openstream('BinData/%s'%name)
        except IOError:
            raise KeyError(name)
        if self.fileheader.flags.compressed:
            strm = StringIO(zlib.decompress(strm.read(), -15))
        return strm

    def read_bindata(self, name):
        return self.open_bindata(name).read()
