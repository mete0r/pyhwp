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

from .xmlmodel import make_ranged_shapes, split_and_shape
class TestShapedText(TestCase):
    def test_make_shape_range(self):
        charshapes = [(0, 'A'), (4, 'B'), (6, 'C'), (10, 'D')]
        ranged_shapes = make_ranged_shapes(charshapes)
        self.assertEquals([((0, 4), 'A'), ((4, 6), 'B'), ((6, 10), 'C'), ((10, 0x7fffffff), 'D')], list(ranged_shapes))

    def test_split(self):
        chunks = [((0, 3), None, 'aaa'), ((3, 6), None, 'bbb'), ((6, 9), None, 'ccc'), ((9, 12), None, 'ddd')]
        charshapes = [(0, 'A'), (4, 'B'), (6, 'C'), (10, 'D')]
        shaped_chunks = split_and_shape(iter(chunks), make_ranged_shapes(charshapes))
        shaped_chunks = list(shaped_chunks)
        self.assertEquals([
            ((0,3), ('A',None), 'aaa'),
            ((3,4), ('A',None), 'b'),
            ((4,6), ('B',None), 'bb'),
            ((6,9), ('C',None), 'ccc'),
            ((9, 10), ('C',None), 'd'),
            ((10, 12), ('D',None), 'dd')],
                shaped_chunks)

        # split twice
        chunks = [((0, 112), None, 'x'*112)]
        charshapes = [(0, 'a'), (3, 'b'), (5,'c')]
        linesegs = [(0, 'A'), (51,'B'), (103,'C')]
        shaped = split_and_shape(iter(chunks), make_ranged_shapes(charshapes))
        shaped = list(shaped)
        self.assertEquals([((0, 3), ('a', None), 'xxx'), ((3, 5), ('b',None), 'xx'), ((5,112), ('c',None), 'x'*107)], shaped)
        lines = split_and_shape(iter(shaped), make_ranged_shapes(linesegs))
        lines = list(lines)
        self.assertEquals([
            ((0,3), ('A', ('a', None)), 'xxx'), 
            ((3,5), ('A', ('b', None)), 'xx'), 
            ((5,51), ('A', ('c', None)), 'x'*(51-5)), 
            ((51,103), ('B', ('c', None)), 'x'*(103-51)), 
            ((103,112), ('C', ('c', None)), 'x'*(112-103)), ], lines)

from .xmlmodel import line_segmented
class TestLineSeg(TestCase):
    def test_line_segmented(self):
        chunks = [((0, 3), None, 'aaa'), ((3, 6), None, 'bbb'), ((6, 9), None, 'ccc'), ((9, 12), None, 'ddd')]
        linesegs = [(0, 'A'), (4, 'B'), (6, 'C'), (10, 'D')]
        lines = line_segmented(iter(chunks), make_ranged_shapes(linesegs))
        lines = list(lines)
        self.assertEquals([ ('A', [((0, 3), None, 'aaa'), ((3,4), None, 'b')]), ('B', [((4,6),None,'bb')]), ('C', [((6,9),None,'ccc'), ((9,10),None,'d')]), ('D', [((10,12),None,'dd')]) ], lines)

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

