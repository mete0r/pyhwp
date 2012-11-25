from unittest import TestCase
import logging
from hwp5.dataio import Struct
from hwp5.dataio import INT32, BSTR
from hwp5.xmlformat import element


class TestHello(TestCase):
    def test_hello(self):
        from hwp5.treeop import STARTEVENT
        from hwp5.treeop import ENDEVENT

        context = dict(logging=logging)
        class SomeStruct(Struct):
            @staticmethod
            def attributes():
                yield INT32, 'a'
                yield BSTR, 'b'
        class SomeStruct2(Struct):
            @staticmethod
            def attributes():
                yield SomeStruct, 'somestruct'
        result = element(context, (SomeStruct2, dict(somestruct=dict(a=1, b=u'b'))))
        result = list(result)
        #for x in result: x[0](*x[1:])
        expected = [
                (STARTEVENT, ('SomeStruct2', dict())),
                (STARTEVENT, ('SomeStruct', {'attribute-name': 'somestruct',
                                             'a': '1', 'b': 'b'})),
                (ENDEVENT, 'SomeStruct'),
                (ENDEVENT, 'SomeStruct2'),
                ]
        self.assertEquals(expected, result)

        result = element(context, (SomeStruct, dict(a=1, b=u'b', c=dict(foo=1))))
        result = list(result)
        #for x in result: x[0](*x[1:])
        expected = [
                (STARTEVENT, ('SomeStruct', dict(a='1', b='b'))),
                (STARTEVENT, ('dict', {'attribute-name': 'c', 'foo': '1'})),
                (ENDEVENT, 'dict'),
                (ENDEVENT, 'SomeStruct')
                ]
        self.assertEquals(expected, result)

    def test_xmlattr_uniqnames(self):
        from hwp5.xmlformat import xmlattr_uniqnames
        a = [('a', 1), ('b', 2)]
        self.assertEquals([('a', 1), ('b', 2)], list(xmlattr_uniqnames(a)))

        a = [('a', 1), ('a', 2)]
        result = xmlattr_uniqnames(a)
        self.assertRaises(Exception, list, result)

