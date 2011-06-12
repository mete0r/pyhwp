from unittest import TestCase

from .dataio import INT32, ARRAY, N_ARRAY, BSTR, Struct
from .dataio import match_attribute_types, typed_struct_attributes
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
    def test_match_attributes_types(self):
        types = ((v, k) for k, v in dict(a=int, b=long).items())
        values = dict(a=1, b=2, c='abc')
        matched = match_attribute_types(types, values)
        matched = list(matched)
        expected = dict(a=(int,1), b=(long,2)).items()
        self.assertEquals(set(expected), set(matched))

    def test_typed_struct_attributes(self):
        class SomeRandomStruct(Struct):
            @staticmethod
            def attributes(context):
                yield INT32, 'a'
                yield BSTR, 'b'
                yield ARRAY(INT32, 3), 'c'

        attributes = dict(a=1, b=u'abc', c=(4,5,6))
        typed_attributes = typed_struct_attributes(SomeRandomStruct, attributes, dict())
        typed_attributes = list(typed_attributes)
        expected = dict(a=(INT32, 1), b=(BSTR,u'abc'), c=(ARRAY(INT32, 3),(4,5,6))).items()
        self.assertEquals(set(expected), set(typed_attributes))

class TestStructType(TestCase):
    def test_assign_enum_flags_name(self):
        from .dataio import StructType, Enum, Flags, UINT16
        class Foo(object):
            __metaclass__ = StructType
            bar = Enum()
            baz = Flags(UINT16)
        self.assertEquals('bar', Foo.bar.__name__)
        self.assertEquals('baz', Foo.baz.__name__)

class TestEnumType(TestCase):
    def test_enum(self):
        from .dataio import EnumType
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
        from .dataio import _parse_flags_args
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
