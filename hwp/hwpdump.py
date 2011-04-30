#!/usr/bin/python
# -*- coding: utf-8 -*-
from hwp import hwp50, dataio
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
        stream = doc.sections[section_number]
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
#    for f in [doc.streams.docinfo, doc.streams.section[0]]:
#        idx = 0
#        for rec in hwp50.getRecords(f):
#            tagname = hwp50.tagnames.get(rec.tagid, None)
#            if tagname is None:
#                tagname = '0x%x(HWPTAG_BEGIN + %d)'%(rec.tagid, rec.tagid - hwp50.HWPTAG_BEGIN)
#            print '\t'*rec.level, idx, tagname, rec.size
#
#            record_type = doc.record_types.get(rec.tagid)
#            if record_type is not None:
#                try:
#                    data = dataio.decodeModel(record_type, rec.datastream)
#                    print '\t'*(rec.level+1), repr(data).replace('\n', '\n'+'\t'*(rec.level)), '\n'
#                except:
#                    pass
#            print '\t'*(rec.level+1) + dataio.hexdump(rec.data).replace('\n', '\n'+'\t'*(rec.level+1))
#
#            idx += 1
