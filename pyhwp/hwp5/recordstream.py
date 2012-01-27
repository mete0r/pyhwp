try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from .tagids import HWPTAG_BEGIN, tagnames
from .dataio import UINT32, Eof
from . import dataio
from .utils import cached_property
from . import filestructure

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

def generate_simplejson_dumps(records, *args, **kwargs):
    ''' generate simplejson.dumps()ed strings for each records

        records: record iterable
        args, kwargs: options for simplejson.dumps
    '''
    from .dataio import dumpbytes
    import binascii
    for rec in records:
        d = dict(index=rec.seqno,
                 tag=rec.tag,
                 tagid=rec.tagid,
                 treelevel=rec.level,
                 payload=list(dumpbytes(rec.payload)))
        if rec.filename:
            d['filename'] = rec.filename
        if rec.streamid:
            d['streamid'] = rec.streamid
        import simplejson # TODO: simplejson is for python2.5+
        yield simplejson.dumps(d, *args, **kwargs) + '\n'

def bin2json_stream(f):
    ''' convert binary record stream into json stream '''
    records = read_records(f, '', '')
    gen = generate_simplejson_dumps(records, sort_keys=True, indent=2)
    from .filestructure import GeneratorReader
    return GeneratorReader(gen)


from .storage import StorageWrapper

class RecordStream(filestructure.Hwp5Object):

    def records(self):
        return read_records(self.open(), '', '')

    def other_formats(self):
        return {'.rec': bin2json_stream}


class Sections(filestructure.Sections):

    section_class = RecordStream


class Hwp5File(filestructure.Hwp5File):
    ''' Hwp5File for 'rec' layer
    '''

    docinfo_class = RecordStream
    bodytext_class = Sections


def main():
    import sys
    from .filestructure import open
    from ._scriptutils import OptionParser, args_pop, args_pop_range, getlogger, open_or_exit

    op = OptionParser(usage='usage: %prog [options] filename <record-stream> [<record-range>]\n\n<record-range> : <index> | <start-index>: | :<end-index> | <start-index>:<end-index>')
    op.add_option('-f', '--format', dest='format', default='hex',
            help='output format: hex, raw or nul [default: hex]')

    options, args = op.parse_args()

    logger = getlogger(options)

    filename = args_pop(args, 'filename')
    if filename == '-':
        filename = 'STDIN'
        streamname = 'STDIN'
        file = sys.stdin
        bytestream = file
    else:
        file = open_or_exit(open, filename)
        streamname = args_pop(args, '<record-stream>')
        bytestream = file.pseudostream(streamname)

    records = read_records(bytestream, streamname, filename)

    from itertools import islice as ranged_records
    record_range = args_pop_range(args)
    if record_range:
        records = ranged_records(records, *record_range)

    def initlevel(records):
        level = None
        for rec in records:
            if level is None:
                level = rec.level
            rec.level -= level
            #logger.info('### record level : %d', rec.level)
            yield rec
    records = initlevel(records)

    records = link_records(records)


    def count_tagids(records):
        occurrences = dict()
        for rec in records:
            occurrences.setdefault(rec.tag, 0)
            occurrences[rec.tag] += 1
            yield rec
        for tag, count in occurrences.iteritems():
            logger.info('%30s: %d', tag, count)
    records = count_tagids(records)

    class RecordFormatter(object):
        def __init__(self, out):
            self.out = out
        def write(self, rec):
            raise NotImplementedError
    class RawFormat(RecordFormatter):
        def write(self, rec):
            bytes = encode_record_header(rec) + rec.payload 
            self.out.write( bytes )
    class HexFormat(RecordFormatter):
        def __init__(self, out):
            out = dataio.IndentedOutput(out, 0)
            super(HexFormat, self).__init__(out)
            self.p = dataio.Printer(out)
        def write(self, rec):
            self.out.level = rec.level
            self.p.prints( rec )
            self.p.prints( dataio.hexdump(rec.payload, True) )
            self.out.write( '-' * 80 + '\n' )
    class NulFormat(RecordFormatter):
        def write(self, rec):
            pass

    formats = dict(hex=HexFormat, raw=RawFormat, nul=NulFormat)
    oformat = formats[options.format](options.outfile)

    for rec in records:
        oformat.write(rec)

    while True:
        if '' == bytestream.read(4096):
            return

if __name__ == '__main__':
    main()
