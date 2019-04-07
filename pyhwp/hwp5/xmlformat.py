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
from itertools import chain
from xml.sax.saxutils import escape
from xml.sax.saxutils import quoteattr
import logging
import sys

from .filestructure import VERSION
from .dataio import typed_struct_attributes
from .dataio import Struct
from .dataio import StructType
from .dataio import ArrayType
from .dataio import FlagsType
from .dataio import EnumType
from .dataio import WCHAR
from .dataio import HWPUNIT
from .dataio import HWPUNIT16
from .dataio import SHWPUNIT
from .binmodel import COLORREF
from .binmodel import BinStorageId
from .binmodel import Margin
from .binmodel import Text
from .treeop import STARTEVENT
from .treeop import ENDEVENT


PY3 = sys.version_info.major == 3
if PY3:
    basestring = str
    unichr = chr


logger = logging.getLogger(__name__)


def xmlattrval(value):
    if isinstance(value, basestring):
        return value
    elif isinstance(value, float):
        # https://stackoverflow.com/questions/25898733/why-does-strfloat-return-more-digits-in-python-3-than-python-2
        return repr(value)
    elif isinstance(type(value), EnumType):
        return value.name.lower() if value.name else str(int(value))
    elif isinstance(value, type):
        return value.__name__
    else:
        return str(value)


def expanded_xmlattribute(ntv):
    name, (t, value) = ntv
    if isinstance(t, FlagsType):
        fmt = '%0'
        fmt += '%d' % (t.basetype.fixed_size * 2)
        fmt += 'X'
        yield name, fmt % int(value)
        for k, v in t.dictvalue(t(value)).items():
            yield k, xmlattrval(v)
    elif t is Margin:
        for pos in ('left', 'right', 'top', 'bottom'):
            yield '-'.join([name, pos]), xmlattrval(value.get(pos))
    elif t is COLORREF:
        yield name, xmlattrval(t(value))
    elif t is VERSION:
        yield name, '.'.join(str(x) for x in value)
    elif t in (HWPUNIT, SHWPUNIT, HWPUNIT16):
        yield name, str(value)
    elif t is WCHAR:
        if value == 0:
            yield name, u''
        else:
            if value in PUA_SYMBOLS:
                yield name, PUA_SYMBOLS[value]
            else:
                yield name, unichr(value)
    elif t is BinStorageId:
        yield name, 'BIN%04X' % value
    else:
        yield name, xmlattrval(value)


# TODO: arbitrary assignment; not based on any standards
PUA_SYMBOLS = {
    0xF046: u'☞',  # U+261E WHITE RIGHT POINTING INDEX
    0xF06C: u'●',  # U+25CF BLACK CIRCLE
    # F06C: u'⚫',  # U+26AB MEDIUM BLACK CIRCLE
    0xF09F: u'•',  # U+2022 BULLET = black small circle
    0xF0A1: u'○',  # U+25CB WHITE CIRCLE
    # F0A1: u'⚪',  # U+26AA MEDIUM WHITE CIRCLE
    # F0A1: u'⚬',  # U+26AC MEDIUM SMALL WHITE CIRCLE
    # F0A1: u' ',  # U+25E6 WHITE BULLET
    0xF06E: u'■',  # U+25A0 BLACK SQUARE = molding mark
    0xF0A7: u'▪',  # U+25AA BLACK SMALL SQUARE = square bullet
    0xF06F: u'☐',  # U+2610 BALLOT BOX
    # F06F: u'□',  # U+25A1 WHITE SQUARE = quadrature
    0xF075: u'◆',  # U+25C6 BLACK DIAMOND
    0xF077: u'⬩',  # U+2B29 BLACK SMALL DIAMOND
    # F077: u'⬥',  # U+2B25 BLACK MEDIUM DIAMOND
    # F077: u'⬦',  # U+2B26 WHITE MEDIUM DIAMOND
    0xF076: u'❖',  # U+2756 BLACK DIAMOND MINUS WHITE X
    0xF0A4: u'◉',  # U+25C9 FISHEYE
    # F0A4: u'⦿ ', # U+29BF CIRCLED BULLET
    0xF0AB: u'★',  # U+2605 BLACK STAR
    0xF0Fc: u'✓',  # U+2713 CHECK MARK
    0xF0FE: u'☑',  # U+2611 BALLOT BOX WITH CHECK
}


def xmlattr_dashednames(attrs):
    for k, v in attrs:
        yield k.replace('_', '-'), v


def xmlattr_uniqnames(attrs):
    names = set([])
    for k, v in attrs:
        assert k not in names, 'name clashes: %s' % k
        yield k, v
        names.add(k)


def xmlattributes_for_plainvalues(context, plainvalues):
    ntvs = plainvalues.items()
    ntvs = chain(*(expanded_xmlattribute(ntv) for ntv in ntvs))
    return dict(xmlattr_uniqnames(xmlattr_dashednames(ntvs)))


def is_complex_type(type, value):
    if isinstance(value, dict):
        return True
    elif isinstance(type, ArrayType) and issubclass(type.itemtype, Struct):
        return True
    elif isinstance(type, ArrayType) and issubclass(type.itemtype, COLORREF):
        return True
    else:
        return False


def separate_plainvalues(typed_attributes):
    d = []
    p = dict()
    for named_item in typed_attributes:
        name, item = named_item
        t, value = item
        try:
            if t is Margin:
                p[name] = item
            elif is_complex_type(t, value):
                d.append(named_item)
            else:
                p[name] = item
        except Exception as e:
            logger.error('%s', (name, t, value))
            logger.error('%s', t.__dict__)
            logger.exception(e)
            raise e
    return d, p


def startelement(context, ma):
    model, attributes = ma
    if isinstance(model, StructType):
        typed_attributes = ((v['name'], (v['type'], v['value']))
                            for v in typed_struct_attributes(model, attributes,
                                                             context))
    else:
        typed_attributes = ((k, (type(v), v))
                            for k, v in attributes.items())

    typed_attributes, plainvalues = separate_plainvalues(typed_attributes)

    if model is Text:
        text = plainvalues.pop('text')[1]
    elif '<text>' in plainvalues:
        text = plainvalues.pop('<text>')[1]
    else:
        text = None

    yield STARTEVENT, (model.__name__,
                       xmlattributes_for_plainvalues(context, plainvalues))
    if text:
        yield Text, text

    for _name, (_type, _value) in typed_attributes:
        if isinstance(_value, dict):
            assert isinstance(_value, dict)
            _value = dict(_value)
            _value['attribute-name'] = _name
            for x in element(context, (_type, _value)):
                yield x
        else:
            assert isinstance(_value, (tuple, list)), (_value, _type)
            # assert issubclass(_type.itemtype, Struct), (_value, _type)
            if issubclass(_type.itemtype, Struct):
                yield STARTEVENT, ('Array', {'name': _name})
                for _itemvalue in _value:
                    for x in element(context, (_type.itemtype, _itemvalue)):
                        yield x
                yield ENDEVENT, 'Array'
            elif issubclass(_type.itemtype, COLORREF):
                for _itemvalue in _value:
                    yield STARTEVENT, (_name, {
                        'r': '%d' % ((_itemvalue >> 0) & 0xff),
                        'g': '%d' % ((_itemvalue >> 8) & 0xff),
                        'b': '%d' % ((_itemvalue >> 16) & 0xff),
                        'alpha': '%d' % ((_itemvalue >> 24) & 0xff),
                        'hex': xmlattrval(_type.itemtype(_itemvalue))
                    })
                    yield ENDEVENT, _name
            else:
                assert False, (_value, _type)


def element(context, ma):
    model, attributes = ma
    for x in startelement(context, ma):
        yield x
    yield ENDEVENT, model.__name__


def xmlevents_to_bytechunks(xmlevents, encoding='utf-8'):
    for textchunk in xmlevents_to_textchunks(xmlevents):
        yield textchunk.encode(encoding)


def xmlevents_to_textchunks(xmlevents):
    entities = {'\r': '&#13;',
                '\n': '&#10;',
                '\t': '&#9;'}
    for event, item in xmlevents:
        if event is STARTEVENT:
            yield '<'
            yield item[0]
            for n, v in item[1].items():
                yield ' '
                yield n
                yield '='
                v = quoteattr(v, entities)
                v = v.replace('\x00', '')
                yield v
            yield '>'
        elif event is Text:
            text = escape(item)
            text = text.replace('\x00', '')
            yield text
        elif event is ENDEVENT:
            yield '</'
            yield item
            yield '>'
