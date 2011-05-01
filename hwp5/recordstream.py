try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from .tagids import HWPTAG_BEGIN, tagnames
from .dataio import UINT32, Eof
from . import dataio

class Record:
    def __init__(self, seqno, tagid, level, bytes):
        self.seqno = seqno
        self.tagid = tagid
        self.level = level
        self.bytes = bytes
        self.subrecs = []
        self.model = None
    def __repr__(self):
        return '<Record %d %s level=%d size=%d>'%(
                self.seqno, tagnames.get(self.tagid, 'HWPTAG_BEGIN+%d'%(self.tagid - HWPTAG_BEGIN)),
                self.level, len(self.bytes))
    def bytestream(self):
        return StringIO(self.bytes)

def decode_record_header(f):
    try:
        # TagID, Level, Size
        rechdr = UINT32.parse(f)
        tagid = rechdr & 0x3ff
        level = (rechdr >> 10) & 0x3ff
        size = (rechdr >> 20) & 0xfff
        if size == 0xfff:
            size = UINT32.parse(f)
        return (tagid, level, size)
    except Eof:
        return None

def decode_record_stream(f):
    seqno = 0
    while True:
        rechdr = decode_record_header(f)
        if rechdr is None:
            return
        tagid, level, size = rechdr
        bytes = dataio.readn(f, size)
        yield Record(seqno, tagid, level, bytes)
        seqno += 1
