from unittest import TestCase

from hwp5.dataio import INT32, ARRAY, N_ARRAY, BSTR, Struct
from hwp5.dataio import typed_struct_attributes
class TestArray(TestCase):
    def test_new(self):
        t1 = ARRAY(INT32, 3)
        t2 = ARRAY(INT32, 3)
        assert t1 is t2

        assert N_ARRAY(INT32, INT32) is N_ARRAY(INT32, INT32)

    def test_BSTR(self):
        assert type(BSTR(u'abc')) is unicode

    def test_hello(self):
        assert INT32.basetype is int

    def test_slots(self):
        a = INT32()
        self.assertRaises(Exception, setattr, a, 'randomattr', 1)

class TestTypedAttributes(TestCase):

    def test_typed_struct_attributes(self):
        class SomeRandomStruct(Struct):
            @staticmethod
            def attributes():
                yield INT32, 'a'
                yield BSTR, 'b'
                yield ARRAY(INT32, 3), 'c'

        attributes = dict(a=1, b=u'abc', c=(4,5,6))
        typed_attributes = typed_struct_attributes(SomeRandomStruct, attributes, dict())
        typed_attributes = list(typed_attributes)
        expected = [dict(name='a', type=INT32, value=1),
                    dict(name='b', type=BSTR, value='abc'),
                    dict(name='c', type=ARRAY(INT32, 3), value=(4,5,6))]
        self.assertEquals(expected, typed_attributes)

class TestStructType(TestCase):
    def test_assign_enum_flags_name(self):
        from hwp5.dataio import StructType, Enum, Flags, UINT16
        class Foo(object):
            __metaclass__ = StructType
            bar = Enum()
            baz = Flags(UINT16)
        self.assertEquals('bar', Foo.bar.__name__)
        self.assertEquals('baz', Foo.baz.__name__)

    def test_parse_members(self):
        from hwp5.dataio import StructType
        from hwp5.dataio import UINT8, UINT16, UINT32

        class A(object):
            __metaclass__ = StructType
            @classmethod
            def attributes(cls):
                yield UINT8, 'uint8'
                yield UINT16, 'uint16'
                yield UINT32, 'uint32'

        values = dict(uint8=8, uint16=16, uint32=32)
        def getvalue(member):
            return values[member['name']]
        context = dict()
        result = list(A.parse_members(context, getvalue))
        self.assertEquals([dict(name='uint8', type=UINT8, value=8),
                           dict(name='uint16', type=UINT16, value=16),
                           dict(name='uint32', type=UINT32, value=32)], result)

    def test_parse_members_condition(self):
        from hwp5.dataio import StructType
        from hwp5.dataio import UINT8, UINT16, UINT32

        def uint32_is_32(context, values):
            return values['uint32'] == 32
        class A(object):
            __metaclass__ = StructType
            @classmethod
            def attributes(cls):
                yield UINT8, 'uint8'
                yield UINT16, 'uint16'
                yield UINT32, 'uint32'
                yield dict(type=UINT32, name='extra', condition=uint32_is_32)

        values = dict(uint8=8, uint16=16, uint32=32, extra=666)
        def getvalue(member):
            return values[member['name']]
        context = dict()
        result = list(A.parse_members(context, getvalue))
        self.assertEquals([dict(name='uint8', type=UINT8, value=8),
                           dict(name='uint16', type=UINT16, value=16),
                           dict(name='uint32', type=UINT32, value=32),
                           dict(name='extra', type=UINT32, value=666,
                                condition=uint32_is_32)],
                          result)

    def test_parse_members_empty(self):
        from hwp5.dataio import StructType

        class A(object):
            __metaclass__ = StructType

        value = dict()
        def getvalue(member):
            return value[member['name']]
        context = dict()
        result = list(A.parse_members_with_inherited(context, getvalue))
        self.assertEquals([], result)

    def test_parse_members_inherited(self):
        from hwp5.dataio import StructType
        from hwp5.dataio import UINT8, UINT16, UINT32
        from hwp5.dataio import INT8, INT16, INT32

        class A(object):
            __metaclass__ = StructType
            @classmethod
            def attributes(cls):
                yield UINT8, 'uint8'
                yield UINT16, 'uint16'
                yield UINT32, 'uint32'

        class B(A):
            @classmethod
            def attributes(cls):
                yield INT8, 'int8'
                yield INT16, 'int16'
                yield INT32, 'int32'

        value = dict(uint8=8, uint16=16, uint32=32,
                     int8=-1, int16=-16, int32=-32)
        def getvalue(member):
            return value[member['name']]
        context = dict()
        result = list(B.parse_members_with_inherited(context, getvalue))
        self.assertEquals([dict(name='uint8', type=UINT8, value=8),
                           dict(name='uint16', type=UINT16, value=16),
                           dict(name='uint32', type=UINT32, value=32),
                           dict(name='int8', type=INT8, value=-1),
                           dict(name='int16', type=INT16, value=-16),
                           dict(name='int32', type=INT32, value=-32)],
                          result)


class TestEnumType(TestCase):
    def test_enum(self):
        from hwp5.dataio import EnumType
        FooEnum = EnumType('FooEnum', (int,), dict(items=['a', 'b', 'c'], moreitems=dict(d=1, e=4)))
        self.assertEquals(0, FooEnum.a)
        self.assertEquals(1, FooEnum.b)
        self.assertEquals(2, FooEnum.c)
        self.assertEquals(1, FooEnum.d)
        self.assertEquals(4, FooEnum.e)
        self.assertEquals('FooEnum.a', repr(FooEnum(0)))
        self.assertEquals('FooEnum.b', repr(FooEnum(1)))
        self.assertEquals('FooEnum.e', repr(FooEnum(4)))
        self.assertEquals('b', FooEnum.name_for(1))
        self.assertRaises(AttributeError, getattr, FooEnum(0), 'items')
        self.assertRaises(AttributeError, getattr, FooEnum(0), 'moreitems')
        self.assertTrue(isinstance(FooEnum.a, FooEnum))
        self.assertTrue(FooEnum(0) is FooEnum(0))
        self.assertTrue(FooEnum(0) is FooEnum.a)

class TestFlags(TestCase):
    def test_parse_args(self):
        from hwp5.dataio import _parse_flags_args
        x = list(_parse_flags_args([0, 1, long, 'bit01']))
        bit01 = ('bit01', (0, 1, long))
        self.assertEquals([bit01], x)

        x = list(_parse_flags_args([2, 3, 'bit23']))
        bit23 = ('bit23', (2, 3, int))
        self.assertEquals([bit23], x)

        x = list(_parse_flags_args([4, long, 'bit4']))
        bit4 = ('bit4', (4, 4, long))
        self.assertEquals([bit4], x)

        x = list(_parse_flags_args([5, 'bit5']))
        bit5 = ('bit5', (5, 5, int))

        x = list(_parse_flags_args([0, 1, long, 'bit01',
                                    2, 3, 'bit23', 
                                    4, long, 'bit4',
                                    5, 'bit5']))
        self.assertEquals([bit01, bit23, bit4, bit5], x)

    def test_basetype(self):
        from hwp5.dataio import UINT32
        from hwp5.dataio import Flags
        MyFlags = Flags(UINT32)
        self.assertEquals(UINT32, MyFlags.basetype)

    def test_bitfields(self):
        from hwp5.dataio import UINT32
        from hwp5.dataio import Flags
        from hwp5.dataio import Enum
        MyEnum = Enum(a=1, b=2)
        MyFlags = Flags(UINT32, 0, 1, 'field0',
                                2, 4, MyEnum, 'field2')
        bitfields = MyFlags.bitfields
        f = bitfields['field0']
        self.assertEquals((0, 1, int),
                          (f.lsb, f.msb, f.valuetype))
        f = bitfields['field2']
        self.assertEquals((2, 4, MyEnum),
                          (f.lsb, f.msb, f.valuetype))

    @property
    def ByteFlags(self):
        from hwp5.dataio import BYTE
        from hwp5.dataio import Flags
        return Flags(BYTE,
                     0, 3, 'low',
                     4, 7, 'high')

    def test_read(self):
        ByteFlags = self.ByteFlags
        from StringIO import StringIO
        stream = StringIO('\xf0')
        flags = ByteFlags.read(stream, dict())
        self.assertTrue(isinstance(flags, ByteFlags))

    def test_dictvalue(self):
        flags = self.ByteFlags(0xf0)
        self.assertEquals(dict(low=0, high=0xf),
                          flags.dictvalue())


class TestReadStruct(TestCase):

    def test_read_parse_error(self):
        from hwp5.dataio import StructType
        from hwp5.dataio import INT16
        from hwp5.dataio import read_struct_attributes_with_offset
        from hwp5.dataio import ParseError

        class Foo(object):
            __metaclass__ = StructType

            def attributes():
                yield INT16, 'a'
            attributes = staticmethod(attributes)

        from StringIO import StringIO
        stream = StringIO()

        record = dict()
        context = dict(record=record)
        members = read_struct_attributes_with_offset(Foo, context, stream)
        try:
            list(members)
            assert False, 'ParseError expected'
        except ParseError, e:
            self.assertEquals(Foo, e.context[-1]['model'])
            self.assertEquals('a', e.context[-1]['member'])
