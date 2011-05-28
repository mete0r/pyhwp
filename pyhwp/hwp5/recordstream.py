try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from .tagids import HWPTAG_BEGIN, tagnames
from .dataio import UINT32, Eof
from . import dataio
from .utils import cached_property

class Record:

    def __init__(self, tagid, level, payload, seqno=None, streamid=None, filename=None):
        self.filename = filename
        self.streamid = streamid
        self.seqno = seqno
        self.tagid = tagid
        self.level = level
        self.payload = payload
        self.parent = None
        self.sister = None

    def tag(self):
        return tagnames.get(self.tagid, 'HWPTAG%d'%(self.tagid - HWPTAG_BEGIN))
    tag = cached_property(tag)

    def tag_verbose(self):
        return tagnames.get(self.tagid, '<UNKNOWN>')+('(=0x%x, HWPTAG_BEGIN+%d)'%(self.tagid, self.tagid-HWPTAG_BEGIN))
    tag_verbose = cached_property(tag_verbose)

    def size(self):
        return len(self.payload)
    size = property(size)

    def id(self):
        return (self.filename, self.streamid, self.seqno)
    id = property(id)

    def __str__(self):
        if self.parent is None:
            parent = None
        else:
            parent = self.parent.seqno
        if self.sister is None:
            sister = None
        else:
            sister = self.sister.seqno
        return '<Record:%d %s(0x%x) level=%d size=%d parent=%s sister=%s (%s:%s)>'%(
                self.seqno, self.tag, self.tagid,
                self.level, self.size, parent, sister,
                self.filename, self.streamid,
                )

    def bytestream(self):
        return StringIO(self.payload)

def decode_record_header(f):
    try:
        # TagID, Level, Size
        rechdr = UINT32.read(f)
        tagid = rechdr & 0x3ff
        level = (rechdr >> 10) & 0x3ff
        size = (rechdr >> 20) & 0xfff
        if size == 0xfff:
            size = UINT32.read(f)
        return (tagid, level, size)
    except Eof:
        return None

def encode_record_header(rec):
    import struct
    size = len(rec.payload)
    level = rec.level
    tagid = rec.tagid
    if size < 0xfff:
        hdr = (size << 20) | (level << 10) | tagid
        return struct.pack('<I', hdr)
    else:
        hdr = (0xfff << 20) | (level << 10) | tagid
        return struct.pack('<II', hdr, size)

def read_records(f, streamid, filename='<unknown>'):
    seqno = 0
    while True:
        rechdr = decode_record_header(f)
        if rechdr is None:
            return
        tagid, level, size = rechdr
        payload = dataio.readn(f, size)
        yield Record(tagid, level, payload, seqno, streamid, filename)
        seqno += 1

def link_records(records):
    prev = None
    for rec in records:
        if prev is not None:
            if rec.level == prev.level:
                rec.sister = prev
                rec.parent = prev.parent
            elif rec.level == prev.level + 1:
                rec.parent = prev
        yield rec
        prev = rec

def main():
    import sys
    import logging
    import itertools
    from .filestructure import File

    from optparse import OptionParser as OP
    op = OP(usage='usage: %prog [options] filename <record-stream> [<record-range>]\n\n<record-range> : <index> | <start-index>: | :<end-index> | <start-index>:<end-index>')
    op.add_option('-f', '--output-format', dest='oformat', default='hex',
            help='output format for record: hex, python or raw [default: hex]')

    options, args = op.parse_args()
    try:
        filename = args.pop(0)
    except IndexError:
        print 'the input filename is required'
        op.print_help()
        return -1

    class RawFormat:
        def write(self, rec):
            bytes = encode_record_header(rec) + rec.payload 
            sys.stdout.write( bytes )
    class PythonStringFormat:
        def write(self, rec):
            bytes = encode_record_header(rec) + rec.payload 
            sys.stdout.write( bytes.encode('string_escape') )
    class HexFormat:
        out = dataio.IndentedOutput(sys.stdout, 0)
        p = dataio.Printer(out)
        def write(self, rec):
            self.out.level = rec.level
            self.p.prints( rec )
            self.p.prints( dataio.hexdump(rec.payload, True) )
            print  '-' * 80
    formats = dict(hex=HexFormat(), raw=RawFormat(), python=PythonStringFormat())
    oformat = formats[options.oformat]

    file = File(filename)

    logging.info( (file.fileheader.version, filename) )

    try:
        stream_specifier = args.pop(0)
    except IndexError:
        print '<record-stream> is not specified'
        op.print_help()
        print 'Available <record-stream>s:'
        print ''
        print 'docinfo'
        print 'bodytext/<idx>'
        return -1

    stream_spec = stream_specifier.split('/')
    stream_name = stream_spec[0]
    stream_args = stream_spec[1:]

    method = getattr(file, stream_name)
    bytestream = method(*stream_args)
    records = read_records(bytestream, stream_specifier, filename)
    records = link_records(records)

    def nth(iterable, n):
        return next(itertools.islice(iterable, n, None))

    def dump_record(records, recidx):
        rec = nth(records, int(recidx))
        logging.info( 'payload size = %d\n', len(rec.payload) )
        oformat.write(rec)

    def dump_records(records):
        out = dataio.IndentedOutput(sys.stdout, 0)
        p = dataio.Printer(out)
        for rec in records:
            oformat.write(rec)

    if len(args) == 0:
        dump_records(records)
    else:
        range = args.pop(0)
        separator = range.find(':')
        if separator == -1:
            dump_record(records, range)
        else:
            start = range[:separator]
            end = range[separator+1:]
            if start != '':
                start = int(start)
                records = itertools.islice(records, start, None)
            else:
                start = 0
            if end != '':
                end = int(end)
                count = end-start
                records = itertools.islice(records, count)
            dump_records(records)

if __name__ == '__main__':
    main()
