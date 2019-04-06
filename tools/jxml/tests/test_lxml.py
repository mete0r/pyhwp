# -*- coding: utf-8 -*-
from __future__ import with_statement

import os.path
import sys
import unittest
from unittest import TestCase

from lxml import etree
from lxml.etree import ElementTree
from lxml.etree import Element
from lxml.etree import SubElement
from lxml.etree import QName


class ElementTreeTest(TestCase):

    def test_etree_parse(self):
        with open('sample.xml') as f:
            et = etree.parse(f)
        et = etree.parse('sample.xml')

    def test_etree_fromstring(self):
        with open('sample.xml') as f:
            text = f.read()
        et = etree.fromstring(text)

    def test_etree_from_file(self):
        with open('sample.xml') as f:
            et = ElementTree(file=f)
        root = et.getroot()
        self.assertEqual('{http://example.tld}document', root.tag)
        self.assertEqual('x', root.prefix)
        self.assertTrue('x' in root.nsmap)

        with open('hello.xml') as f:
            et = ElementTree(file=f)
        root = et.getroot()
        self.assertEqual('hello', root.tag)
        self.assertEqual(None, root.prefix)
        self.assertEqual({}, root.nsmap)

    def test_etree_tostring(self):
        with open('sample.xml') as f:
            et = etree.parse(f)
        etree.tostring(et, encoding='utf-8', xml_declaration=True)
        etree.tostring(et.getroot()[0], encoding='utf-8', xml_declaration=True)

    def test_from_element(self):
        elem = Element('document')
        tree = ElementTree(elem)
        self.assertEqual('document', tree.getroot().tag)

        with open('sample.xml') as f:
            et = ElementTree(file=f)
        root = et.getroot()

        tree = ElementTree(root)
        self.assertEqual(root.base, tree.getroot().base)
        self.assertEqual(et.docinfo.URL, tree.docinfo.URL)

    def test_docinfo(self):
        with open('sample.xml') as f:
            et = etree.parse(f)
        import os.path
        self.assertEqual(os.path.abspath('sample.xml'), et.docinfo.URL)
        self.assertEqual('', et.docinfo.doctype)
        self.assertEqual('utf-8', et.docinfo.encoding)
        self.assertEqual(None, et.docinfo.externalDTD)
        self.assertEqual(None, et.docinfo.internalDTD)
        self.assertEqual(None, et.docinfo.public_id)
        self.assertEqual('document', et.docinfo.root_name)
        self.assertFalse(et.docinfo.standalone)
        self.assertEqual(None, et.docinfo.system_url)
        self.assertEqual('1.0', et.docinfo.xml_version)

        et.docinfo.URL = 'http://example.tld'
        self.assertEqual('http://example.tld', et.docinfo.URL)

    def test_parser(self):
        pass

    def test__copy__(self):
        pass

    def test__deepcopy__(self):
        pass

    def test_setroot(self):
        from lxml.etree import XML
        a = XML('<a />').getroottree()
        b = XML('<b />').getroottree()
        a._setroot(b.getroot())
        self.assertEqual('b', a.getroot().tag)

    def test_find(self):
        pass

    def test_findall(self):
        pass

    def test_findtext(self):
        pass

    def test_getiterator(self):
        pass

    def test_getpath(self):
        pass

    def test_getroot(self):
        with open('sample.xml') as f:
            et = etree.parse(f)
        tree = etree.parse('sample.xml')
        root = tree.getroot()
        self.assertEqual('{http://example.tld}document', root.tag)

    def test_iter(self):
        pass

    def test_iterfind(self):
        pass

    def test_parse(self):
        pass

    def test_relaxng(self):
        pass

    def test_write(self):
        with open('sample.xml') as f:
            tree = etree.parse(f)

        import tempfile
        import os
        fd, name = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'w') as f:
                tree.write(f)
            with open(name) as f:
                tree2 = etree.parse(f)
        finally:
            os.unlink(name)
        self.assertEqual(tree.getroot().tag, tree2.getroot().tag)

    def test_write_c14n(self):
        pass

    def test_xinclude(self):
        pass

    def test_xmlschema(self):
        pass

    def test_xpath(self):
        with open('sample.xml') as f:
            et = etree.parse(f)
        tree = etree.parse('sample.xml')

        nsmap = dict(x='http://example.tld')

        # element
        result = tree.xpath('//x:paragraph', namespaces=nsmap)
        self.assertEqual(1, len(result))
        self.assertEqual('{http://example.tld}paragraph',
                          result[0].tag)

        # attribute
        result = tree.xpath('@version', namespaces=nsmap)
        self.assertEqual(['1.0'], result)

        # string
        result = tree.xpath('"foo"', namespaces=nsmap)
        self.assertEqual('foo', result)

        # number expression
        result = tree.xpath('1', namespaces=nsmap)
        self.assertEqual(1.0, result)

        result = tree.xpath('"1.0"', namespaces=nsmap)
        # should be string, but alas, it returns a number in jxml
        if sys.platform.startswith('java'):
            self.assertEqual(1.0, result)
        else:
            self.assertEqual('1.0', result)

    def test_xslt(self):
        tree = etree.XML('<hello />').getroottree()
        with open('xsl/import-test.xsl') as f:
            xsl_tree = etree.parse(f)
        result = tree.xslt(xsl_tree)
        self.assertEqual('world', result.getroot().tag)


class ElementTest(TestCase):

    def setUp(self):
        with open('sample.xml') as f:
            self.et = ElementTree(file=f)
        self.root = self.et.getroot()

    def tearDown(self):
        pass

    def test_Element(self):
        elem = Element('document', dict(a='1', b='2'), c='3')
        self.assertEqual('document', elem.tag)
        self.assertEqual(dict(a='1', b='2', c='3'),
                          elem.attrib)

        nsmap = dict(a='http://a.example.tld', c='http://c.example.tld')
        elem = Element('{http://a.example.tld}document',
                       {'{http://a.example.tld}a': '1',
                        '{http://b.example.tld}a': '2',
                        'a': '3'},
                       nsmap)

        self.assertEqual('a', elem.prefix)
        self.assertEqual('{http://a.example.tld}document', elem.tag)
        self.assertEqual(nsmap['a'], elem.nsmap['a'])
        self.assertEqual(nsmap['c'], elem.nsmap['c'])
        self.assertTrue('http://b.example.tld' in elem.nsmap.values())
        self.assertEqual('1', elem.get('{http://a.example.tld}a'))
        self.assertEqual('2', elem.get('{http://b.example.tld}a'))
        self.assertEqual('3', elem.get('a'))

    def test_SubElement(self):
        elem = Element('document')
        child = SubElement(elem, 'paragraph')
        grandchild = SubElement(child, 'span')
        self.assertEqual('paragraph', elem[0].tag)
        self.assertEqual('span', elem[0][0].tag)

    def test_base(self):
        uri = os.path.abspath('sample.xml')
        with open(uri) as f:
            et = etree.parse(f)
        root = et.getroot()
        self.assertEqual(uri, root.base)

    def test_tag(self):
        elem = Element('HwpDoc')
        self.assertEqual('HwpDoc', elem.tag)

        elem = Element('{http://www.w3.org/1999/XSL/Transform}stylesheet')
        self.assertTrue(elem.prefix)
        self.assertEqual('{http://www.w3.org/1999/XSL/Transform}stylesheet', elem.tag)

        elem = Element('{http://www.w3.org/1999/XSL/Transform}stylesheet',
                       nsmap=dict(xsl='http://www.w3.org/1999/XSL/Transform'))
        self.assertEqual('xsl', elem.prefix)
        self.assertEqual('{http://www.w3.org/1999/XSL/Transform}stylesheet', elem.tag)

    def test_nsmap(self):
        self.assertEqual(dict(x='http://example.tld'),
                          self.root.nsmap)
        self.assertEqual(dict(x='http://example.tld',
                               z='http://z.example.tld'),
                          self.root[1].nsmap)

    def test_prefix(self):
        self.assertEqual('x', self.root.prefix)
        self.assertEqual('z', self.root[1].prefix)

    def test_text(self):
        self.assertEqual('text', self.root[0].text)
        self.assertEqual(None, self.root[1].text)

    def test_tail(self):
        self.assertEqual('tail', self.root[0].tail)
        self.assertEqual(None, self.root[0][0].tail)

    def test_attrib(self):
        self.assertEqual({'version': '1.0'},
                          self.root.attrib)
        self.assertEqual({'a': '1',
                           '{http://example.tld}b': '2',
                           '{http://z.example.tld}c': '3'},
                          self.root[1].attrib)

    def test__contains__(self):
        pass

    def test__copy__(self):
        pass

    def test__deepcopy__(self):
        pass

    def test__delitem__(self):
        pass

    def test__getitem__(self):
        paragraph = self.root.__getitem__(0)
        self.assertEqual('{http://example.tld}paragraph', paragraph.tag)
        paragraph = self.root[0]
        self.assertEqual('{http://example.tld}paragraph', paragraph.tag)

        paragraph = self.root.__getitem__(1)
        self.assertEqual('{http://z.example.tld}object', paragraph.tag)
        paragraph = self.root[1]
        self.assertEqual('{http://z.example.tld}object', paragraph.tag)

        child = self.root.__getitem__(-1)
        self.assertEqual('{http://example.tld}third', child.tag)
        child = self.root[-1]
        self.assertEqual('{http://example.tld}third', child.tag)

    def test__iter__(self):
        it = self.root.__iter__()

        paragraph = it.next()
        self.assertEqual('{http://example.tld}paragraph',
                          paragraph.tag)
        self.assertEqual('text', paragraph.text)
        self.assertEqual('tail', paragraph.tail)

        paragraph = it.next()
        self.assertEqual('{http://z.example.tld}object',
                          paragraph.tag)

        child = it.next()
        self.assertEqual('{http://example.tld}third',
                          child.tag)

        self.assertRaises(StopIteration, it.next)

    def test__len__(self):
        self.assertEqual(3, self.root.__len__())
        self.assertEqual(3, len(self.root))

    def test__nonzero__(self):
        pass

    def test__repr__(self):
        pass

    def test__reversed__(self):
        it = self.root.__reversed__()

        child = it.next()
        self.assertEqual('{http://example.tld}third',
                          child.tag)

        paragraph = it.next()
        self.assertEqual('{http://z.example.tld}object',
                          paragraph.tag)

        paragraph = it.next()
        self.assertEqual('{http://example.tld}paragraph',
                          paragraph.tag)
        self.assertEqual('text', paragraph.text)
        self.assertEqual('tail', paragraph.tail)

        self.assertRaises(StopIteration, it.next)

    def test__setitem__(self):
        new_child = Element('new-child')
        self.root.__setitem__(1, new_child)
        self.assertEqual('new-child', self.root[1].tag)

        new_child = Element('new-child2')
        self.assertRaises(IndexError, self.root.__setitem__, 3, new_child)

    def test_addnext(self):
        pass

    def test_addprevious(self):
        pass

    def test_append(self):
        new_child = Element('new-child')
        self.root.append(new_child)

        child = self.root[3]
        self.assertEqual('new-child', child.tag)

    def test_clear(self):
        pass

    def test_extend(self):
        pass

    def test_find(self):
        pass

    def test_findall(self):
        pass

    def test_findtext(self):
        pass

    def test_get(self):
        self.assertEqual(None, self.root.get('nonexists'))
        self.assertEqual('1.0', self.root.get('version'))
        self.assertEqual('1', self.root[1].get('a'))
        self.assertEqual('2', self.root[1].get('{http://example.tld}b'))
        self.assertEqual('3', self.root[1].get('{http://z.example.tld}c'))

    def test_getchildren(self):
        children = self.root.getchildren()

        child = children[0]
        self.assertEqual('{http://example.tld}paragraph',
                          child.tag)
        self.assertEqual('text', child.text)
        self.assertEqual('tail', child.tail)

        child = children[1]
        self.assertEqual('{http://z.example.tld}object',
                          child.tag)

        child = children[2]
        self.assertEqual('{http://example.tld}third',
                          child.tag)

    def test_getiterator(self):
        pass

    def test_getnext(self):
        child = self.root[0]
        child = child.getnext()
        self.assertEqual('{http://z.example.tld}object',
                          child.tag)
        child = child.getnext()
        self.assertEqual('{http://example.tld}third',
                          child.tag)
        child = child.getnext()
        self.assertEqual(None, child)

    def test_getparent(self):
        parent = self.root.getparent()
        self.assertEqual(None, parent)

        for child in self.root:
            parent = child.getparent()
            self.assertEqual('{http://example.tld}document',
                              parent.tag)

    def test_getprevious(self):
        child = self.root[-1]
        self.assertEqual('{http://example.tld}third',
                          child.tag)
        child = child.getprevious()
        self.assertEqual('{http://z.example.tld}object',
                          child.tag)
        child = child.getprevious()
        self.assertEqual('{http://example.tld}paragraph',
                          child.tag)
        child = child.getprevious()
        self.assertEqual(None, child)

    def test_getroottree(self):
        elem = Element('HwpDoc')
        self.assertTrue(elem.getroottree() is not None)

    def test_index(self):
        pass

    def test_insert(self):
        pass

    def test_items(self):
        pass

    def test_iter(self):
        pass

    def test_iterancestors(self):
        span = self.root[0][0]
        it = span.iterancestors()

        parent = it.next()
        self.assertEqual('{http://example.tld}paragraph',
                          parent.tag)

        parent = it.next()
        self.assertEqual('{http://example.tld}document',
                          parent.tag)

        self.assertRaises(StopIteration, it.next)

        # with tags predicate

        it = span.iterancestors('{http://example.tld}document')

        parent = it.next()
        self.assertEqual('{http://example.tld}document',
                          parent.tag)

        self.assertRaises(StopIteration, it.next)

    def test_iterchildren(self):
        pass

    def test_descendants(self):
        pass

    def test_iterfind(self):
        pass

    def test_siblings(self):
        pass

    def test_itertext(self):
        pass

    def test_keys(self):
        self.assertEqual(set(['version']),
                          set(self.root.keys()))
        self.assertEqual(set(['a', '{http://example.tld}b',
                               '{http://z.example.tld}c']),
                          set(self.root[1].keys()))

    def test_makeelement(self):
        pass

    def test_remove(self):
        pass

    def test_replace(self):
        pass

    def test_set(self):
        self.root.set('{http://example.tld}a', '1')
        self.assertEqual('1', self.root.get('{http://example.tld}a'))
        self.root.set('{http://c.example.tld}a', '2')
        self.assertEqual('2', self.root.get('{http://c.example.tld}a'))
        self.root.set('a', '3')
        self.assertEqual('3', self.root.get('a'))

    def test_values(self):
        self.root[1].values()

    def test_xpath(self):
        nsmap = dict(x='http://example.tld')

        # element
        result = self.root.xpath('//x:paragraph', namespaces=nsmap)
        self.assertEqual(1, len(result))
        self.assertEqual('{http://example.tld}paragraph',
                          result[0].tag)

        # attribute
        result = self.root.xpath('@version', namespaces=nsmap)
        self.assertEqual(['1.0'], result)

        # string
        result = self.root.xpath('"foo"', namespaces=nsmap)
        self.assertEqual('foo', result)

        # number expression
        result = self.root.xpath('1', namespaces=nsmap)
        self.assertEqual(1.0, result)

        result = self.root.xpath('"1.0"', namespaces=nsmap)
        # should be string, but alas, it returns a number in jxml
        if sys.platform.startswith('java'):
            self.assertEqual(1.0, result)
        else:
            self.assertEqual('1.0', result)


class QNameTest(TestCase):

    text = '{http://example.tld}document'
    namespace = 'http://example.tld'
    localname = 'document'

    def test_from_text(self):
        qname = QName(self.text)
        self.assertEqual(self.text, qname.text)
        self.assertEqual(self.namespace, qname.namespace)
        self.assertEqual(self.localname, qname.localname)

        qname = QName('document')
        self.assertEqual('document', qname.text)
        self.assertEqual(None, qname.namespace)
        self.assertEqual('document', qname.localname)

    def test_from_nsuri_and_tag(self):
        qname = QName(self.namespace, self.localname)
        self.assertEqual(self.text, qname.text)
        self.assertEqual(self.namespace, qname.namespace)
        self.assertEqual(self.localname, qname.localname)

    def test_from_element(self):
        element = Element(self.text)
        qname = QName(element)
        self.assertEqual(self.text, qname.text)
        self.assertEqual(self.namespace, qname.namespace)
        self.assertEqual(self.localname, qname.localname)


class XPathTest(TestCase):

    def test_xpath(self):
        from lxml.etree import parse
        from lxml.etree import XPath
        with file('sample.xml') as f:
            doc = parse(f)

        nsmap = dict(x='http://example.tld')

        # element
        xpath = XPath('//x:paragraph', namespaces=nsmap)
        result = xpath(doc)
        self.assertEqual(1, len(result))
        self.assertEqual('{http://example.tld}paragraph',
                          result[0].tag)

        # attribute
        xpath = XPath('@version', namespaces=nsmap)
        result = xpath(doc)
        self.assertEqual(['1.0'], result)

        # string
        xpath = XPath('"foo"', namespaces=nsmap)
        result = xpath(doc)
        self.assertEqual('foo', result)

        # number
        xpath = XPath('1', namespaces=nsmap)
        self.assertEqual(1, xpath(doc))

        # string, but alas, it returns a number in jxml
        xpath = XPath('"1.0"', namespaces=nsmap)
        result = xpath(doc)
        if sys.platform.startswith('java'):
            self.assertEqual(1.0, result)
        else:
            self.assertEqual('1.0', result)

        # Boolean
        xpath = XPath('1 = 1', namespaces=nsmap)
        self.assertEqual(True, xpath(doc))


class XSLTTest(TestCase):

    def test_from_element(self):
        with open('xsl/import-test.xsl') as f:
            xsl_tree = etree.parse(f)
        etree.XSLT(xsl_tree.getroot())

    def test_xslt_with_default_parser(self):
        with open('xsl/import-test.xsl') as f:
            xsl_tree = etree.parse(f)
        transform = etree.XSLT(xsl_tree)
        result = transform(etree.XML('<hello />'))
        self.assertEqual('world', result.getroot().tag)

    def test_text_output(self):
        with open('text-output.xsl') as f:
            xsl_tree = etree.parse(f)
        transform = etree.XSLT(xsl_tree)
        result = transform(etree.XML('<hello/>'))
        self.assertEqual(None, result.getroot())
        self.assertEqual(u'world', unicode(result))
        self.assertEqual('world', str(result))


if __name__ == '__main__':
    unittest.main()
