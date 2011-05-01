#!/usr/bin/python
# -*- coding: utf-8 -*-
from . import hwp50, dataio
import sys

def hwpdump(argv):
    if len(argv) < 1:
        print 'filename required'
        return -1
    filename = argv[0]
    doc = hwp50.Document(filename)

    if len(argv) < 2:
        print 'section | docinfo'
        return -1
    stream_type = argv[1]
    
    if stream_type == 'section':
        if len(argv) < 3:
            print 'section number required'
            return -1
        section_number = int(argv[2])
        stream = doc.get_bodytext_section(section_number)
    elif stream_type == 'docinfo':
        stream = doc.docinfo
    else:
        print 'unknown stream type: '+stream_type
        return -1

    print doc.header.version, filename
    out = dataio.IndentedOutput(sys.stdout, 0)
    p = dataio.Printer(out)
    for rec in stream.records:
        out.level = rec.level
        p.prints( rec )
        p.prints( rec.model )
        p.prints( dataio.hexdump(rec.bytes, True) )
        print  '-' * 80

def main():
    hwpdump(list(sys.argv[1:]))

if __name__ == '__main__':
    main()
