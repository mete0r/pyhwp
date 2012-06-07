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
    try:
        return islice(iterable, n, None).next()
    except StopIteration:
        return default


class RecordStream(filestructure.VersionSensitiveItem):

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


def parse_recordstream_name(hwpfile, streamname):
    if streamname == 'docinfo':
        return hwpfile.docinfo
    segments = streamname.split('/')
    if len(segments) == 2:
        if segments[0] == 'bodytext':
            try:
                idx = int(segments[1])
                return hwpfile.bodytext.section(idx)
            except ValueError:
                pass
    raise ValueError('invalid stream name: %s' % streamname)
