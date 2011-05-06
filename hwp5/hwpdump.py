#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import struct
import logging
from . import hwp50, dataio

def encode_record_header(rec):
    size = len(rec.bytes)
    level = rec.level
    tagid = rec.tagid
    if size < 0xfff:
        hdr = (size << 20) | (level << 10) | tagid
        return struct.pack('<I', hdr)
    else:
        hdr = (0xfff << 20) | (level << 10) | tagid
        return struct.pack('<II', hdr, size)

def dump_stream(stream, args):
    try:
        recidx = int(args.pop(0))
    except IndexError:
        recidx = None
    except ValueError:
        print 'invalid record number'
        sys.exit(-1)

    if recidx is None:
        out = dataio.IndentedOutput(sys.stdout, 0)
        p = dataio.Printer(out)
        for rec in stream.records:
            out.level = rec.level
            p.prints( rec )
            p.prints( rec.model )
            p.prints( dataio.hexdump(rec.bytes, True) )
            print  '-' * 80
    else:
        rec = list(stream.records)[recidx]
        sys.stderr.write( 'size = %d\n' % len(rec.bytes) )
        sys.stdout.write( encode_record_header(rec) )
        sys.stdout.write( rec.bytes )

def hwpdump(args):
    try:
        filename = args.pop(0)
    except IndexError:
        print 'filename required'
        return -1

    doc = hwp50.Document(filename)

    logging.info( (doc.header.version, filename) )

    try:
        stream_type = args.pop(0)
    except IndexError:
        print 'section | docinfo'
        return -1
    
    if stream_type == 'section':
        try:
            section_number = int(args.pop(0))
        except IndexError:
            print 'section number required'
            return -1
        except ValueError:
            print 'invalid section number'

        stream = doc.get_bodytext_section(section_number)
        dump_stream(stream, args)
    elif stream_type == 'docinfo':
        stream = doc.docinfo
        dump_stream(stream, args)
    else:
        print 'unknown stream type: '+stream_type
        return -1

def main():
    hwpdump(list(sys.argv[1:]))

if __name__ == '__main__':
    main()
