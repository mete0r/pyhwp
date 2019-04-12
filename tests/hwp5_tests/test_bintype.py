# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from io import BytesIO
from unittest import TestCase

from six import add_metaclass

from hwp5.binmodel import ParaTextChunks
from hwp5.bintype import bintype_map_events
from hwp5.bintype import construct_composite_values
from hwp5.bintype import filter_with_version
from hwp5.bintype import static_to_mutable
from hwp5.bintype import read_type_events
from hwp5.bintype import resolve_typedefs
from hwp5.bintype import resolve_values_from_stream
from hwp5.dataio import BSTR
from hwp5.dataio import SelectiveType
from hwp5.dataio import StructType
from hwp5.dataio import UINT16
from hwp5.dataio import X_ARRAY
from hwp5.dataio import ref_member
from hwp5.treeop import STARTEVENT, ENDEVENT


class lazy_property(object):

    def __init__(self, f):
        self.f = f

    def __get__(self, object, owner=None):
        name = self.f.__name__
        if name not in object.__dict__:
            object.__dict__[name] = self.f(object)
        return object.__dict__[name]


class TestBinIO(TestCase):

    @lazy_property
    def BasicStruct(self):

        @add_metaclass(StructType)
        class BasicStruct(object):

            @staticmethod
            def attributes():
                yield UINT16, 'a'
                yield UINT16, 'b'
        return BasicStruct

    @lazy_property
    def NestedStruct(self):

        @add_metaclass(StructType)
        class NestedStruct(object):

            @staticmethod
            def attributes():
                yield UINT16, 'a'
                yield self.BasicStruct, 's'
                yield UINT16, 'b'
        return NestedStruct

    def test_map_events(self):

        bin_item = dict(type=self.BasicStruct)
        events = bintype_map_events(bin_item)

        ev, item = next(events)
        self.assertEqual((STARTEVENT, bin_item), (ev, item))

        ev, item = next(events)
        self.assertEqual((None, dict(name='a', type=UINT16)),
                         (ev, item))

        ev, item = next(events)
        self.assertEqual((None, dict(name='b', type=UINT16)),
                         (ev, item))

        ev, item = next(events)
        self.assertEqual((ENDEVENT, bin_item), (ev, item))

    def test_map_events_nested(self):

        bin_item = dict(type=self.NestedStruct)
        events = bintype_map_events(bin_item)

        ev, item = next(events)
        self.assertEqual((STARTEVENT, bin_item), (ev, item))

        ev, item = next(events)
        self.assertEqual((None, dict(name='a', type=UINT16)),
                         (ev, item))

        ev, item = next(events)
        self.assertEqual((STARTEVENT, dict(name='s', type=self.BasicStruct)),
                         (ev, item))

        ev, item = next(events)
        self.assertEqual((None, dict(name='a', type=UINT16)),
                         (ev, item))

        ev, item = next(events)
        self.assertEqual((None, dict(name='b', type=UINT16)),
                         (ev, item))

        ev, item = next(events)
        self.assertEqual((ENDEVENT, dict(name='s', type=self.BasicStruct)),
                         (ev, item))

        ev, item = next(events)
        self.assertEqual((None, dict(name='b', type=UINT16)),
                         (ev, item))

        ev, item = next(events)
        self.assertEqual((ENDEVENT, bin_item), (ev, item))

    def test_map_struct_with_xarray(self):

        xarray_type = X_ARRAY(self.BasicStruct, ref_member('count'))

        @add_metaclass(StructType)
        class StructWithXArray(object):

            @staticmethod
            def attributes():
                yield UINT16, 'count'
                yield dict(type=xarray_type,
                           name='items')
        bin_item = dict(type=StructWithXArray)
        events = bintype_map_events(bin_item)
        self.assertEqual((STARTEVENT,
                          bin_item),
                         next(events))
        self.assertEqual((None,
                          dict(type=UINT16, name='count')),
                         next(events))
        self.assertEqual((STARTEVENT,
                          dict(type=xarray_type,
                               name='items')),
                         next(events))
        self.assertEqual((STARTEVENT,
                          dict(type=self.BasicStruct)),
                         next(events))
        self.assertEqual((None,
                          dict(type=UINT16, name='a')),
                         next(events))
        self.assertEqual((None,
                          dict(type=UINT16, name='b')),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(type=self.BasicStruct)),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(type=xarray_type,
                               name='items')),
                         next(events))
        self.assertEqual((ENDEVENT,
                          bin_item),
                         next(events))

    def test_filter_with_version(self):

        @add_metaclass(StructType)
        class StructWithVersion(object):

            @classmethod
            def attributes(cls):
                yield UINT16, 'a'
                yield dict(name='b', type=UINT16, version=(5, 0, 2, 4))

        bin_item = dict(type=StructWithVersion)

        events = bintype_map_events(bin_item)
        events = filter_with_version(events, (5, 0, 0, 0))

        self.assertEqual((STARTEVENT, bin_item), next(events))
        self.assertEqual((None, dict(name='a', type=UINT16)), next(events))
        self.assertEqual((ENDEVENT, bin_item), next(events))

        events = bintype_map_events(bin_item)
        events = filter_with_version(events, (5, 0, 2, 4))
        self.assertEqual((STARTEVENT, bin_item), next(events))
        self.assertEqual((None, dict(name='a', type=UINT16)), next(events))
        self.assertEqual((None, dict(name='b', type=UINT16,
                                     version=(5, 0, 2, 4))), next(events))
        self.assertEqual((ENDEVENT, bin_item), next(events))

    def test_resolve_xarray(self):

        xarray_type = X_ARRAY(UINT16, ref_member('a'))

        @add_metaclass(StructType)
        class StructWithXArray(object):

            @staticmethod
            def attributes():
                yield UINT16, 'a'
                yield dict(name='b',
                           type=xarray_type)

        static_events = bintype_map_events(dict(type=StructWithXArray))
        static_events = list(static_events)

        events = static_to_mutable(iter(static_events))
        events = resolve_typedefs(events, dict())
        ev, struct = next(events)
        self.assertEqual((STARTEVENT, struct), (ev, struct))
        self.assertEqual((None,
                          dict(name='a', type=UINT16)),
                         next(events))
        struct['value'] = dict(a=0)
        self.assertEqual((STARTEVENT,
                          dict(name='b',
                               count=0,
                               type=xarray_type)),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(name='b',
                               count=0,
                               type=xarray_type)),
                         next(events))
        self.assertEqual((ENDEVENT, struct),
                         next(events))

        events = static_to_mutable(iter(static_events))
        events = resolve_typedefs(events, dict())
        ev, struct = next(events)
        self.assertEqual((STARTEVENT, struct), (ev, struct))
        self.assertEqual((None,
                          dict(name='a', type=UINT16)),
                         next(events))
        struct['value'] = dict(a=1)
        self.assertEqual((STARTEVENT,
                          dict(name='b',
                               count=1,
                               type=xarray_type)),
                         next(events))
        self.assertEqual((None, dict(type=UINT16)),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(name='b',
                               count=1,
                               type=xarray_type)),
                         next(events))
        self.assertEqual((ENDEVENT, struct),
                         next(events))

        events = static_to_mutable(iter(static_events))
        events = resolve_typedefs(events, dict())
        ev, struct = next(events)
        self.assertEqual((STARTEVENT, struct), (ev, struct))
        self.assertEqual((None,
                          dict(name='a', type=UINT16)),
                         next(events))
        struct['value'] = dict(a=2)
        self.assertEqual((STARTEVENT,
                          dict(name='b',
                               count=2,
                               type=xarray_type)),
                         next(events))
        self.assertEqual((None, dict(type=UINT16)),
                         next(events))
        self.assertEqual((None, dict(type=UINT16)),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(name='b',
                               count=2,
                               type=xarray_type)),
                         next(events))
        self.assertEqual((ENDEVENT, struct),
                         next(events))

    def test_resolve_xarray_struct(self):

        xarray_type = X_ARRAY(self.BasicStruct, ref_member('a'))

        @add_metaclass(StructType)
        class StructWithXArray(object):

            @staticmethod
            def attributes():
                yield UINT16, 'a'
                yield dict(name='b',
                           type=xarray_type)

        static_events = bintype_map_events(dict(type=StructWithXArray))
        static_events = list(static_events)

        events = static_to_mutable(iter(static_events))
        events = resolve_typedefs(events, dict())
        ev, struct = next(events)
        self.assertEqual((STARTEVENT, struct), (ev, struct))
        self.assertEqual((None,
                          dict(name='a', type=UINT16)),
                         next(events))
        struct['value'] = dict(a=0)
        self.assertEqual((STARTEVENT,
                          dict(name='b', count=0, type=xarray_type)),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(name='b', count=0, type=xarray_type)),
                         next(events))
        self.assertEqual((ENDEVENT, struct),
                         next(events))

        events = static_to_mutable(iter(static_events))
        events = resolve_typedefs(events, dict())
        ev, struct = next(events)
        self.assertEqual((STARTEVENT, struct), (ev, struct))
        self.assertEqual((None,
                          dict(name='a', type=UINT16)),
                         next(events))
        struct['value'] = dict(a=1)
        self.assertEqual((STARTEVENT,
                          dict(name='b', count=1, type=xarray_type)),
                         next(events))
        self.assertEqual((STARTEVENT, dict(type=self.BasicStruct)),
                         next(events))
        self.assertEqual((None, dict(name='a', type=UINT16)),
                         next(events))
        self.assertEqual((None, dict(name='b', type=UINT16)),
                         next(events))
        self.assertEqual((ENDEVENT, dict(type=self.BasicStruct)),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(name='b', count=1, type=xarray_type)),
                         next(events))
        self.assertEqual((ENDEVENT, struct),
                         next(events))

        events = static_to_mutable(iter(static_events))
        events = resolve_typedefs(events, dict())
        ev, struct = next(events)
        self.assertEqual((STARTEVENT, struct), (ev, struct))
        self.assertEqual((None,
                          dict(name='a', type=UINT16)),
                         next(events))
        struct['value'] = dict(a=2)
        self.assertEqual((STARTEVENT,
                          dict(name='b', count=2, type=xarray_type)),
                         next(events))
        self.assertEqual((STARTEVENT, dict(type=self.BasicStruct)),
                         next(events))
        self.assertEqual((None, dict(name='a', type=UINT16)),
                         next(events))
        self.assertEqual((None, dict(name='b', type=UINT16)),
                         next(events))
        self.assertEqual((ENDEVENT, dict(type=self.BasicStruct)),
                         next(events))
        self.assertEqual((STARTEVENT, dict(type=self.BasicStruct)),
                         next(events))
        self.assertEqual((None, dict(name='a', type=UINT16)),
                         next(events))
        self.assertEqual((None, dict(name='b', type=UINT16)),
                         next(events))
        self.assertEqual((ENDEVENT, dict(type=self.BasicStruct)),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(name='b', count=2, type=xarray_type)),
                         next(events))
        self.assertEqual((ENDEVENT, struct),
                         next(events))

    def test_resolve_conditional_simple(self):

        def if_a_is_1(context, values):
            return values['a'] == 1

        @add_metaclass(StructType)
        class StructWithCondition(object):

            @staticmethod
            def attributes():
                yield UINT16, 'a'
                yield dict(name='b', type=UINT16, condition=if_a_is_1)
                yield UINT16, 'c'

        static_events = bintype_map_events(dict(type=StructWithCondition))
        static_events = list(static_events)

        events = static_to_mutable(iter(static_events))
        events = resolve_typedefs(events, dict())
        ev, struct = next(events)
        self.assertEqual(STARTEVENT, ev)
        self.assertEqual(StructWithCondition, struct['type'])
        self.assertEqual((None, dict(name='a', type=UINT16)),
                         next(events))
        struct['value'] = dict(a=0)
        self.assertEqual((None, dict(name='c', type=UINT16)),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(struct,
                               value=dict(a=0))),
                         next(events))

        events = static_to_mutable(iter(static_events))
        events = resolve_typedefs(events, dict())
        ev, struct = next(events)
        self.assertEqual(STARTEVENT, ev)
        self.assertEqual(StructWithCondition, struct['type'])
        self.assertEqual((None, dict(name='a', type=UINT16)),
                         next(events))
        struct['value'] = dict(a=1)
        self.assertEqual((None,
                          dict(name='b',
                               type=UINT16)),
                         next(events))
        self.assertEqual((None, dict(name='c', type=UINT16)),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(struct,
                               value=dict(a=1))),
                         next(events))

    def test_resolve_conditional_struct(self):

        def if_a_is_1(context, values):
            return values['a'] == 1

        @add_metaclass(StructType)
        class StructWithCondition(object):

            @staticmethod
            def attributes():
                yield UINT16, 'a'
                yield dict(name='b', type=self.BasicStruct,
                           condition=if_a_is_1)
                yield UINT16, 'c'

        static_events = bintype_map_events(dict(type=StructWithCondition))
        static_events = list(static_events)

        events = static_to_mutable(iter(static_events))
        events = resolve_typedefs(events, dict())
        ev, struct = next(events)
        self.assertEqual(STARTEVENT, ev)
        self.assertEqual(StructWithCondition, struct['type'])
        self.assertEqual((None, dict(name='a', type=UINT16)),
                         next(events))
        struct['value'] = dict(a=0)
        self.assertEqual((None, dict(name='c', type=UINT16)),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(struct,
                               value=dict(a=0))),
                         next(events))

        events = static_to_mutable(iter(static_events))
        events = resolve_typedefs(events, dict())
        ev, struct = next(events)
        self.assertEqual(STARTEVENT, ev)
        self.assertEqual(StructWithCondition, struct['type'])
        self.assertEqual((None, dict(name='a', type=UINT16)),
                         next(events))
        struct['value'] = dict(a=1)
        self.assertEqual((STARTEVENT,
                          dict(name='b',
                               type=self.BasicStruct)),
                         next(events))
        self.assertEqual((None, dict(name='a', type=UINT16)),
                         next(events))
        self.assertEqual((None, dict(name='b', type=UINT16)),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(name='b',
                               type=self.BasicStruct)),
                         next(events))
        self.assertEqual((None, dict(name='c', type=UINT16)),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(struct,
                               value=dict(a=1))),
                         next(events))

    def test_resolve_selective_type(self):

        @add_metaclass(StructType)
        class StructWithSelectiveType(object):

            @staticmethod
            def attributes():
                yield UINT16, 'a'
                yield dict(name='b',
                           type=SelectiveType(ref_member('a'),
                                              {0: UINT16,
                                               1: self.BasicStruct}))
                yield UINT16, 'c'

        static_events = bintype_map_events(dict(type=StructWithSelectiveType))
        static_events = list(static_events)

        events = static_to_mutable(iter(static_events))
        events = resolve_typedefs(events, dict())
        ev, struct = next(events)
        self.assertEqual(STARTEVENT, ev)
        self.assertEqual(StructWithSelectiveType, struct['type'])
        self.assertEqual((None, dict(name='a', type=UINT16)),
                         next(events))
        struct['value'] = dict(a=0)
        self.assertEqual((None, dict(name='b', type=UINT16)),
                         next(events))
        self.assertEqual((None, dict(name='c', type=UINT16)),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(struct,
                               value=dict(a=0))),
                         next(events))

        events = static_to_mutable(iter(static_events))
        events = resolve_typedefs(events, dict())
        ev, struct = next(events)
        self.assertEqual(STARTEVENT, ev)
        self.assertEqual(StructWithSelectiveType, struct['type'])
        self.assertEqual((None, dict(name='a', type=UINT16)),
                         next(events))
        struct['value'] = dict(a=1)
        self.assertEqual((STARTEVENT,
                          dict(name='b',
                               type=self.BasicStruct)),
                         next(events))
        self.assertEqual((None, dict(name='a', type=UINT16)),
                         next(events))
        self.assertEqual((None, dict(name='b', type=UINT16)),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(name='b',
                               type=self.BasicStruct)),
                         next(events))
        self.assertEqual((None, dict(name='c', type=UINT16)),
                         next(events))
        self.assertEqual((ENDEVENT,
                          dict(struct,
                               value=dict(a=1))),
                         next(events))

    def test_resolve_values_from_stream(self):
        assertEqual = self.assertEqual

        stream = BytesIO(b'\x00\x01\x00\x02')
        resolve_values = resolve_values_from_stream(stream)

        bin_item = dict(type=self.BasicStruct)
        events = bintype_map_events(bin_item)
        events = resolve_values(events)

        assertEqual((STARTEVENT, bin_item), next(events))
        assertEqual((None,
                     dict(name='a', type=UINT16, bin_offset=0, value=256)),
                    next(events))
        assertEqual((None,
                     dict(name='b', type=UINT16, bin_offset=2, value=512)),
                    next(events))
        assertEqual((ENDEVENT, bin_item), next(events))

        @add_metaclass(StructType)
        class StructWithBSTR(object):

            @staticmethod
            def attributes():
                yield BSTR, 'name'

        stream = BytesIO(b'\x02\x00\x00\x01\x00\x02')
        resolve_values = resolve_values_from_stream(stream)
        bin_item = dict(type=StructWithBSTR)
        events = bintype_map_events(bin_item)
        events = resolve_values(events)
        assertEqual((STARTEVENT, bin_item), next(events))
        assertEqual((None,
                     dict(name='name', type=BSTR, bin_offset=0,
                          value=u'\u0100\u0200')),
                    next(events))
        assertEqual((ENDEVENT, bin_item), next(events))

        @add_metaclass(StructType)
        class StructWithParaTextChunks(object):

            @staticmethod
            def attributes():
                yield ParaTextChunks, 'texts'

        stream = BytesIO(b'\x20\x00\x21\x00\x22\x00')
        resolve_values = resolve_values_from_stream(stream)
        bin_item = dict(type=StructWithParaTextChunks)
        events = bintype_map_events(bin_item)
        events = resolve_values(events)
        assertEqual((STARTEVENT, bin_item), next(events))
        assertEqual((None,
                     dict(name='texts', type=ParaTextChunks,
                          bin_offset=0,
                          value=[((0, 3), u'\u0020\u0021\u0022')])),
                    next(events))
        assertEqual((ENDEVENT, bin_item), next(events))

    def test_collect_values(self):

        stream = BytesIO(b'\x01\x00\x01\x01\x02\x01\x02\x00')
        resolve_values = resolve_values_from_stream(stream)

        bin_item = dict(type=self.NestedStruct)
        events = bintype_map_events(bin_item)
        events = resolve_values(events)
        events = construct_composite_values(events)

        a = dict(name='a', type=UINT16, bin_offset=0, value=1)
        s_a = dict(name='a', type=UINT16, bin_offset=2, value=0x101)
        s_b = dict(name='b', type=UINT16, bin_offset=4, value=0x102)
        b = dict(name='b', type=UINT16, bin_offset=6, value=2)
        s = dict(name='s', type=self.BasicStruct,
                 value=dict(a=0x101, b=0x102))
        x = dict(type=self.NestedStruct,
                 value=dict(a=1, s=dict(a=0x101, b=0x102), b=2))
        self.assertEqual((STARTEVENT, bin_item), next(events))
        self.assertEqual((None, a), next(events))
        self.assertEqual((STARTEVENT, dict(name='s', type=self.BasicStruct,
                                           value=dict())),
                         next(events))
        self.assertEqual((None, s_a), next(events))
        self.assertEqual((None, s_b), next(events))
        self.assertEqual((ENDEVENT, s), next(events))
        self.assertEqual((None, b), next(events))
        self.assertEqual((ENDEVENT, x), next(events))


class TestReadEvents(TestCase):
    def test_struct_with_condition(self):

        def if_a_is_1(context, values):
            return values['a'] == 1

        @add_metaclass(StructType)
        class StructWithCondition(object):

            @staticmethod
            def attributes():
                yield UINT16, 'a'
                yield dict(name='b', type=UINT16, condition=if_a_is_1)
                yield UINT16, 'c'

        context = dict()

        # if a = 0
        stream = BytesIO(b'\x00\x00\x02\x00')
        events = read_type_events(StructWithCondition, context, stream)
        a = dict(name='a', type=UINT16, value=0, bin_offset=0)
        c = dict(name='c', type=UINT16, value=2, bin_offset=2)
        self.assertEqual((STARTEVENT, dict(type=StructWithCondition,
                                           value=dict())),
                         next(events))
        self.assertEqual((None, a), next(events))
        self.assertEqual((None, c), next(events))
        self.assertEqual((ENDEVENT, dict(type=StructWithCondition,
                                         value=dict(a=0, c=2))),
                         next(events))
        self.assertEqual(b'', stream.read())

        # if a = 1
        stream = BytesIO(b'\x01\x00\x0f\x00\x02\x00')
        events = read_type_events(StructWithCondition, context, stream)
        a = dict(name='a', type=UINT16, value=1, bin_offset=0)
        b = dict(name='b', type=UINT16, value=0xf, bin_offset=2)
        c = dict(name='c', type=UINT16, value=2, bin_offset=4)
        x = dict(type=StructWithCondition,
                 value=dict(a=1, b=0xf, c=2))
        self.assertEqual((STARTEVENT, dict(type=StructWithCondition,
                                           value={})),
                         next(events))
        self.assertEqual((None, a), next(events))
        self.assertEqual((None, b), next(events))
        self.assertEqual((None, c), next(events))
        self.assertEqual((ENDEVENT, x), next(events))
        self.assertEqual(b'', stream.read())
