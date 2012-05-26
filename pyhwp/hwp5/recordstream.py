# -*- coding: utf-8 -*-
from .tagids import HWPTAG_BEGIN, tagnames
from .dataio import UINT32, Eof
from . import dataio
from . import filestructure
from .importhelper import importStringIO
StringIO = importStringIO()


def tagname(tagid):
    return tagnames.get(tagid, 'HWPTAG%d' % (tagid - HWPTAG_BEGIN))


def Record(tagid, level, payload, size=None, seqno=None, streamid=None, filename=None):
    if size is None:
        size = len(payload)
    d = dict(tagid=tagid, tagname=tagname(tagid), level=level,
                size=size, payload=payload)
    if seqno is not None:
        d['seqno'] = seqno
    if streamid:
        d['streamid'] = streamid
    if filename:
        d['filename'] = filename
    return d


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
    size = len(rec['payload'])
    level = rec['level']
    tagid = rec['tagid']
    if size < 0xfff:
        hdr = (size << 20) | (level << 10) | tagid
        return struct.pack('<I', hdr)
    else:
        hdr = (0xfff << 20) | (level << 10) | tagid
        return struct.pack('<II', hdr, size)


def read_record(f, seqno):
    header = decode_record_header(f)
    if header is None:
        return
    tagid, level, size = header
    payload = dataio.readn(f, size)
    return Record(tagid, level, payload, size, seqno)


def read_records(f, streamid='', filename=''):
    seqno = 0
    while True:
        record = read_record(f, seqno)
        if record:
            if streamid:
                record['streamid'] = streamid
            if filename:
                record['filename'] = filename
            yield record
        else:
            return
        seqno += 1


def link_records(records):
    prev = None
    for rec in records:
        if prev is not None:
            if rec['level'] == prev['level']:
                rec['sister'] = prev
                rec['parent'] = prev.get('parent')
            elif rec['level'] == prev['level'] + 1:
                rec['parent'] = prev
        yield rec
        prev = rec


def record_to_json(record, *args, **kwargs):
    ''' convert a record to json '''
    from .dataio import dumpbytes
    import simplejson  # TODO: simplejson is for python2.5+
    record['payload'] = list(dumpbytes(record['payload']))
    return simplejson.dumps(record, *args, **kwargs)


def generate_json_array(tokens):
    ''' generate json array with given tokens '''
    first = True
    for token in tokens:
        if first:
            yield '[\n'
            first = False
        else:
            yield ',\n'
        yield token
    yield '\n]'


def generate_simplejson_dumps(records, *args, **kwargs):
    ''' generate simplejson.dumps()ed strings for each records

        records: record iterable
        args, kwargs: options for simplejson.dumps
    '''
    tokens = (record_to_json(record, *args, **kwargs)
              for record in records)
    return generate_json_array(tokens)


def bin2json_stream(f):
    ''' convert binary record stream into json stream '''
    records = read_records(f)
    gen = generate_simplejson_dumps(records, sort_keys=True, indent=2)
    from .filestructure import GeneratorReader
    return GeneratorReader(gen)


def nth(iterable, n, default=None):
    from itertools import islice
    return next(islice(iterable, n, None), default)


class RecordStream(filestructure.Hwp5Object):

    def records(self):
        return read_records(self.open(), '', '')

    def record(self, idx):
        ''' get the record at `idx' '''
        return nth(self.records(), idx)

    def records_stream(self):
        return bin2json_stream(self.open())

    def other_formats(self):
        return {'.records': self.records_stream}


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
    from ._scriptutils import (OptionParser, args_pop, args_pop_range,
                               getlogger, open_or_exit)

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
                level = rec['level']
            rec['level'] -= level
            #logger.info('### record level : %d', rec.level)
            yield rec
    records = initlevel(records)

    records = link_records(records)

    def count_tagids(records):
        occurrences = dict()
        for rec in records:
            tagname = rec['tagname']
            occurrences.setdefault(tagname, 0)
            occurrences[tagname] += 1
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
            bytes = encode_record_header(rec) + rec['payload']
            self.out.write(bytes)

    class HexFormat(RecordFormatter):
        def __init__(self, out):
            out = dataio.IndentedOutput(out, 0)
            super(HexFormat, self).__init__(out)
            self.p = dataio.Printer(out)

        def write(self, rec):
            self.out.level = rec['level']
            self.p.prints((rec['seqno'], rec['tagid'], rec['tagname'],
                           rec['size']))
            self.p.prints(dataio.hexdump(rec['payload'], True))
            self.out.write('-' * 80 + '\n')

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
