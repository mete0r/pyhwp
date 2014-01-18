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
from hwp5.dataio import BSTR
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


class VT_LPWSTR(object):
    __metaclass__ = VT_Type
    code = 31


class VT_FILETIME(object):
    __metaclass__ = VT_Type
    code = 64


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
                      0, 16, 'code',
                      17, 'is_vector')

    def attributes(cls):
        yield cls.TypeFlags, 'type'
    attributes = classmethod(attributes)


class MSOLEPropertySet(object):
    def read(f, context):
        propset_header = read_type(MSOLEPropertySetHeader, context, f)
        common_prop_names = {
            0: 'Dictionary',
            1: 'CodePage',
            2: 'Title',
            3: 'Subject',
            4: 'Author',
            5: 'Keywords',
            6: 'Comments',
            7: 'Template',
            8: 'LastSavedBy',
            9: 'RevisionNumber',
            11: 'LastPrinted',
            12: 'CreateTime',
            13: 'LastSavedTime',
            14: 'NumPages',
        }
        for section_desc in propset_header['sections']:
            f.seek(section_desc['offset'])
            section_header = read_type(MSOLEPropertySetSectionHeader,
                                       context, f)
            section_desc['properties'] = section_properties = dict()
            prop_names = dict(common_prop_names)
            for prop_desc in section_header['properties']:
                prop_id = prop_desc['id']
                logger.debug('property id: %d', prop_id)
                f.seek(section_desc['offset'] + prop_desc['offset'])
                if prop_id == 0:
                    namedict = read_type(MSOLEPropertyNameDict, context, f)
                    section_prop_names = dict((name['id'], name['name'])
                                              for name in namedict['names'])
                    #prop_names.update(section_prop_names)
                    section_properties[prop_id] = prop = dict(id=prop_id)
                    prop['name'] = prop_names.get(prop_id, 'property-id-%s' %
                                                  prop_id)
                    prop['value'] = section_prop_names
                elif prop_id == 1:
                    # code page
                    pass
                else:
                    prop = read_type(MSOLEProperty, context, f)
                    prop['id'] = prop_id
                    section_properties[prop_id] = prop
                    if prop_id in prop_names:
                        prop['name'] = prop_names[prop_id]
                    else:
                        prop['name'] = 'property-id-%s' % prop_id
                    logger.debug('name: %s', prop['name'])
                    if not prop['type'].is_vector:
                        vt_code = prop['type'].code
                        vt_type = vt_types[vt_code]
                        logger.debug('type: %s', vt_type)
                        value = read_vt_value(vt_type, context, f)
                        if value is not None:
                            prop['value'] = value

        return propset_header
    read = staticmethod(read)


def read_vt_value(vt_type, context, f):
    if vt_type == VT_I4:
        value = read_type(INT32, context, f)
        logger.debug('value: %s', value)
        return value
    elif vt_type == VT_LPWSTR:
        value = read_type(BSTR, context, f)
        logger.debug('value: %s', value)
        return value
    elif vt_type == VT_FILETIME:
        lword = read_type(UINT32, context, f)
        hword = read_type(UINT32, context, f)
        value = hword << 32 | lword
        value = FILETIME_to_datetime(value)
        logger.debug('value: %s', value)
        return value


def FILETIME_to_datetime(value):
    return datetime(1601, 1, 1, 0, 0, 0) + timedelta(microseconds=value / 10)
