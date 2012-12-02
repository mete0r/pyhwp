# -*- coding: utf-8 -*-
from unittest import TestCase


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
        from hwp5.dataio import StructType
        from hwp5.dataio import UINT16
        class BasicStruct(object):
            __metaclass__ = StructType

            @staticmethod
            def attributes():
                yield UINT16, 'a'
                yield UINT16, 'b'
        return BasicStruct

    @lazy_property
    def NestedStruct(self):
        from hwp5.dataio import StructType
        from hwp5.dataio import UINT16
        class NestedStruct(object):
            __metaclass__ = StructType

            @staticmethod
            def attributes():
                yield UINT16, 'a'
                yield self.BasicStruct, 's'
                yield UINT16, 'b'
        return NestedStruct

    def test_map_events(self):
        from hwp5.treeop import STARTEVENT, ENDEVENT
        from hwp5.dataio import UINT16
        from hwp5.bintype import bintype_map_events

        bin_item = dict(type=self.BasicStruct)
        events = bintype_map_events(bin_item)

        ev, item = events.next()
        self.assertEquals((STARTEVENT, bin_item), (ev, item))

        ev, item = events.next()
        self.assertEquals((None, dict(name='a', type=UINT16)),
                          (ev, item))

        ev, item = events.next()
        self.assertEquals((None, dict(name='b', type=UINT16)),
                          (ev, item))

        ev, item = events.next()
        self.assertEquals((ENDEVENT, bin_item), (ev, item))


    def test_map_events_nested(self):
        from hwp5.treeop import STARTEVENT, ENDEVENT
        from hwp5.dataio import UINT16
        from hwp5.bintype import bintype_map_events

        bin_item = dict(type=self.NestedStruct)
        events = bintype_map_events(bin_item)

        ev, item = events.next()
        self.assertEquals((STARTEVENT, bin_item), (ev, item))

        ev, item = events.next()
        self.assertEquals((None, dict(name='a', type=UINT16)),
                          (ev, item))

        ev, item = events.next()
        self.assertEquals((STARTEVENT, dict(name='s', type=self.BasicStruct)),
                          (ev, item))

        ev, item = events.next()
        self.assertEquals((None, dict(name='a', type=UINT16)),
                          (ev, item))

        ev, item = events.next()
        self.assertEquals((None, dict(name='b', type=UINT16)),
                          (ev, item))

        ev, item = events.next()
        self.assertEquals((ENDEVENT, dict(name='s', type=self.BasicStruct)),
                          (ev, item))

        ev, item = events.next()
        self.assertEquals((None, dict(name='b', type=UINT16)),
                          (ev, item))

        ev, item = events.next()
        self.assertEquals((ENDEVENT, bin_item), (ev, item))

    def test_map_struct_with_xarray(self):
        from hwp5.treeop import STARTEVENT, ENDEVENT
        from hwp5.dataio import StructType
        from hwp5.dataio import X_ARRAY
        from hwp5.dataio import ref_member
        from hwp5.dataio import UINT16
        from hwp5.bintype import bintype_map_events

        xarray_type = X_ARRAY(self.BasicStruct, ref_member('count'))
        class StructWithXArray(object):
            __metaclass__ = StructType
            @staticmethod
            def attributes():
                yield UINT16, 'count'
                yield dict(type=xarray_type,
                           name='items')
        bin_item = dict(type=StructWithXArray)
        events = bintype_map_events(bin_item)
        self.assertEquals((STARTEVENT,
                           bin_item),
                          events.next())
        self.assertEquals((None,
                           dict(type=UINT16, name='count')),
                          events.next())
        self.assertEquals((STARTEVENT,
                           dict(type=xarray_type,
                                name='items')),
                          events.next())
        self.assertEquals((STARTEVENT,
                           dict(type=self.BasicStruct)),
                          events.next())
        self.assertEquals((None,
                           dict(type=UINT16, name='a')),
                          events.next())
        self.assertEquals((None,
                           dict(type=UINT16, name='b')),
                          events.next())
        self.assertEquals((ENDEVENT,
                           dict(type=self.BasicStruct)),
                          events.next())
        self.assertEquals((ENDEVENT,
                           dict(type=xarray_type,
                                name='items')),
                          events.next())
        self.assertEquals((ENDEVENT,
                           bin_item),
                          events.next())

    def test_filter_with_version(self):
        from hwp5.treeop import STARTEVENT, ENDEVENT
        from hwp5.dataio import StructType
        from hwp5.dataio import UINT16
        from hwp5.bintype import bintype_map_events
        from hwp5.bintype import filter_with_version

        class StructWithVersion(object):
            __metaclass__ = StructType

            @classmethod
            def attributes(cls):
                yield UINT16, 'a'
                yield dict(name='b', type=UINT16, version=(5, 0, 2, 4))

        bin_item = dict(type=StructWithVersion)

        events = bintype_map_events(bin_item)
        events = filter_with_version(events, (5, 0, 0, 0))

        self.assertEquals((STARTEVENT, bin_item), events.next())
        self.assertEquals((None, dict(name='a', type=UINT16)), events.next())
        self.assertEquals((ENDEVENT, bin_item), events.next())

        events = bintype_map_events(bin_item)
        events = filter_with_version(events, (5, 0, 2, 4))
        self.assertEquals((STARTEVENT, bin_item), events.next())
        self.assertEquals((None, dict(name='a', type=UINT16)), events.next())
        self.assertEquals((None, dict(name='b', type=UINT16,
                                      version=(5, 0, 2, 4))), events.next())
        self.assertEquals((ENDEVENT, bin_item), events.next())

    def test_resolve_xarray(self):
        from hwp5.treeop import STARTEVENT, ENDEVENT
        from hwp5.dataio import StructType
        from hwp5.dataio import X_ARRAY
        from hwp5.dataio import UINT16
        from hwp5.dataio import ref_member
        from hwp5.bintype import bintype_map_events
        from hwp5.bintype import static_to_mutable
        from hwp5.bintype import resolve_types

        xarray_type = X_ARRAY(UINT16, ref_member('a'))
        class StructWithXArray(object):
            __metaclass__ = StructType

            @staticmethod
            def attributes():
                yield UINT16, 'a'
                yield dict(name='b',
                           type=xarray_type)

        static_events = bintype_map_events(dict(type=StructWithXArray))
        static_events = list(static_events)

        events = static_to_mutable(iter(static_events))
        events = resolve_types(events, dict())
        ev, struct = events.next()
        self.assertEquals((STARTEVENT, struct), (ev, struct))
        self.assertEquals((None,
                           dict(name='a', type=UINT16)),
                          events.next())
        struct['value'] = dict(a=0)
        self.assertEquals((STARTEVENT,
                           dict(name='b',
                                count=0,
                                type=xarray_type)),
                          events.next())
        self.assertEquals((ENDEVENT,
                           dict(name='b',
                                count=0,
                                type=xarray_type)),
                          events.next())
        self.assertEquals((ENDEVENT, struct),
                          events.next())

        events = static_to_mutable(iter(static_events))
        events = resolve_types(events, dict())
        ev, struct = events.next()
        self.assertEquals((STARTEVENT, struct), (ev, struct))
        self.assertEquals((None,
                           dict(name='a', type=UINT16)),
                          events.next())
        struct['value'] = dict(a=1)
        self.assertEquals((STARTEVENT,
                           dict(name='b',
                                count=1,
                                type=xarray_type)),
                          events.next())
        self.assertEquals((None, dict(type=UINT16)),
                          events.next())
        self.assertEquals((ENDEVENT,
                           dict(name='b',
                                count=1,
                                type=xarray_type)),
                          events.next())
        self.assertEquals((ENDEVENT, struct),
                          events.next())

        events = static_to_mutable(iter(static_events))
        events = resolve_types(events, dict())
        ev, struct = events.next()
        self.assertEquals((STARTEVENT, struct), (ev, struct))
        self.assertEquals((None,
                           dict(name='a', type=UINT16)),
                          events.next())
        struct['value'] = dict(a=2)
        self.assertEquals((STARTEVENT,
                           dict(name='b',
                                count=2,
                                type=xarray_type)),
                          events.next())
        self.assertEquals((None, dict(type=UINT16)),
                          events.next())
        self.assertEquals((None, dict(type=UINT16)),
                          events.next())
        self.assertEquals((ENDEVENT,
                           dict(name='b',
                                count=2,
                                type=xarray_type)),
                          events.next())
        self.assertEquals((ENDEVENT, struct),
                          events.next())

    def test_resolve_xarray_struct(self):
        from hwp5.treeop import STARTEVENT, ENDEVENT
        from hwp5.dataio import StructType
        from hwp5.dataio import X_ARRAY
        from hwp5.dataio import UINT16
        from hwp5.dataio import ref_member
        from hwp5.bintype import bintype_map_events
        from hwp5.bintype import static_to_mutable
        from hwp5.bintype import resolve_types

        xarray_type = X_ARRAY(self.BasicStruct, ref_member('a'))
        class StructWithXArray(object):
            __metaclass__ = StructType

            @staticmethod
            def attributes():
                yield UINT16, 'a'
                yield dict(name='b',
                           type=xarray_type)

        static_events = bintype_map_events(dict(type=StructWithXArray))
        static_events = list(static_events)

        events = static_to_mutable(iter(static_events))
        events = resolve_types(events, dict())
        ev, struct = events.next()
        self.assertEquals((STARTEVENT, struct), (ev, struct))
        self.assertEquals((None,
                           dict(name='a', type=UINT16)),
                          events.next())
        struct['value'] = dict(a=0)
        self.assertEquals((STARTEVENT,
                           dict(name='b', count=0, type=xarray_type)),
                          events.next())
        self.assertEquals((ENDEVENT,
                           dict(name='b', count=0, type=xarray_type)),
                          events.next())
        self.assertEquals((ENDEVENT, struct),
                          events.next())

        events = static_to_mutable(iter(static_events))
        events = resolve_types(events, dict())
        ev, struct = events.next()
        self.assertEquals((STARTEVENT, struct), (ev, struct))
        self.assertEquals((None,
                           dict(name='a', type=UINT16)),
                          events.next())
        struct['value'] = dict(a=1)
        self.assertEquals((STARTEVENT,
                           dict(name='b', count=1, type=xarray_type)),
                          events.next())
        self.assertEquals((STARTEVENT, dict(type=self.BasicStruct)),
                           events.next())
        self.assertEquals((None, dict(name='a', type=UINT16)),
                          events.next())
        self.assertEquals((None, dict(name='b', type=UINT16)),
                          events.next())
        self.assertEquals((ENDEVENT, dict(type=self.BasicStruct)),
                           events.next())
        self.assertEquals((ENDEVENT,
                           dict(name='b', count=1, type=xarray_type)),
                          events.next())
        self.assertEquals((ENDEVENT, struct),
                          events.next())

        events = static_to_mutable(iter(static_events))
        events = resolve_types(events, dict())
        ev, struct = events.next()
        self.assertEquals((STARTEVENT, struct), (ev, struct))
        self.assertEquals((None,
                           dict(name='a', type=UINT16)),
                          events.next())
        struct['value'] = dict(a=2)
        self.assertEquals((STARTEVENT,
                           dict(name='b', count=2, type=xarray_type)),
                          events.next())
        self.assertEquals((STARTEVENT, dict(type=self.BasicStruct)),
                           events.next())
        self.assertEquals((None, dict(name='a', type=UINT16)),
                          events.next())
        self.assertEquals((None, dict(name='b', type=UINT16)),
                          events.next())
        self.assertEquals((ENDEVENT, dict(type=self.BasicStruct)),
                           events.next())
        self.assertEquals((STARTEVENT, dict(type=self.BasicStruct)),
                           events.next())
        self.assertEquals((None, dict(name='a', type=UINT16)),
                          events.next())
        self.assertEquals((None, dict(name='b', type=UINT16)),
                          events.next())
        self.assertEquals((ENDEVENT, dict(type=self.BasicStruct)),
                           events.next())
        self.assertEquals((ENDEVENT,
                           dict(name='b', count=2, type=xarray_type)),
                          events.next())
        self.assertEquals((ENDEVENT, struct),
                          events.next())

    def test_resolve_conditional_simple(self):
        from hwp5.treeop import STARTEVENT, ENDEVENT
        from hwp5.dataio import StructType
        from hwp5.dataio import UINT16
        from hwp5.bintype import bintype_map_events
        from hwp5.bintype import static_to_mutable
        from hwp5.bintype import resolve_types

        def if_a_is_1(context, values):
            return values['a'] == 1

        class StructWithCondition(object):
            __metaclass__ = StructType

            @staticmethod
            def attributes():
                yield UINT16, 'a'
                yield dict(name='b', type=UINT16, condition=if_a_is_1)
                yield UINT16, 'c'

        static_events = bintype_map_events(dict(type=StructWithCondition))
        static_events = list(static_events)

        events = static_to_mutable(iter(static_events))
        events = resolve_types(events, dict())
        ev, struct = events.next()
        self.assertEquals(STARTEVENT, ev)
        self.assertEquals(StructWithCondition, struct['type'])
        self.assertEquals((None, dict(name='a', type=UINT16)),
                          events.next())
        struct['value'] = dict(a=0)
        self.assertEquals((None, dict(name='c', type=UINT16)),
                          events.next())
        self.assertEquals((ENDEVENT,
                           dict(struct,
                                value=dict(a=0))),
                          events.next())

        events = static_to_mutable(iter(static_events))
        events = resolve_types(events, dict())
        ev, struct = events.next()
        self.assertEquals(STARTEVENT, ev)
        self.assertEquals(StructWithCondition, struct['type'])
        self.assertEquals((None, dict(name='a', type=UINT16)),
                          events.next())
        struct['value'] = dict(a=1)
        self.assertEquals((None,
                           dict(name='b',
                                type=UINT16)),
                          events.next())
        self.assertEquals((None, dict(name='c', type=UINT16)),
                          events.next())
        self.assertEquals((ENDEVENT,
                           dict(struct,
                                value=dict(a=1))),
                          events.next())

    def test_resolve_conditional_struct(self):
        from hwp5.treeop import STARTEVENT, ENDEVENT
        from hwp5.dataio import StructType
        from hwp5.dataio import UINT16
        from hwp5.bintype import bintype_map_events
        from hwp5.bintype import static_to_mutable
        from hwp5.bintype import resolve_types

        def if_a_is_1(context, values):
            return values['a'] == 1

        class StructWithCondition(object):
            __metaclass__ = StructType

            @staticmethod
            def attributes():
                yield UINT16, 'a'
                yield dict(name='b', type=self.BasicStruct, condition=if_a_is_1)
                yield UINT16, 'c'

        static_events = bintype_map_events(dict(type=StructWithCondition))
        static_events = list(static_events)

        events = static_to_mutable(iter(static_events))
        events = resolve_types(events, dict())
        ev, struct = events.next()
        self.assertEquals(STARTEVENT, ev)
        self.assertEquals(StructWithCondition, struct['type'])
        self.assertEquals((None, dict(name='a', type=UINT16)),
                          events.next())
        struct['value'] = dict(a=0)
        self.assertEquals((None, dict(name='c', type=UINT16)),
                          events.next())
        self.assertEquals((ENDEVENT,
                           dict(struct,
                                value=dict(a=0))),
                          events.next())

        events = static_to_mutable(iter(static_events))
        events = resolve_types(events, dict())
        ev, struct = events.next()
        self.assertEquals(STARTEVENT, ev)
        self.assertEquals(StructWithCondition, struct['type'])
        self.assertEquals((None, dict(name='a', type=UINT16)),
                          events.next())
        struct['value'] = dict(a=1)
        self.assertEquals((STARTEVENT,
                           dict(name='b',
                                type=self.BasicStruct)),
                          events.next())
        self.assertEquals((None, dict(name='a', type=UINT16)),
                          events.next())
        self.assertEquals((None, dict(name='b', type=UINT16)),
                          events.next())
        self.assertEquals((ENDEVENT,
                           dict(name='b',
                                type=self.BasicStruct)),
                          events.next())
        self.assertEquals((None, dict(name='c', type=UINT16)),
                          events.next())
        self.assertEquals((ENDEVENT,
                           dict(struct,
                                value=dict(a=1))),
                          events.next())

    def test_resolve_selective_type(self):
        from hwp5.treeop import STARTEVENT, ENDEVENT
        from hwp5.dataio import StructType
        from hwp5.dataio import SelectiveType
        from hwp5.dataio import ref_member
        from hwp5.dataio import UINT16
        from hwp5.bintype import bintype_map_events
        from hwp5.bintype import static_to_mutable
        from hwp5.bintype import resolve_types

        class StructWithSelectiveType(object):
            __metaclass__ = StructType

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
        events = resolve_types(events, dict())
        ev, struct = events.next()
        self.assertEquals(STARTEVENT, ev)
        self.assertEquals(StructWithSelectiveType, struct['type'])
        self.assertEquals((None, dict(name='a', type=UINT16)),
                          events.next())
        struct['value'] = dict(a=0)
        self.assertEquals((None, dict(name='b', type=UINT16)),
                          events.next())
        self.assertEquals((None, dict(name='c', type=UINT16)),
                          events.next())
        self.assertEquals((ENDEVENT,
                           dict(struct,
                                value=dict(a=0))),
                          events.next())

        events = static_to_mutable(iter(static_events))
        events = resolve_types(events, dict())
        ev, struct = events.next()
        self.assertEquals(STARTEVENT, ev)
        self.assertEquals(StructWithSelectiveType, struct['type'])
        self.assertEquals((None, dict(name='a', type=UINT16)),
                          events.next())
        struct['value'] = dict(a=1)
        self.assertEquals((STARTEVENT,
                           dict(name='b',
                                type=self.BasicStruct)),
                          events.next())
        self.assertEquals((None, dict(name='a', type=UINT16)),
                          events.next())
        self.assertEquals((None, dict(name='b', type=UINT16)),
                          events.next())
        self.assertEquals((ENDEVENT,
                           dict(name='b',
                                type=self.BasicStruct)),
                          events.next())
        self.assertEquals((None, dict(name='c', type=UINT16)),
                          events.next())
        self.assertEquals((ENDEVENT,
                           dict(struct,
                                value=dict(a=1))),
                          events.next())

    def test_resolve_values_from_stream(self):
        assertEquals = self.assertEquals
        from hwp5.treeop import STARTEVENT, ENDEVENT
        from hwp5.dataio import UINT16
        from hwp5.bintype import bintype_map_events
        from hwp5.bintype import resolve_values_from_stream

        from StringIO import StringIO
        stream = StringIO('\x00\x01\x00\x02')
        resolve_values = resolve_values_from_stream(stream)

        bin_item = dict(type=self.BasicStruct)
        events = bintype_map_events(bin_item)
        events = resolve_values(events)

        assertEquals((STARTEVENT, bin_item), events.next())
        assertEquals((None,
                      dict(name='a', type=UINT16, bin_offset=0, value=256)),
                     events.next())
        assertEquals((None,
                      dict(name='b', type=UINT16, bin_offset=2, value=512)),
                     events.next())
        assertEquals((ENDEVENT, bin_item), events.next())

        from hwp5.dataio import StructType
        from hwp5.dataio import BSTR
        class StructWithBSTR(object):
            __metaclass__ = StructType

            @staticmethod
            def attributes():
                yield BSTR, 'name'

        stream = StringIO('\x02\x00\x00\x01\x00\x02')
        resolve_values = resolve_values_from_stream(stream)
        bin_item = dict(type=StructWithBSTR)
        events = bintype_map_events(bin_item)
        events = resolve_values(events)
        assertEquals((STARTEVENT, bin_item), events.next())
        assertEquals((None,
                      dict(name='name', type=BSTR, bin_offset=0,
                           value=u'\u0100\u0200')),
                     events.next())
        assertEquals((ENDEVENT, bin_item), events.next())

        from hwp5.binmodel import ParaTextChunks
        class StructWithParaTextChunks(object):
            __metaclass__ = StructType

            @staticmethod
            def attributes():
                yield ParaTextChunks, 'texts'

        stream = StringIO('\x20\x00\x21\x00\x22\x00')
        resolve_values = resolve_values_from_stream(stream)
        bin_item = dict(type=StructWithParaTextChunks)
        events = bintype_map_events(bin_item)
        events = resolve_values(events)
        assertEquals((STARTEVENT, bin_item), events.next())
        assertEquals((None,
                      dict(name='texts', type=ParaTextChunks,
                           bin_offset=0,
                           value=[((0, 3), u'\u0020\u0021\u0022')])),
                     events.next())
        assertEquals((ENDEVENT, bin_item), events.next())

    def test_collect_values(self):
        from hwp5.treeop import STARTEVENT, ENDEVENT
        from hwp5.dataio import UINT16
        from hwp5.bintype import bintype_map_events
        from hwp5.bintype import resolve_values_from_stream
        from hwp5.bintype import collect_values
        from StringIO import StringIO

        stream = StringIO('\x01\x00\x01\x01\x02\x01\x02\x00')
        resolve_values = resolve_values_from_stream(stream)

        bin_item = dict(type=self.NestedStruct)
        events = bintype_map_events(bin_item)
        events = resolve_values(events)
        events = collect_values(events)

        a = dict(name='a', type=UINT16, bin_offset=0, value=1)
        s_a = dict(name='a', type=UINT16, bin_offset=2, value=0x101)
        s_b = dict(name='b', type=UINT16, bin_offset=4, value=0x102)
        b = dict(name='b', type=UINT16, bin_offset=6, value=2)
        s = dict(name='s', type=self.BasicStruct,
                 value=dict(a=0x101, b=0x102))
        x = dict(type=self.NestedStruct,
                 value=dict(a=1, s=dict(a=0x101, b=0x102), b=2))
        self.assertEquals((STARTEVENT, bin_item), events.next())
        self.assertEquals((None, a), events.next())
        self.assertEquals((STARTEVENT, dict(name='s', type=self.BasicStruct,
                                            value=dict())),
                           events.next())
        self.assertEquals((None, s_a), events.next())
        self.assertEquals((None, s_b), events.next())
        self.assertEquals((ENDEVENT, s), events.next())
        self.assertEquals((None, b), events.next())
        self.assertEquals((ENDEVENT, x), events.next())


class TestReadEvents(TestCase):
    def test_struct_with_condition(self):
        from hwp5.treeop import STARTEVENT, ENDEVENT
        from hwp5.dataio import UINT16
        from hwp5.dataio import StructType
        from hwp5.bintype import read_type_events
        from StringIO import StringIO

        def if_a_is_1(context, values):
            return values['a'] == 1

        class StructWithCondition(object):
            __metaclass__ = StructType

            @staticmethod
            def attributes():
                yield UINT16, 'a'
                yield dict(name='b', type=UINT16, condition=if_a_is_1)
                yield UINT16, 'c'

        context = dict()

        # if a = 0
        stream = StringIO('\x00\x00\x02\x00')
        events = read_type_events(StructWithCondition, context, stream)
        a = dict(name='a', type=UINT16, value=0, bin_offset=0)
        c = dict(name='c', type=UINT16, value=2, bin_offset=2)
        self.assertEquals((STARTEVENT, dict(type=StructWithCondition,
                                           value=dict())),
                          events.next())
        self.assertEquals((None, a), events.next())
        self.assertEquals((None, c), events.next())
        self.assertEquals((ENDEVENT, dict(type=StructWithCondition,
                                          value=dict(a=0, c=2))),
                          events.next())
        self.assertEquals('', stream.read())

        # if a = 1
        stream = StringIO('\x01\x00\x0f\x00\x02\x00')
        events = read_type_events(StructWithCondition, context, stream)
        a = dict(name='a', type=UINT16, value=1, bin_offset=0)
        b = dict(name='b', type=UINT16, value=0xf, bin_offset=2)
        c = dict(name='c', type=UINT16, value=2, bin_offset=4)
        x = dict(type=StructWithCondition,
                 value=dict(a=1, b=0xf, c=2))
        self.assertEquals((STARTEVENT, dict(type=StructWithCondition,
                                            value={})),
                          events.next())
        self.assertEquals((None, a), events.next())
        self.assertEquals((None, b), events.next())
        self.assertEquals((None, c), events.next())
        self.assertEquals((ENDEVENT, x), events.next())
        self.assertEquals('', stream.read())
