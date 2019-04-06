# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2015 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from itertools import islice
import json
import struct

from . import dataio
from . import filestructure
from .dataio import dumpbytes
from .dataio import Eof
from .dataio import UINT32
from .tagids import HWPTAG_BEGIN
from .tagids import tagnames
from .utils import JsonObjects


def tagname(tagid):
    return tagnames.get(tagid, 'HWPTAG%d' % (tagid - HWPTAG_BEGIN))


def Record(tagid, level, payload, size=None, seqno=None):
    if size is None:
        size = len(payload)
    d = dict(tagid=tagid, tagname=tagname(tagid), level=level,
             size=size, payload=payload)
    if seqno is not None:
        d['seqno'] = seqno
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


def dump_record(f, record):
    hdr = encode_record_header(record)
    f.write(hdr)
    f.write(record['payload'])


def read_records(f):
    seqno = 0
    while True:
        record = read_record(f, seqno)
        if record:
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
    record['payload'] = list(dumpbytes(record['payload']))
    return json.dumps(record, *args, **kwargs)


def nth(iterable, n, default=None):
    try:
        return next(islice(iterable, n, None))
    except StopIteration:
        return default


def group_records_by_toplevel(records, group_as_list=True):
    ''' group records by top-level trees and return iterable of the groups
    '''
    context = dict()

    try:
        context['top'] = next(records)
    except StopIteration:
        return

    def records_in_a_tree():
        yield context.pop('top')

        for record in records:
            if record['level'] == 0:
                context['top'] = record
                return
            yield record

    while 'top' in context:
        group = records_in_a_tree()
        if group_as_list:
            group = list(group)
        yield group


class RecordStream(filestructure.VersionSensitiveItem):

    def records(self, **kwargs):
        records = read_records(self.open())
        if 'range' in kwargs:
            range = kwargs['range']
            records = islice(records, range[0], range[1])
        elif 'treegroup' in kwargs:
            groups = group_records_by_toplevel(records, group_as_list=True)
            records = nth(groups, kwargs['treegroup'])
        return records

    def record(self, idx):
        ''' get the record at `idx' '''
        return nth(self.records(), idx)

    def records_json(self, **kwargs):
        records = self.records(**kwargs)
        return JsonObjects(records, record_to_json)

    def records_treegrouped(self, group_as_list=True):
        ''' group records by top-level trees and return iterable of the groups
        '''
        records = self.records()
        return group_records_by_toplevel(records, group_as_list)

    def records_treegroup(self, n):
        ''' returns list of records in `n'th top-level tree '''
        groups = self.records_treegrouped()
        return nth(groups, n)

    def other_formats(self):
        return {'.records': self.records_json().open}


class Sections(filestructure.Sections):

    section_class = RecordStream


class Hwp5File(filestructure.Hwp5File):
    ''' Hwp5File for 'rec' layer
    '''

    docinfo_class = RecordStream
    bodytext_class = Sections
