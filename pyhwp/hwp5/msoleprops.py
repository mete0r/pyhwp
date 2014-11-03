# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2014 mete0r <mete0r@sarangbang.or.kr>
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
from datetime import datetime
from datetime import timedelta
import logging

from hwp5.dataio import Struct
from hwp5.dataio import Flags
from hwp5.dataio import N_ARRAY
from hwp5.dataio import ARRAY
from hwp5.dataio import BYTE
from hwp5.dataio import UINT16
from hwp5.dataio import UINT32
from hwp5.dataio import INT32
from hwp5.bintype import read_type


logger = logging.getLogger(__name__)


vt_types = dict()


class VT_Type(type):
    def __new__(mcs, name, bases, attrs):
        t = type.__new__(mcs, name, bases, attrs)
        code = attrs['code']
        vt_types[code] = t
        return t


class VT_I4(object):
    __metaclass__ = VT_Type
    code = 3

    @classmethod
    def read_value(cls, context, f):
        return read_type(INT32, context, f)


class VT_LPWSTR(object):
    __metaclass__ = VT_Type
    code = 31

    @classmethod
    def read_value(cls, context, f):
        length = read_type(UINT32, context, f)
        data = f.read(length * 2)
        return data.decode('utf-16le')[:-1]  # remove null character


class VT_FILETIME(object):
    __metaclass__ = VT_Type
    code = 64

    @classmethod
    def read_value(cls, context, f):
        lword = read_type(UINT32, context, f)
        hword = read_type(UINT32, context, f)
        value = hword << 32 | lword
        value = FILETIME_to_datetime(value)
        return value


class MSOLEPropertySectionDesc(Struct):
    def attributes():
        yield ARRAY(BYTE, 16), 'formatid'
        yield UINT32, 'offset'
    attributes = staticmethod(attributes)


class MSOLEPropertySetHeader(Struct):
    def attributes():
        yield UINT16, 'byteorder'
        yield UINT16, 'format'
        yield UINT16, 'osversion'
        yield UINT16, 'os'
        yield ARRAY(BYTE, 16), 'clsid'
        yield N_ARRAY(UINT32, MSOLEPropertySectionDesc), 'sections'
    attributes = staticmethod(attributes)


class MSOLEPropertyDesc(Struct):
    def attributes():
        yield UINT32, 'id'
        yield UINT32, 'offset'  # offset from section start
    attributes = staticmethod(attributes)


class MSOLEPropertySetSectionHeader(Struct):
    def attributes():
        from hwp5.dataio import N_ARRAY
        yield UINT32, 'bytesize'
        yield N_ARRAY(UINT32, MSOLEPropertyDesc), 'properties'
    attributes = staticmethod(attributes)


class MSOLEPropertyName(Struct):
    def attributes():
        from hwp5.dataio import N_ARRAY
        from hwp5.dataio import BYTE
        yield UINT32, 'id'
        yield N_ARRAY(UINT32, BYTE), 'name'
    attributes = staticmethod(attributes)


class MSOLEPropertyNameDict(Struct):
    def attributes():
        from hwp5.dataio import N_ARRAY
        yield N_ARRAY(UINT32, MSOLEPropertyName), 'names'
    attributes = staticmethod(attributes)


class MSOLEProperty(Struct):
    TypeFlags = Flags(UINT32,
                      0, 16, 'code')

    def attributes(cls):
        yield cls.TypeFlags, 'type'
    attributes = classmethod(attributes)


RESERVED_PROPERTIES = [
    dict(id=0x00, name='PID_PROPDISPNAMEDICT',
         title='Property Set Display Name Dictionary'),
    dict(id=0x01, name='PID_CODEPAGE',
         title='Code Page Indicator'),
    dict(id=0x80000000, name='PID_LOCALEID',
         title='Locale ID'),
    dict(id=0x80000003, name='PID_PROPSETBEHAVIOR',
         title='Property Set Behavior')
]


SUMMARY_INFORMATION_PROPERTIES = [
    dict(id=0x02, name='PIDSI_TITLE', title='Title'),
    dict(id=0x03, name='PIDSI_SUBJECT', title='Subject'),
    dict(id=0x04, name='PIDSI_AUTHOR', title='Author'),
    dict(id=0x05, name='PIDSI_KEYWORDS', title='Keywords'),
    dict(id=0x06, name='PIDSI_COMMENTS', title='Comments'),
    dict(id=0x07, name='PIDSI_TEMPLATE', title='Templates'),
    dict(id=0x08, name='PIDSI_LASTAUTHOR', title='Last Saved By'),
    dict(id=0x09, name='PIDSI_REVNUMBER', title='Revision Number'),
    dict(id=0x0a, name='PIDSI_EDITTIME', title='Total Editing Time'),
    dict(id=0x0b, name='PIDSI_LASTPRINTED', title='Last Printed'),
    dict(id=0x0c, name='PIDSI_CREATE_DTM', title='Create Time/Date'),
    dict(id=0x0d, name='PIDSI_LASTSAVE_DTM', title='Last saved Time/Date'),
    dict(id=0x0e, name='PIDSI_PAGECOUNT', title='Number of Pages'),
    dict(id=0x0f, name='PIDSI_WORDCOUNT', title='Number of Words'),
    dict(id=0x10, name='PIDSI_CHARCOUNT', title='Number of Characters'),
    dict(id=0x11, name='PIDSI_THUMBNAIL', title='Thumbnail'),
    dict(id=0x12, name='PIDSI_APPNAME', title='Name of Creating Application'),
    dict(id=0x13, name='PIDSI_SECURITY', title='Security'),
]

for prop in RESERVED_PROPERTIES + SUMMARY_INFORMATION_PROPERTIES:
    namespace = globals()
    namespace[prop['name']] = prop['id']
del namespace
del prop


def uuid_from_bytes_tuple(t):
    from uuid import UUID
    return UUID(bytes_le=''.join(chr(x) for x in t))


def str_from_bytes_tuple(bs):
    return ''.join(chr(x) for x in bs)


class MSOLEPropertySet(object):
    def read(f, context):
        propertyset = read_type(MSOLEPropertySetHeader, context, f)
        propertyset['clsid'] = uuid_from_bytes_tuple(propertyset['clsid'])
        for section in propertyset['sections']:
            section_offset = section.pop('offset')
            f.seek(section_offset)
            section['formatid'] = uuid_from_bytes_tuple(section['formatid'])
            section['properties'] = dict()
            section_header = read_type(MSOLEPropertySetSectionHeader,
                                       context, f)
            prop_names = dict((p['id'], p['name'])
                              for p in RESERVED_PROPERTIES
                              + SUMMARY_INFORMATION_PROPERTIES)
            for desc in section_header['properties']:
                prop_offset = desc['offset']
                f.seek(section_offset + prop_offset)

                prop_id = desc['id']
                prop = section['properties'][prop_id] = dict()
                if prop_id in prop_names:
                    prop['name'] = prop_names[prop_id]

                if prop_id == globals()['PID_PROPDISPNAMEDICT']:
                    namedict = read_type(MSOLEPropertyNameDict, context, f)
                    names = dict((e['id'], str_from_bytes_tuple(e['name']))
                                 for e in namedict['names'])
                    prop['value'] = names
                elif prop_id == globals()['PID_CODEPAGE']:
                    pass
                else:
                    prop.update(read_type(MSOLEProperty, context, f))
                    vt_code = prop['type'].code
                    vt_type = vt_types[vt_code]
                    prop['value'] = vt_type.read_value(context, f)

        return propertyset
    read = staticmethod(read)


def FILETIME_to_datetime(value):
    return datetime(1601, 1, 1, 0, 0, 0) + timedelta(microseconds=value / 10)
