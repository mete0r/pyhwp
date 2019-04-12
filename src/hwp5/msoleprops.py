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

from collections import namedtuple
from datetime import datetime
from datetime import timedelta
from uuid import UUID
import logging
import struct

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


def PropertyType(code):

    def decorator(cls):
        cls.code = code
        vt_types[code] = cls
        return cls

    return decorator


@PropertyType(code=0x0003)
class VT_I4(object):

    @classmethod
    def read_value(cls, context, f):
        return read_type(INT32, context, f)


@PropertyType(code=0x001F)
class VT_LPWSTR(object):

    @classmethod
    def read_value(cls, context, f):
        length = read_type(UINT32, context, f)
        data = f.read(length * 2)
        return data.decode('utf-16le')[:-1]  # remove null character


@PropertyType(code=0x0040)
class VT_FILETIME(object):

    @classmethod
    def read_value(cls, context, f):
        lword = read_type(UINT32, context, f)
        hword = read_type(UINT32, context, f)
        value = hword << 32 | lword
        value = FILETIME(value)
        return value


class FILETIME(object):
    __slots__ = ('value', )

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.datetime)

    @property
    def datetime(self):
        return (
            datetime(1601, 1, 1, 0, 0, 0) +
            timedelta(microseconds=self.value / 10)
        )


PropertyIdentifier = namedtuple('PropertyIdentifier', [
    'id',
    'label',
])


PID_DICTIONARY = PropertyIdentifier(
    id=0x00000000,
    label='PID_DICTIONARY',
)
PID_CODEPAGE = PropertyIdentifier(
    id=0x00000001,
    label='PID_CODEPAGE',
)
PID_LOCALE = PropertyIdentifier(
    id=0x80000000,
    label='PID_LOCALE',
)
PID_BEHAVIOR = PropertyIdentifier(
    id=0x80000003,
    label='PID_BEHAVIOR',
)
PIDSI_TITLE = PropertyIdentifier(
    id=0x02,
    label='PIDSI_TITLE'
)
PIDSI_SUBJECT = PropertyIdentifier(
    id=0x03,
    label='PIDSI_SUBJECT'
)
PIDSI_AUTHOR = PropertyIdentifier(
    id=0x04,
    label='PIDSI_AUTHOR'
)
PIDSI_KEYWORDS = PropertyIdentifier(
    id=0x05,
    label='PIDSI_KEYWORDS'
)
PIDSI_COMMENTS = PropertyIdentifier(
    id=0x06,
    label='PIDSI_COMMENTS'
)
PIDSI_TEMPLATE = PropertyIdentifier(
    id=0x07,
    label='PIDSI_TEMPLATE'
)
PIDSI_LASTAUTHOR = PropertyIdentifier(
    id=0x08,
    label='PIDSI_LASTAUTHOR'
)
PIDSI_REVNUMBER = PropertyIdentifier(
    id=0x09,
    label='PIDSI_REVNUMBER'
)
PIDSI_EDITTIME = PropertyIdentifier(
    id=0x0a,
    label='PIDSI_EDITTIME'
)
PIDSI_LASTPRINTED = PropertyIdentifier(
    id=0x0b,
    label='PIDSI_LASTPRINTED'
)
PIDSI_CREATE_DTM = PropertyIdentifier(
    id=0x0c,
    label='PIDSI_CREATE_DTM'
)
PIDSI_LASTSAVE_DTM = PropertyIdentifier(
    id=0x0d,
    label='PIDSI_LASTSAVE_DTM'
)
PIDSI_PAGECOUNT = PropertyIdentifier(
    id=0x0e,
    label='PIDSI_PAGECOUNT'
)
PIDSI_WORDCOUNT = PropertyIdentifier(
    id=0x0f,
    label='PIDSI_WORDCOUNT'
)
PIDSI_CHARCOUNT = PropertyIdentifier(
    id=0x10,
    label='PIDSI_CHARCOUNT'
)
PIDSI_THUMBNAIL = PropertyIdentifier(
    id=0x11,
    label='PIDSI_THUMBNAIL'
)
PIDSI_APPNAME = PropertyIdentifier(
    id=0x12,
    label='PIDSI_APPNAME'
)
PIDSI_SECURITY = PropertyIdentifier(
    id=0x13,
    label='PIDSI_SECURITY'
)


RESERVED_PROPERTIES = (
    PID_DICTIONARY,
    PID_CODEPAGE,
    PID_LOCALE,
    PID_BEHAVIOR,
)


SUMMARY_INFORMATION_PROPERTIES = (
    PIDSI_TITLE,
    PIDSI_SUBJECT,
    PIDSI_AUTHOR,
    PIDSI_KEYWORDS,
    PIDSI_COMMENTS,
    PIDSI_TEMPLATE,
    PIDSI_LASTAUTHOR,
    PIDSI_REVNUMBER,
    PIDSI_EDITTIME,
    PIDSI_LASTPRINTED,
    PIDSI_CREATE_DTM,
    PIDSI_LASTSAVE_DTM,
    PIDSI_PAGECOUNT,
    PIDSI_WORDCOUNT,
    PIDSI_CHARCOUNT,
    PIDSI_THUMBNAIL,
    PIDSI_APPNAME,
    PIDSI_SECURITY,
)


class Property(object):

    def __init__(self, desc, idLabel, type, value):
        self.desc = desc
        self.idLabel = idLabel
        self.type = type
        self.value = value

    @property
    def id(self):
        return self.desc.id


class PropertyDesc(Struct):

    def __init__(self, id, offset):
        self.id = id
        self.offset = offset

    @classmethod
    def fromDict(cls, d):
        return cls(id=d['id'], offset=d['offset'])

    def attributes():
        yield UINT32, 'id'
        yield UINT32, 'offset'  # offset from section start
    attributes = staticmethod(attributes)


class PropertyReader(object):

    def __init__(self, propsetDesc, propDesc, idLabel, codepage,
                 displayName=None):
        self.propsetDesc = propsetDesc
        self.propDesc = propDesc
        self.idLabel = idLabel
        self.codepage = codepage
        self.displayName = displayName

    def read(self, f):
        f.seek(self.propsetDesc.offset + self.propDesc.offset)

        context = {}
        propType = read_type(TypedPropertyValue, context, f)
        propType = TypedPropertyValue.fromDict(propType)
        vt_type = vt_types[propType.code]
        propValue = vt_type.read_value(context, f)

        return Property(
            desc=self.propDesc,
            idLabel=self.idLabel,
            type=propType,
            value=propValue,
        )


class TypedPropertyValue(Struct):
    '''
    [MS-OLEPS] 2.15 TypedPropertyValue
    '''

    def __init__(self, code):
        self.code = code

    @classmethod
    def fromDict(cls, d):
        return cls(code=d['type'].code)

    TypeFlags = Flags(UINT32,
                      0, 16, 'code')

    def attributes(cls):
        yield cls.TypeFlags, 'type'
    attributes = classmethod(attributes)

    @property
    def vt_type(self):
        try:
            return vt_types[self.code]
        except KeyError:
            return None


class DictionaryEntry(Struct):
    '''
    [MS-OLEPS] 2.16 DictionaryEntry
    '''

    def __init__(self, id, name):
        self.id = id
        self.name = name

    @classmethod
    def fromDict(cls, d):
        return cls(
            id=d['id'],
            name=nullterminated_string(d['name']),
        )

    def attributes():
        from hwp5.dataio import N_ARRAY
        from hwp5.dataio import BYTE
        yield UINT32, 'id'
        yield N_ARRAY(UINT32, BYTE), 'name'
    attributes = staticmethod(attributes)


class Dictionary(Struct):
    '''
    [MS-OLEPS] 2.17 Dictionary
    '''

    def __init__(self, entries):
        self.entries = entries

    @classmethod
    def fromDict(cls, d):
        entries = tuple(
            DictionaryEntry.fromDict(entry)
            for entry in d['entries']
        )
        return cls(entries=entries)

    def attributes():
        from hwp5.dataio import N_ARRAY
        yield N_ARRAY(UINT32, DictionaryEntry), 'entries'
    attributes = staticmethod(attributes)

    def get(self, id, defvalue=None):
        for entry in self.entries:
            if id == entry.id:
                return entry.name
        return defvalue


class DictionaryReader(object):

    def __init__(self, propsetDesc, propDesc, idLabel, codepage):
        self.propsetDesc = propsetDesc
        self.propDesc = propDesc
        self.idLabel = idLabel
        self.codepage = codepage

    def read(self, f):
        propsetDesc = self.propsetDesc
        propDesc = self.propDesc
        idLabel = self.idLabel

        f.seek(propsetDesc.offset + propDesc.offset)
        context = {}
        propType = None
        propValue = read_type(Dictionary, context, f)
        propValue = Dictionary.fromDict(propValue)
        return Property(
            desc=propDesc,
            idLabel=idLabel,
            type=propType,
            value=propValue,
        )


class PropertySet(object):
    '''
    [MS-OLEPS] 2.20 PropertySet
    '''

    def __init__(self, desc, header, properties):
        self.desc = desc
        self.header = header
        self.properties = properties

    @property
    def fmtid(self):
        return self.desc.fmtid

    def __getitem__(self, propertyIdentifier):
        for property in self.properties:
            if property.id == propertyIdentifier.id:
                return property.value
        raise KeyError(propertyIdentifier)


class PropertySetHeader(Struct):

    def __init__(self, bytesize, propDescList):
        self.bytesize = bytesize,
        self.propDescList = propDescList

    @classmethod
    def fromDict(cls, d):
        return cls(
            bytesize=d['bytesize'],
            propDescList=tuple(
                PropertyDesc.fromDict(
                    propDesc
                )
                for propDesc in d['propDescList']
            ),
        )

    def attributes():
        from hwp5.dataio import N_ARRAY
        yield UINT32, 'bytesize'
        yield N_ARRAY(UINT32, PropertyDesc), 'propDescList'
    attributes = staticmethod(attributes)


class PropertySetDesc(Struct):

    def __init__(self, fmtid, offset):
        self.fmtid = fmtid
        self.offset = offset

    def attributes():
        yield ARRAY(BYTE, 16), 'fmtid'
        yield UINT32, 'offset'
    attributes = staticmethod(attributes)

    @classmethod
    def fromDict(cls, d):
        return cls(
            fmtid=uuid_from_bytes_tuple(d['fmtid']),
            offset=d['offset'],
        )


class PropertySetStreamHeader(Struct):

    def __init__(self, byteOrder, version, systemIdentifier, clsid,
                 propsetDescList):
        self.byteOrder = byteOrder
        self.version = version
        self.systemIdentifier = systemIdentifier
        self.clsid = clsid
        self.propsetDescList = propsetDescList

    @classmethod
    def fromDict(cls, d):
        return cls(
            byteOrder=d['byteOrder'],
            version=d['version'],
            systemIdentifier=d['systemIdentifier'],
            clsid=uuid_from_bytes_tuple(d['clsid']),
            propsetDescList=tuple(
                PropertySetDesc.fromDict(
                    propsetDesc
                )
                for propsetDesc in d['propsetDescList']
            )
        )

    def attributes():
        yield UINT16, 'byteOrder'
        yield UINT16, 'version'
        yield UINT32, 'systemIdentifier'
        yield ARRAY(BYTE, 16), 'clsid'
        yield N_ARRAY(UINT32, PropertySetDesc), 'propsetDescList'
    attributes = staticmethod(attributes)


class PropertySetStream(object):
    '''
    [MS-OLEPS] 2.21 PropertySetStream
    '''

    def __init__(self, header, propertysets):
        self.header = header
        self.propertysets = propertysets

    @property
    def byteOrder(self):
        return self.header.byteOrder

    @property
    def version(self):
        return self.header.version

    @property
    def systemIdentifier(self):
        return self.header.systemIdentifier

    @property
    def clsid(self):
        return self.header.clsid


class PropertySetFormat(object):

    def __init__(self, fmtid, propertyIdentifiers):
        self.fmtid = fmtid
        self.propertyIdentifiers = propertyIdentifiers

    @property
    def idLabels(self):
        return {
            p.id: p.label
            for p in self.propertyIdentifiers
        }


class PropertySetStreamReader(object):

    def __init__(self, propertySetFormats):
        self.propertySetFormats = {
            propsetFormat.fmtid: propsetFormat
            for propsetFormat in propertySetFormats
        }

    def read(self, f):
        context = {}
        streamHeader = read_type(PropertySetStreamHeader, context, f)
        streamHeader = PropertySetStreamHeader.fromDict(streamHeader)
        propertysetList = list()
        for propsetDesc in streamHeader.propsetDescList:
            f.seek(propsetDesc.offset)
            propsetHeader = read_type(PropertySetHeader, context, f)
            propsetHeader = PropertySetHeader.fromDict(
                propsetHeader,
            )
            try:
                propsetFormat = self.propertySetFormats[propsetDesc.fmtid]
            except KeyError:
                idLabels = {}
            else:
                idLabels = propsetFormat.idLabels

            properties = []
            propDescMap = {
                propDesc.id: propDesc
                for propDesc in propsetHeader.propDescList
            }

            propDesc = propDescMap.pop(PID_CODEPAGE.id, None)
            if propDesc is not None:
                idLabel = idLabels.get(propDesc.id)
                propReader = PropertyReader(
                    propsetDesc=propsetDesc,
                    propDesc=propDesc,
                    idLabel=idLabel,
                    codepage=None,
                    displayName=None,
                )
                prop = propReader.read(f)
                properties.append(prop)

                codepage = prop.value
            else:
                codepage = None

            propDesc = propDescMap.pop(PID_DICTIONARY.id, None)
            if propDesc is not None:
                idLabel = idLabels.get(propDesc.id)
                propReader = DictionaryReader(
                    propsetDesc,
                    propDesc,
                    idLabel,
                    codepage,
                )
                prop = propReader.read(f)
                properties.append(prop)

                dictionary = prop.value
            else:
                dictionary = None

            for propDesc in propDescMap.values():
                idLabel = idLabels.get(propDesc.id)
                displayName = dictionary.get(propDesc.id, None)
                propReader = PropertyReader(
                    propsetDesc=propsetDesc,
                    propDesc=propDesc,
                    idLabel=idLabel,
                    codepage=codepage,
                    displayName=displayName,
                )
                prop = propReader.read(f)
                properties.append(prop)

            propertyset = PropertySet(
                desc=propsetDesc,
                header=propsetHeader,
                properties=properties,
            )
            propertysetList.append(propertyset)

        return PropertySetStream(
            header=streamHeader,
            propertysets=propertysetList,
        )


class PropertySetStreamTextFormatter(object):

    def formatTextLines(self, stream):
        yield '- ByteOrder: 0x%x' % stream.byteOrder
        yield '- Version: %d' % stream.version
        yield '- SystemIdentifier: 0x%08x' % stream.systemIdentifier
        yield '- CLSID: %s' % stream.clsid
        yield ''

        for propertyset in stream.propertysets:
            title = 'Property Set {}'.format(
                propertyset.fmtid,
            )
            yield '- {:08x}: {}'.format(
                propertyset.desc.offset,
                title,
            )
            yield '            {}'.format(
                '-' * len(title)
            )

            properties = sorted(
                propertyset.properties,
                key=lambda property: property.desc.offset,
            )
            for property in properties:
                if property.id == PID_DICTIONARY.id:
                    yield '- {:08x}: {}(=0x{:08x}):'.format(
                        propertyset.desc.offset + property.desc.offset,
                        property.idLabel if property.idLabel is not None
                        else '',
                        property.id,
                    )
                    for entry in property.value.entries:
                        yield '            - {}: {}'.format(
                            entry.id,
                            entry.name,
                        )
                else:
                    yield '- {:08x}: {}(=0x{:08x}): {}'.format(
                        propertyset.desc.offset + property.desc.offset,
                        property.idLabel if property.idLabel is not None
                        else '',
                        property.id,
                        property.value
                    )


def uuid_from_bytes_tuple(t):
    fmt = 'B' * len(t)
    fmt = '<' + fmt
    bytes_le = struct.pack(fmt, *t)
    return UUID(bytes_le=bytes_le)


def nullterminated_string(bs):
    return ''.join(chr(x) for x in bs)[:-1]
