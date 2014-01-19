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
from itertools import chain
from hwp5.filestructure import VERSION
from hwp5.dataio import typed_struct_attributes
from hwp5.dataio import Struct
from hwp5.dataio import ArrayType
from hwp5.dataio import FlagsType
from hwp5.dataio import EnumType
from hwp5.dataio import WCHAR
from hwp5.dataio import HWPUNIT
from hwp5.dataio import HWPUNIT16
from hwp5.dataio import SHWPUNIT
from hwp5.binmodel import COLORREF
from hwp5.binmodel import BinStorageId
from hwp5.binmodel import Margin
from hwp5.binmodel import Text
from hwp5.treeop import STARTEVENT
from hwp5.treeop import ENDEVENT
import logging
logger = logging.getLogger(__name__)


def xmlattrval(value):
    if isinstance(value, basestring):
        return value
    elif isinstance(type(value), EnumType):
        return type(value)(value).name.lower()
    elif isinstance(value, type):
        return value.__name__
    else:
        return str(value)


def expanded_xmlattribute((name, (t, value))):
    if isinstance(t, FlagsType):
        fmt = '%0'
        fmt += '%d' % (t.basetype.fixed_size * 2)
        fmt += 'X'
        yield name, fmt % int(value)
        for k, v in t.dictvalue(t(value)).iteritems():
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
            yield name, unichr(value)
    elif t is BinStorageId:
        yield name, 'BIN%04X' % value
    else:
        yield name, xmlattrval(value)


def xmlattr_dashednames(attrs):
    for k, v in attrs:
        yield k.replace('_', '-'), v


def xmlattr_uniqnames(attrs):
    names = set([])
    for k, v in attrs:
        assert not k in names, 'name clashes: %s' % k
        yield k, v
        names.add(k)


def xmlattributes_for_plainvalues(context, plainvalues):
    ntvs = plainvalues.iteritems()
    ntvs = chain(*(expanded_xmlattribute(ntv) for ntv in ntvs))
    return dict(xmlattr_uniqnames(xmlattr_dashednames(ntvs)))


def is_complex_type(type, value):
    if isinstance(value, dict):
        return True
    elif isinstance(type, ArrayType) and issubclass(type.itemtype, Struct):
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
        except Exception, e:
            logger.error('%s', (name, t, value))
            logger.error('%s', t.__dict__)
            logger.exception(e)
            raise e
    return d, p


def startelement(context, (model, attributes)):
    from hwp5.dataio import StructType
    if isinstance(model, StructType):
        typed_attributes = ((v['name'], (v['type'], v['value']))
                            for v in typed_struct_attributes(model, attributes,
                                                             context))
    else:
        typed_attributes = ((k, (type(v), v))
                            for k, v in attributes.iteritems())

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
            assert issubclass(_type.itemtype, Struct), (_value, _type)
            yield STARTEVENT, ('Array', {'name': _name})
            for _itemvalue in _value:
                for x in element(context, (_type.itemtype, _itemvalue)):
                    yield x
            yield ENDEVENT, 'Array'


def element(context, (model, attributes)):
    for x in startelement(context, (model, attributes)):
        yield x
    yield ENDEVENT, model.__name__


def xmlevents_to_bytechunks(xmlevents, encoding='utf-8'):
    from xml.sax.saxutils import escape
    from xml.sax.saxutils import quoteattr
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
                if isinstance(v, unicode):
                    v = v.encode(encoding)
                yield v
            yield '>'
        elif event is Text:
            text = escape(item)
            if isinstance(text, unicode):
                text = text.encode(encoding)
            yield text
        elif event is ENDEVENT:
            yield '</'
            yield item
            yield '>'
