from unittest import TestCase
import sys, logging
from xml.sax.saxutils import XMLGenerator
from hwp5.dataio import Struct
from hwp5.dataio import INT32, BSTR
from hwp5.xmlformat import element


class TestHello(TestCase):
    def test_hello(self):
        context = dict(logging=logging)
        xmlgen = XMLGenerator(sys.stdout, 'utf-8')
        class SomeStruct(Struct):
            @staticmethod
            def attributes():
                yield INT32, 'a'
                yield BSTR, 'b'
        class SomeStruct2(Struct):
            @staticmethod
            def attributes():
                yield SomeStruct, 'somestruct'
        result = element(context, xmlgen, (SomeStruct2, dict(somestruct=dict(a=1, b=u'b'))))
        result = list(result)
        #for x in result: x[0](*x[1:])
        expected = [
                (xmlgen.startElement, 'SomeStruct2', dict()),
                (xmlgen.startElement, 'SomeStruct', {'attribute-name':'somestruct', 'a':'1', 'b':'b'}),
                (xmlgen.endElement, 'SomeStruct'),
                (xmlgen.endElement, 'SomeStruct2'),
                ]
        self.assertEquals(expected, result)

        result = element(context, xmlgen, (SomeStruct, dict(a=1, b=u'b', c=dict(foo=1))))
        result = list(result)
        #for x in result: x[0](*x[1:])
        expected = [
                (xmlgen.startElement, 'SomeStruct', dict(a='1', b='b')),
                (xmlgen.startElement, 'dict', {'attribute-name':'c', 'foo':'1'}),
                (xmlgen.endElement, 'dict'),
                (xmlgen.endElement, 'SomeStruct')
                ]
        self.assertEquals(expected, result)

    def test_xmlattr_uniqnames(self):
        from hwp5.xmlformat import xmlattr_uniqnames
        a = [('a', 1), ('b', 2)]
        self.assertEquals([('a', 1), ('b', 2)], list(xmlattr_uniqnames(a)))

        a = [('a', 1), ('a', 2)]
        result = xmlattr_uniqnames(a)
        self.assertRaises(Exception, list, result)

