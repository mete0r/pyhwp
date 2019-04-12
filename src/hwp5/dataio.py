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
from array import array
from binascii import b2a_hex
from itertools import takewhile
import inspect
import logging
import struct
import sys

from six import with_metaclass


PY3 = sys.version_info.major == 3


if PY3:
    long = int
    unicode = str
    basestring = str


logger = logging.getLogger(__name__)


class Eof(Exception):
    def __init__(self, *args):
        self.args = args


class OutOfData(Exception):
    pass


def readn(f, size):
    data = f.read(size)
    datasize = len(data)
    if datasize == 0:
        try:
            pos = f.tell()
        except IOError:
            pos = '<UNKNOWN>'
        raise Eof(pos)
    return data


class PrimitiveType(type):
    def __new__(mcs, name, bases, attrs):
        basetype = bases[0]
        attrs['basetype'] = basetype
        attrs.setdefault('__slots__', [])

        never_instantiate = attrs.pop('never_instantiate', True)
        if never_instantiate and '__new__' not in attrs:
            def __new__(cls, *args, **kwargs):
                return basetype.__new__(basetype, *args, **kwargs)
            attrs['__new__'] = __new__

        if 'binfmt' in attrs:
            binfmt = attrs['binfmt']
            fixed_size = struct.calcsize(binfmt)

            if 'fixed_size' in attrs:
                assert fixed_size == attrs['fixed_size']
            else:
                attrs['fixed_size'] = fixed_size

            if 'decode' not in attrs:
                def decode(cls, s):
                    return struct.unpack(binfmt, s)[0]
                attrs['decode'] = classmethod(decode)

        if 'fixed_size' in attrs and 'read' not in attrs:
            fixed_size = attrs['fixed_size']

            def read(cls, f):
                s = readn(f, fixed_size)
                decode = getattr(cls, 'decode', None)
                if decode:
                    return decode(s)
                return s
            attrs['read'] = classmethod(read)

        return type.__new__(mcs, str(name), bases, attrs)


def Primitive(name, basetype, binfmt, **attrs):
    attrs['binfmt'] = binfmt
    return PrimitiveType(name, (basetype,), attrs)


UINT32 = Primitive('UINT32', long, '<I')
INT32 = Primitive('INT32', int, '<i')
UINT16 = Primitive('UINT16', int, '<H')
INT16 = Primitive('INT16', int, '<h')
UINT8 = Primitive('UINT8', int, '<B')
INT8 = Primitive('INT8', int, '<b')
WORD = Primitive('WORD', int, '<H')
BYTE = Primitive('BYTE', int, '<B')
DOUBLE = Primitive('DOUBLE', float, '<d')
WCHAR = Primitive('WCHAR', int, '<H')
HWPUNIT = Primitive('HWPUNIT', long, '<I')
SHWPUNIT = Primitive('SHWPUNIT', int, '<i')
HWPUNIT16 = Primitive('HWPUNIT16', int, '<h')

inch2mm = lambda x: float(int(x * 25.4 * 100 + 0.5)) / 100  # noqa
hwp2inch = lambda x: x / 7200.0  # noqa
hwp2mm = lambda x: inch2mm(hwp2inch(x))  # noqa
hwp2pt = lambda x: int((x / 100.0) * 10 + 0.5) / 10.0  # noqa


class HexBytes(type):
    def __new__(mcs, size):
        decode = staticmethod(b2a_hex)
        return type.__new__(mcs, str('HexBytes(%d)' % size), (str,),
                            dict(fixed_size=size, decode=decode))


def decode_uint16le_array_default(bytes):
    codes = array(str('H'), bytes)
    if sys.byteorder == 'big':
        codes.byteswap()
    return codes


def decode_uint16le_array_in_jython(bytes):
    codes = array(str('h'), bytes)
    assert codes.itemsize == 2
    assert sys.byteorder == 'big'
    codes.byteswap()
    codes = array(str('H'), codes.tostring())
    assert codes.itemsize == 4
    return codes


in_jython = sys.platform.startswith('java')
if in_jython:
    decode_uint16le_array = decode_uint16le_array_in_jython
else:
    decode_uint16le_array = decode_uint16le_array_default


class BSTR(with_metaclass(PrimitiveType, unicode)):

    def read(f):
        size = UINT16.read(f)
        if size == 0:
            return u''
        data = readn(f, 2 * size)
        return decode_utf16le_with_hypua(data)
    read = staticmethod(read)


def decode_utf16le_with_hypua(bytes):
    ''' decode utf-16le encoded bytes with Hanyang-PUA codes into a unicode
    string with Hangul Jamo codes

    :param bytes: utf-16le encoded bytes with Hanyang-PUA codes
    :returns: a unicode string with Hangul Jamo codes
    '''
    return bytes.decode('utf-16le')


class BitGroupDescriptor(object):
    def __init__(self, bitgroup):
        valuetype = int
        if isinstance(bitgroup, tuple):
            if len(bitgroup) > 2:
                lsb, msb, valuetype = bitgroup
            else:
                lsb, msb = bitgroup
        else:
            lsb = msb = bitgroup
        self.lsb = lsb
        self.msb = msb
        self.valuetype = valuetype

    def __get__(self, instance, owner):
        valuetype = self.valuetype
        return valuetype(self.get_int_value(instance))

    def get_int_value(self, instance):
        lsb = self.lsb
        msb = self.msb
        return int(instance >> lsb) & int((2 ** (msb + 1 - lsb)) - 1)


class FlagsType(type):
    def __new__(mcs, name, bases, attrs):
        basetype = attrs.pop('basetype')
        bases = (basetype.basetype,)

        bitgroups = dict((k, BitGroupDescriptor(v))
                         for k, v in attrs.items())

        attrs = dict(bitgroups)
        attrs['__name__'] = name
        attrs['__slots__'] = ()

        attrs['basetype'] = basetype
        attrs['bitfields'] = bitgroups

        def dictvalue(self):
            return dict((name, getattr(self, name))
                        for name in bitgroups.keys())
        attrs['dictvalue'] = dictvalue

        return type.__new__(mcs, str(name), bases, attrs)


def _lex_flags_args(args):
    for idx, arg in enumerate(args):
        while True:
            pushback = (yield idx, arg)
            if pushback is arg:
                yield
                continue
            break


def _parse_flags_args(args):
    args = _lex_flags_args(args)
    try:
        idx = -1
        while True:
            # lsb
            try:
                idx, lsb = next(args)
            except StopIteration:
                break
            assert isinstance(lsb, int), ('#%d arg is expected to be'
                                          'a int: %s' % (idx, repr(lsb)))

            # msb (default: lsb)
            idx, x = next(args)
            if isinstance(x, int):
                msb = x
            elif isinstance(x, (type, basestring)):
                args.send(x)  # pushback
                msb = lsb
            else:
                assert False, '#%d arg is unexpected type: %s' % (idx, repr(x))

            # type (default: int)
            idx, x = next(args)
            assert not isinstance(x, int), ('#%d args is expected to be a type'
                                            'or name: %s' % (idx, repr(x)))
            if isinstance(x, type):
                t = x
            elif isinstance(x, basestring):
                args.send(x)  # pushback
                t = int
            else:
                assert False, '#%d arg is unexpected type: %s' % (idx, repr(x))

            # name
            idx, name = next(args)
            assert isinstance(name, basestring), ('#%d args is expected to be '
                                                  'a name: %s' % (idx,
                                                                  repr(name)))

            yield name, (lsb, msb, t)

    except StopIteration:
        assert False, '#%d arg is expected' % (idx + 1)


def Flags(basetype, *args):
    attrs = dict(_parse_flags_args(args))
    attrs['basetype'] = basetype
    return FlagsType('Flags', (), attrs)


enum_type_instances = set()


class EnumType(type):
    def __new__(mcs, enum_type_name, bases, attrs):
        items = attrs.pop('items')
        moreitems = attrs.pop('moreitems')

        populate_state = [1]

        names_by_instance = dict()
        instances_by_name = dict()
        instances_by_value = dict()

        def __new__(cls, value, name=None):
            if isinstance(value, cls):
                return value

            if name is None:
                if value in instances_by_value:
                    return instances_by_value[value]
                else:
                    logger.warning('undefined %s value: %s',
                                   cls.__name__, value)
                    logger.warning('defined name/values: %s',
                                   str(instances_by_name))
                    return int.__new__(cls, value)

            if len(populate_state) == 0:
                raise TypeError()

            assert name not in instances_by_name

            if value in instances_by_value:
                self = instances_by_value[value]
            else:
                # define new instance of this enum
                self = int.__new__(cls, value)
                instances_by_value[value] = self
                names_by_instance[self] = name

            instances_by_name[name] = self
            return self
        attrs['__new__'] = __new__
        attrs['__slots__'] = []
        attrs['scoping_struct'] = None

        class NameDescriptor(object):
            def __get__(self, instance, owner):
                if instance is None:
                    return owner.__name__
                return names_by_instance.get(instance)

        attrs['name'] = NameDescriptor()

        def __repr__(self):
            enum_name = type(self).__name__
            item_name = self.name
            if item_name is not None:
                return enum_name + '.' + item_name
            else:
                return '%s(%d)' % (enum_name, self)
        attrs['__repr__'] = __repr__

        cls = type.__new__(mcs, str(enum_type_name), bases, attrs)

        for v, k in enumerate(items):
            setattr(cls, k, cls(v, k))
        for k, v in moreitems.items():
            setattr(cls, k, cls(v, k))

        cls.names = set(instances_by_name.keys())
        cls.instances = set(names_by_instance.keys())

        # no more population
        populate_state.pop()

        enum_type_instances.add(cls)
        return cls

    def __init__(cls, *args, **kwargs):
        pass


def Enum(*items, **moreitems):
    attrs = dict(items=items, moreitems=moreitems)
    return EnumType('Enum', (int,), attrs)


class CompoundType(type):
    def __new__(mcs, name, bases, attrs):
        return type.__new__(mcs, str(name), bases, attrs)


class ArrayType(CompoundType):
    def __init__(self, *args, **kwargs):
        pass


class FixedArrayType(ArrayType):

    classes = dict()

    def __new__(mcs, itemtype, size):
        key = itemtype, size

        cls = mcs.classes.get(key)
        if cls is not None:
            return cls

        attrs = dict(itemtype=itemtype, size=size)
        name = 'ARRAY(%s,%s)' % (itemtype.__name__, size)
        cls = ArrayType.__new__(mcs, str(name), (tuple,), attrs)
        mcs.classes[key] = cls
        return cls


ARRAY = FixedArrayType


class VariableLengthArrayType(ArrayType):

    classes = dict()

    def __new__(mcs, counttype, itemtype):
        key = counttype, itemtype

        cls = mcs.classes.get(key)
        if cls is not None:
            return cls

        attrs = dict(itemtype=itemtype, counttype=counttype)
        name = 'N_ARRAY(%s,%s)' % (counttype.__name__, itemtype.__name__)
        cls = ArrayType.__new__(mcs, str(name), (list,), attrs)
        mcs.classes[key] = cls
        return cls


N_ARRAY = VariableLengthArrayType


def ref_member(member_name):
    def fn(context, values):
        return values[member_name]
    fn.__doc__ = member_name
    return fn


def ref_member_flag(member_name, bitfield_name):
    def fn(context, values):
        return getattr(values[member_name], bitfield_name)
    fn.__doc__ = '%s.%s' % (member_name, bitfield_name)
    return fn


class X_ARRAY(object):

    def __init__(self, itemtype, count_reference):
        name = 'ARRAY(%s, \'%s\')' % (itemtype.__name__,
                                      count_reference.__doc__)
        self.__doc__ = self.__name__ = name
        self.itemtype = itemtype
        self.count_reference = count_reference

    def __call__(self, context, values):
        count = self.count_reference(context, values)
        return ARRAY(self.itemtype, count)


class SelectiveType(object):

    def __init__(self, selector_reference, selections):
        self.__name__ = 'SelectiveType'
        self.selections = selections
        self.selector_reference = selector_reference

    def __call__(self, context, values):
        selector = self.selector_reference(context, values)
        return self.selections.get(selector, Struct)  # default: empty struct


class ParseError(Exception):

    treegroup = None

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.cause = None
        self.path = None
        self.record = None
        self.binevents = None
        self.parse_stack_traces = []

    def print_to_logger(self, logger):
        e = self
        logger.error('ParseError: %s', e)
        logger.error('Caused by: %s', repr(e.cause))
        logger.error('Path: %s', e.path)
        if e.treegroup is not None:
            logger.error('Treegroup: %s', e.treegroup)
        if e.record:
            logger.error('Record: %s', e.record['seqno'])
            logger.error('Record Payload:')
            for line in dumpbytes(e.record['payload'], True):
                logger.error('  %s', line)
        logger.error('Problem Offset: at %d (=0x%x)', e.offset, e.offset)
        if self.binevents:
            logger.error('Binary Parse Events:')
            from hwp5.bintype import log_events
            for ev, item in log_events(self.binevents, logger.error):
                pass
        logger.error('Model Stack:')
        for level, c in enumerate(reversed(e.parse_stack_traces)):
            model = c['model']
            if isinstance(model, StructType):
                logger.error('  %s', model)
                parsed_members = c['parsed']
                for member in parsed_members:
                    offset = member.get('offset', 0)
                    offset_end = member.get('offset_end', 1)
                    name = member['name']
                    value = member['value']
                    logger.error('    %06x:%06x: %s = %s',
                                 offset, offset_end - 1, name, value)
                logger.error('    %06x:      : %s', c['offset'], c['member'])
                pass
            else:
                logger.error('  %s%s', ' ' * level, c)


def typed_struct_attributes(struct, attributes, context):
    attributes = dict(attributes)

    def popvalue(member):
        name = member['name']
        if name in attributes:
            return attributes.pop(name)
        else:
            return member['type']()

    for member in struct.parse_members_with_inherited(context, popvalue):
        yield member

    # remnants
    for name, value in attributes.items():
        yield dict(name=name, type=type(value), value=value)


class StructType(CompoundType):
    def __init__(cls, name, bases, attrs):
        super(StructType, cls).__init__(name, bases, attrs)
        if 'attributes' in cls.__dict__:
            members = (dict(type=member[0], name=member[1])
                       if isinstance(member, tuple)
                       else member
                       for member in cls.attributes())
            cls.members = list(members)
        for k, v in attrs.items():
            if isinstance(v, EnumType):
                v.__name__ = k
                v.scoping_struct = cls
            elif isinstance(v, FlagsType):
                v.__name__ = k

    def parse_members(cls, context, getvalue):
        if 'attributes' not in cls.__dict__:
            return
        values = dict()
        for member in cls.members:
            member = dict(member)
            if isinstance(member['type'], X_ARRAY):
                member['type'] = member['type'](context, values)
            elif isinstance(member['type'], SelectiveType):
                member['type'] = member['type'](context, values)

            member_version = member.get('version')
            if member_version is None or context['version'] >= member_version:
                condition_func = member.get('condition')
                if condition_func is None or condition_func(context, values):
                    try:
                        value = getvalue(member)
                    except ParseError as e:
                        tracepoint = dict(model=cls, member=member['name'])
                        e.parse_stack_traces.append(tracepoint)
                        raise
                    values[member['name']] = member['value'] = value
                    yield member

    def parse_members_with_inherited(cls, context, getvalue, up_to_cls=None):
        mro = inspect.getmro(cls)
        mro = takewhile(lambda cls: cls is not up_to_cls, mro)
        mro = list(cls for cls in mro if 'attributes' in cls.__dict__)
        mro = reversed(mro)
        for cls in mro:
            for member in cls.parse_members(context, getvalue):
                yield member


class Struct(with_metaclass(StructType, object)):
    pass


def dumpbytes(data, crust=False):
    if PY3:
        _ord = int
    else:
        _ord = ord

    offsbase = 0
    if crust:
        yield '\t 0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F'
    while len(data) > 16:
        if crust:
            line = '%05x0: ' % offsbase
        else:
            line = ''
        line += ' '.join(['%02x' % _ord(ch) for ch in data[0:16]])
        yield line
        data = data[16:]
        offsbase += 1

    if crust:
        line = '%05x0: ' % offsbase
    else:
        line = ''
    line += ' '.join(['%02x' % _ord(ch) for ch in data])
    yield line


def hexdump(data, crust=False):
    return '\n'.join([line for line in dumpbytes(data, crust)])


class IndentedOutput:
    def __init__(self, base, level):
        self.base = base
        self.level = level

    def write(self, x):
        for line in x.split('\n'):
            if len(line) > 0:
                self.base.write('\t' * self.level)
                self.base.write(line)
                self.base.write('\n')


class Printer:
    def __init__(self, baseout):
        self.baseout = baseout

    def prints(self, *args):
        for x in args:
            self.baseout.write(str(x) + ' ')
        self.baseout.write('\n')
