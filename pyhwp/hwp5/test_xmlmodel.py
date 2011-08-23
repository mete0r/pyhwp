from unittest import TestCase

from .dataio import Struct
from .dataio import INT32, BSTR
from .xmlmodel import element
from xml.sax.saxutils import XMLGenerator
import sys, logging

class TestHello(TestCase):
    def test_hello(self):
        context = dict(logging=logging)
        xmlgen = XMLGenerator(sys.stdout, 'utf-8')
        class SomeStruct(Struct):
            @staticmethod
            def attributes(context):
                yield INT32, 'a'
                yield BSTR, 'b'
        class SomeStruct2(Struct):
            @staticmethod
            def attributes(context):
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
        from .xmlmodel import xmlattr_uniqnames
        a = [('a', 1), ('b', 2)]
        self.assertEquals([('a', 1), ('b', 2)], list(xmlattr_uniqnames(a)))

        a = [('a', 1), ('a', 2)]
        result = xmlattr_uniqnames(a)
        self.assertRaises(Exception, list, result)

class TestTreeEvents(TestCase):
    def test_tree_events(self):
        from .binmodel import STARTEVENT, ENDEVENT
        from .xmlmodel import build_subtree, tree_events
        event_prefixed_items = [ (STARTEVENT, 'a'), (ENDEVENT, 'a') ]
        rootitem, childs = build_subtree(iter(event_prefixed_items[1:]))
        self.assertEquals('a', rootitem)
        self.assertEquals(0, len(childs))

        event_prefixed_items = [ (STARTEVENT, 'a'), (STARTEVENT, 'b'), (ENDEVENT, 'b'), (ENDEVENT, 'a') ]
        self.assertEquals( ('a', [('b', [])]), build_subtree(iter(event_prefixed_items[1:])))

        event_prefixed_items = [
            (STARTEVENT, 'a'),
                (STARTEVENT, 'b'),
                    (STARTEVENT, 'c'), (ENDEVENT, 'c'),
                    (STARTEVENT, 'd'), (ENDEVENT, 'd'),
                (ENDEVENT, 'b'),
            (ENDEVENT, 'a')]

        result = build_subtree(iter(event_prefixed_items[1:]))
        self.assertEquals( ('a', [('b', [('c', []), ('d', [])])]), result)

        back = list(tree_events(*result))
        self.assertEquals(event_prefixed_items, back)

