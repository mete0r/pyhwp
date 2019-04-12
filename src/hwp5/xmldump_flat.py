# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2015 mete0r <mete0r@sarangbang.or.kr>
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

from .binmodel import ControlChar
from .binmodel import ParaTextChunks
from .binmodel import Text
from .bintype import resolve_type_events
from .bintype import resolve_values_from_stream
from .dataio import ArrayType
from .dataio import EnumType
from .dataio import FlagsType
from .dataio import SelectiveType
from .dataio import StructType
from .dataio import X_ARRAY
from .filestructure import FileHeader
from .treeop import ENDEVENT
from .treeop import STARTEVENT
from .xmlformat import xmlevents_to_bytechunks


def xmldump_flat(hwp5file, output, xml_declaration=True):
    xmlevents = xmlevents_from_hwp5file(hwp5file)
    bytechunks = xmlevents_to_bytechunks(xmlevents)
    if xml_declaration:
        output.write('<?xml version="1.0" encoding="utf-8"?>')
    for x in bytechunks:
        output.write(x)


def xmlevents_from_hwp5file(hwp5file):
    version = '%d.%d.%d.%d' % hwp5file.fileheader.version
    hexversion = '%02x%02x%02x%02x' % hwp5file.fileheader.version
    yield STARTEVENT, ('Hwp5Doc', {
        'version': version,
        'hexversion': hexversion
    })

    with hwp5file.fileheader.open() as f:
        yield STARTEVENT, ('FileHeader', {
        })
        resolve_values = resolve_values_from_stream(f)
        model_events = resolve_type_events(FileHeader, {}, resolve_values)
        for x in xmlevents_from_modelevents(model_events):
            yield x
        yield ENDEVENT, 'FileHeader'

    yield STARTEVENT, ('DocInfo', {
    })
    model_events = hwp5file.docinfo.parse_model_events()
    for x in xmlevents_from_modelevents(model_events):
        yield x
    yield ENDEVENT, 'DocInfo'

    for section_name in hwp5file.bodytext:
        section = hwp5file.bodytext[section_name]
        yield STARTEVENT, ('Section', {
            'name': section_name
        })
        model_events = section.parse_model_events()
        for x in xmlevents_from_modelevents(model_events):
            yield x
        yield ENDEVENT, 'Section'

    yield ENDEVENT, 'Hwp5Doc'


def expand_item_value(ev, data):
    if ev is None and data['type'] is ParaTextChunks:
        yield STARTEVENT, data
        for (start, end), item in data['value']:
            if isinstance(item, unicode):
                yield None, {
                    'bin_offset': data['bin_offset'] + start * 2,
                    'type': Text,
                    'value': item,
                }
            else:
                x = {
                    'bin_offset': data['bin_offset'] + start * 2,
                    'type': ControlChar,
                    'value': item,
                }
                yield None, x
        yield ENDEVENT, data
    else:
        yield ev, data


def expand_item_values(model_events):
    for ev, item in model_events:
        for x in expand_item_value(ev, item):
            yield x


def xmlevents_from_modelevents(model_events):  # noqa
    expanded_events = expand_item_values(model_events)
    for ev, data in expanded_events:
        record = data.get('record')
        if record:
            if ev is STARTEVENT:
                yield ev, ('Record', {
                    'tagname': record['tagname'],
                    'tagid': unicode(record['tagid']),
                    'seqno': unicode(record['seqno']),
                    'level': unicode(record['level']),
                    'size': unicode(record['size']),
                })
            elif ev is ENDEVENT:
                yield ev, 'Record'
            else:
                assert False
        else:
            datatype = data['type']
            typename = datatype.__name__

            if ev in (STARTEVENT, ENDEVENT):
                if isinstance(datatype, (ArrayType, X_ARRAY)):
                    elem = 'array'
                    atrs = {
                    }
                elif isinstance(datatype, (StructType, SelectiveType)):
                    elem = 'struct'
                    atrs = {
                        'type': typename
                    }
                else:
                    raise Exception(datatype.__name__)

                if 'name' in data:
                    atrs['name'] = data['name']
                if ev is STARTEVENT:
                    yield ev, (elem, atrs)
                else:
                    yield ev, elem
            elif ev is None:
                atrs = {
                    'type': typename,
                    'value': unicode(data['value'])
                }
                if 'name' in data:
                    atrs['name'] = data['name']
                if 'bin_offset' in data:
                    atrs['offset'] = unicode(data['bin_offset'])
                if 'bin_value' in data:
                    atrs['bin_value'] = unicode(data['bin_value'])
                if 'bin_type' in data:
                    atrs['type'] = data['bin_type'].__name__
                yield STARTEVENT, ('item', atrs)

                if isinstance(datatype, FlagsType):
                    fixed_size = datatype.basetype.fixed_size
                    b = bin(data['value'])[2:]
                    if len(b) < fixed_size * 8:
                        b = '0' * (fixed_size * 8 - len(b)) + b
                    h = hex(data['value'])[2:]
                    if len(h) < fixed_size * 2:
                        h = '0' * (fixed_size * 2 - len(h)) + h
                    if h.endswith('L'):
                        h = h[:-1]
                    atrs = {
                        'hex': h,
                        'bin': b
                    }
                    yield STARTEVENT, ('bitflags', atrs)

                    for bitfield_name in datatype.bitfields:
                        desc = datatype.bitfields[bitfield_name]
                        bitfield_type = desc.valuetype
                        value = desc.__get__(data['value'], None)

                        atrs = {
                            'type': datatype.basetype.__name__,
                            'name': bitfield_name,
                            'msb': unicode(desc.msb),
                            'lsb': unicode(desc.lsb),
                            'value': unicode(value)
                        }
                        yield STARTEVENT, ('bits', atrs)

                        if isinstance(bitfield_type, EnumType):
                            atrs = {
                                'type': bitfield_type.__name__,
                                'value': value.name
                            }
                            yield STARTEVENT, ('enum', atrs)
                            yield ENDEVENT, 'enum'

                        yield ENDEVENT, 'bits'

                    yield ENDEVENT, 'bitflags'

                yield ENDEVENT, 'item'
