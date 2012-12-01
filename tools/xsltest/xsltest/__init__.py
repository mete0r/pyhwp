# -*- coding: utf-8 -*-
from __future__ import with_statement

import os
import os.path
import logging
from copy import deepcopy
import contextlib
import lxml.etree
from lxml.etree import Element, SubElement
import unittest


logger = logging.getLogger(__name__)


XUNIT_URI = 'urn:xunit/xunit'
XUNIT = '{%s}' % XUNIT_URI

EXPECT_URI = 'urn:xunit/expect'
EXPECT = '{%s}' % EXPECT_URI

CONTEXT_URI = 'urn:xunit/context'
CONTEXT = '{%s}' % CONTEXT_URI

XSL = '{http://www.w3.org/1999/XSL/Transform}'

NAMESPACES = {
    'xunit': XUNIT_URI,
    'expect': EXPECT_URI,
}


@contextlib.contextmanager
def changed_working_dir(working_dir):
    prev = os.getcwd()
    os.chdir(working_dir)
    try:
        yield
    finally:
        os.chdir(prev)


def pretty_print(elem):
    if elem is not None:
        return lxml.etree.tostring(elem, encoding='utf-8', pretty_print=True)


doc = ''' XUnit test

Usage:
    xsltest [--styles-dir=<dir>] [--import-dir=<dir>] [--gen-dir=<dir>] <files>...
    xsltest --help

Options:
    -h --help               Show this screen
       --styles-dir=<dir>   Set XSL stylesheet directory
       --import-dir=<dir>   Set context:import directory
       --gen-dir=<dir>      Set a directory where .py files to be generated

    <files>...          XUnit files
'''


def expand_files(files):
    for path in files:
        if os.path.isdir(path):
            for x in os.listdir(path):
                if x.lower().endswith('.xml'):
                    yield os.path.join(path, x)
        else:
            yield path


def main():
    from docopt import docopt

    args = docopt(doc, version='0.0')

    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    cur_dir = os.getcwd()
    xunit_files = args['<files>']
    styles_dir = args['--styles-dir']
    import_dir = args['--import-dir']
    gen_dir = args['--gen-dir']
    if gen_dir is None:
        gen_dir = cur_dir
    else:
        if not os.path.exists(gen_dir):
            os.makedirs(gen_dir)

    py_files = list()

    proc = Processor(cur_dir, styles_dir=styles_dir, import_dir=import_dir)
    for xunit_path in expand_files(xunit_files):
        xunit_py = proc.generate_testsuite_from_path(xunit_path, gen_dir)
        py_files.append(xunit_py)

    tests = list()
    for xunit_py in py_files:
        d = dict()
        execfile(xunit_py, d)
        ts = unittest.TestLoader().loadTestsFromTestCase(d['Test'])
        tests.append(ts)

    ts = unittest.TestSuite(tests)
    result = unittest.TextTestRunner().run(ts)
    return 0 if result.wasSuccessful() else 1


def generate_testsuite_py(filename, context_tests):
    with file(filename, 'w') as f:
        for line in generate_testsuite_source(context_tests):
            f.write(line)
            f.write('\n')


def generate_testsuite_source(context_tests):
    yield '# -*- coding: utf-8 -*-'
    yield 'import %s' % __name__
    yield ''
    yield ''
    yield 'class Test(%s.TestCase):' % __name__
    yield ''
    for context_test in context_tests:
        for line in context_test.generate_testcase_py(None):
            yield ' ' * 4 + line


class ExpectHandler(object):

    def __init__(self, elem):
        self.name = type(self).__name__
        self.params = self.params_from_elem(elem)
        self.sourceline = elem.sourceline

    def generate_source(self):
        source = 'self.%s(' % self.name + ', '.join(['%r'] * len(self.params)) + ')'
        source = source % self.params
        return source


EXPECT_HANDLER = dict()

def expect(localname):
    def wrapper(f):
        EXPECT_HANDLER[EXPECT + localname] = f
        return f
    return wrapper


@expect('elem')
class expect_elem(ExpectHandler):

    @classmethod
    def params_from_elem(cls, elem):
        expected = evaluate(elem)
        return (expected, )


@expect('attr')
class expect_attr(ExpectHandler):

    @classmethod
    def params_from_elem(cls, elem):
        expected = evaluate(elem)
        name = elem.get('name')
        return (name, expected)


@expect('empty')
class expect_empty(ExpectHandler):

    @classmethod
    def params_from_elem(cls, elem):
        xpath_expr = evaluate(elem)
        return (xpath_expr, )


@expect('true')
class expect_true(ExpectHandler):

    @classmethod
    def params_from_elem(cls, elem):
        bool_expr = evaluate(elem)
        return (bool_expr, )


@expect('equals')
class expect_equals(ExpectHandler):

    @classmethod
    def params_from_elem(cls, elem):
        expected = elem.xpath('expect:expected', namespaces=NAMESPACES)
        assert len(expected) == 1
        expected = expected[0]
        expected = evaluate(expected)

        tested = elem.xpath('expect:tested', namespaces=NAMESPACES)
        assert len(tested) == 1
        tested = tested[0]
        tested = evaluate(tested)
        return tested, expected


@expect('text')
class expect_text(ExpectHandler):
    
    @classmethod
    def params_from_elem(cls, elem):
        text = evaluate(elem)
        return (text, )


@expect('shell')
class expect_shell(ExpectHandler):

    @classmethod
    def params_from_elem(cls, elem):
        return tuple()


class TestCase(unittest.TestCase):

    def expect_elem(self, expected):
        sourceline = self.sourceline
        context = self.context
        value = context.tag
        prefix, qname = interpret_as_qname(expected, context.nsmap)
        logger.info('%5s: expecting element: %r', sourceline, expected)
        logger.debug(' '*7+'- xmlns:%s = %s', prefix, qname.namespace)
        logger.debug(' '*7+'- value: %r', value)
        assert qname.text == value, 'source: %d' % sourceline

    def expect_attr(self, name, expected):
        sourceline = self.sourceline
        context = self.context
        prefix, qname = interpret_as_qname(name, context.nsmap)
        value = context.get(qname.text)
        logger.info('%5s: expecting attribute %r: %r',
                    sourceline,
                    name, expected)
        logger.debug(' '*7+'- xmlns:%s = %s', prefix, qname.namespace)
        logger.debug(' '*7+'- value: %r', value)
        assert expected == value, 'source: %d' % sourceline

    def expect_empty(self, xpath_expr):
        sourceline = self.sourceline
        context = self.context
        boolexpr = u'count(%s) = 0' % xpath_expr
        logger.info('%5s: expecting empty: %r', sourceline, xpath_expr)
        assert context.xpath(boolexpr, namespaces=context.nsmap)

    def expect_true(self, boolexpr):
        sourceline = self.sourceline
        context = self.context
        logger.info('%5s: expecting true: "%s"', sourceline, boolexpr)
        try:
            return context.xpath(boolexpr, namespaces=context.nsmap)
        except:
            logger.info('%s', pretty_print(context))
            logger.info('%s', boolexpr)
            raise

    def expect_equals(self, tested, expected):
        sourceline = self.sourceline
        context = self.context

        logger.info('%5s: expecting equals: %r and %r',
                    sourceline, expected, tested)

        expected_value = context.xpath(expected, namespaces=context.nsmap)
        tested_value = context.xpath(tested, namespaces=context.nsmap)
        logger.info(' '*7+'- expected: %r', expected_value)
        logger.info(' '*7+'- tested: %r', tested_value)
        self.assertEquals(expected_value, tested_value)

    def expect_text(self, text):
        sourceline = self.sourceline
        context = self.context

        logger.info('%5s: expecting text: %r', sourceline, text)

        self.assertEquals(text, context.text)

    def expect_shell(self):
        xpath_inspect(self.context, None, None)


class STARTEVENT: pass
class ENDEVENT: pass


def generate_events(elem):
    from collections import deque
    events = deque([(STARTEVENT, elem), (ENDEVENT, elem)])
    while len(events):
        event, elem = events.popleft()
        yield event, elem
        if event is STARTEVENT:
            for child in reversed(elem):
                events.appendleft((ENDEVENT, child))
                events.appendleft((STARTEVENT, child))


class Processor(object):

    def __init__(self, basepath, styles_dir=None, import_dir=None):
        self.basepath = basepath
        self.styles_dir = styles_dir
        self.import_dir = import_dir

    @property
    def context(self):
        return self.contexts[-1]

    @property
    def stylesheet(self):
        return self.stylesheets[-1]

    def generate_testsuite_from_path(self, path, out_dir):
        path = os.path.abspath(path)
        logger.info('generating testsuite from %s', path)
        with file(path) as f:
            doc = lxml.etree.parse(f)
        root = doc.getroot()

        events = generate_events(root)
        context_tests = self.handle_events(events)
        context_tests = list(context_tests)
        
        basename = os.path.basename(path)
        rootname = os.path.splitext(basename)[0]
        xunit_py = os.path.join(out_dir, rootname+'.py')
        generate_testsuite_py(xunit_py, context_tests)
        return xunit_py

    def handle_events(self, events):
        self.contexts = [None]
        self.stylesheets = [None]
        for ev, elem in events:
            assert ev in (STARTEVENT, ENDEVENT)
            if elem.tag in CONTEXT_HANDLERS:
                handler_class = CONTEXT_HANDLERS[elem.tag]
                if ev is STARTEVENT:
                    transform = handler_class.from_elem(self, elem)
                    context_test = ContextTest(transform, elem)
                    if self.context is None:
                        yield context_test
                    else:
                        self.context.childs.append(context_test)
                    self.contexts.append(context_test)
                else:
                    self.contexts.pop()
            elif elem.tag in STYLESHEET_HANDLERS:
                handler = STYLESHEET_HANDLERS[elem.tag]
                if ev is STARTEVENT:
                    stylesheet = handler(self, elem)
                    self.stylesheets.append(stylesheet)
                else:
                    self.stylesheets.pop()

    def resolve_href_to_path(self, href):
        path = os.path.join(self.basepath, href)
        return os.path.abspath(path)

    def resolve_stylesheet_path(self, href):
        basepath = self.styles_dir
        if basepath is None:
            basepath = self.basepath
        path = os.path.join(basepath, href)
        return os.path.abspath(path)

    def resolve_import_path(self, href):
        basepath = self.import_dir
        if basepath is None:
            basepath = self.basepath
        path = os.path.join(basepath, href)
        return os.path.abspath(path)


class ContextTest(object):

    def __init__(self, transform, context_elem):
        self.transform = transform
        self.expects = []
        for child in context_elem:
            if child.tag in EXPECT_HANDLER:
                expect_handler = EXPECT_HANDLER[child.tag]
                expect = expect_handler(child)
                self.expects.append(expect)
        self.childs = []

    def generate_testcase_py(self, parent):
        sourceline = self.transform.sourceline
        yield ''
        yield '# Line %d' % sourceline
        yield 'def get_context_%d(self):' % sourceline
        if parent is None:
            yield '    parent = None'
        else:
            yield '    parent = self.get_context_%d()' % (parent.transform.sourceline)
        yield '    return %s(parent)' % self.transform.gen_instantiate()
        yield ''
        if len(self.expects) > 0:
            yield 'def test_%d(self):' % sourceline
            yield '    self.context = self.get_context_%d()' % sourceline
            for expect in self.expects:
                yield '    # Line %d' % expect.sourceline
                yield '    self.sourceline = %r' % expect.sourceline
                yield '    '+expect.generate_source()
        for child in self.childs:
            for x in child.generate_testcase_py(self):
                yield x


def xpath_inspect(context, result, xpath):
    import sys
    if sys.stdout.isatty():
        if context is not None:
            logger.info('%s', pretty_print(context))
        if xpath is not None:
            logger.info('xpath: %s', xpath)
        if result is not None:
            logger.info('%r', result)
        while True:
            try:
                xpath = raw_input('xpath> ').strip()
            except EOFError:
                break
            resultset = context.xpath(xpath, namespaces=context.nsmap)
            if isinstance(resultset, list):
                for result in resultset:
                    logger.info('type: %r', type(result))
                    logger.info('%r', result)
            else:
                result = resultset
                logger.info('type: %r', type(result))
                logger.info('%r', result)
            continue


STYLESHEET_HANDLERS = dict()

def stylesheet_handler(ns, localname):
    def wrapper(f):
        STYLESHEET_HANDLERS[ns + localname] = f
        return f
    return wrapper


@stylesheet_handler(XUNIT, 'stylesheet')
def xunit_stylesheet(self, elem):
    stylesheet = elem.get('href')
    assert stylesheet is not None
    return stylesheet


CONTEXT_HANDLERS = dict()
def context_handler(ns, localname):
    def wrapper(f):
        CONTEXT_HANDLERS[ns + localname] = f
        return f
    return wrapper


class ContextTransform(object):

    def __init__(self, params):
        self.__dict__.update(params)

    @classmethod
    def from_elem(cls, proc, elem):
        params = cls.params_from_elem(proc, elem)
        params['sourceline'] = elem.sourceline
        return cls(params)

    def gen_instantiate(self):
        return '%s.%s(%r)' % (__name__, type(self).__name__, self.__dict__)


@context_handler(CONTEXT, 'hwp5-to-xml')
class context_hwp5xml(ContextTransform):

    @classmethod
    def params_from_elem(cls, proc, elem):
        href = elem.get('href')
        hwp5_path = proc.resolve_href_to_path(href)
        logger.debug('%5s: hwp5-to-xml: %r', elem.sourceline, hwp5_path)
        return dict(hwp5_path=hwp5_path)

    def __call__(self, parent_context):
        from hwp5.xmlmodel import Hwp5File
        hwp5_file = Hwp5File(self.hwp5_path)
        from StringIO import StringIO
        out = StringIO()
        hwp5_file.xmlevents(embedbin=True).dump(out)
        out.seek(0)
        xhwp5_doc = lxml.etree.parse(out)
        return xhwp5_doc.getroot()


@context_handler(CONTEXT, 'import')
class context_import(ContextTransform):

    @classmethod
    def params_from_elem(cls, proc, elem):
        href = elem.get('href')
        path = proc.resolve_import_path(href)
        logger.debug('%5s: import: %r', elem.sourceline, path)
        return dict(path=path)

    def __call__(self, parent_context):
        logger.info('%5s: context:import: %r', self.sourceline, self.path)
        with file(self.path) as f:
            return lxml.etree.parse(f).getroot()


@context_handler(CONTEXT, 'subtree')
class context_subtree(ContextTransform):

    @classmethod
    def params_from_elem(cls, proc, elem):
        xpath = get_select(elem)
        assert xpath is not None
        logger.debug('%5s: selecting new context root with: %r', elem.sourceline, xpath)
        return dict(xpath=xpath)

    def __call__(self, parent_context):
        context = parent_context
        xpath = self.xpath
        logger.info('%5s: context:subtree: xpath=%r', self.sourceline, xpath)
        logger.debug(' '*7+'- current context namespaces: %r', context.nsmap)
        root = context.xpath(xpath, namespaces=context.nsmap)
        if len(root) != 1:
            xpath_inspect(context, root, xpath)
        assert len(root) == 1
        return root[0]


@context_handler(CONTEXT, 'wrap-subnodes')
class context_wrap_subnodes(ContextTransform):

    @classmethod
    def params_from_elem(cls, proc, elem):
        xpath = get_select(elem)
        assert xpath is not None
        logger.debug('%5s: creating new context root with: %r', elem.sourceline, xpath)
        return dict(xpath=xpath)

    def __call__(self, parent_context):
        context = parent_context
        xpath = self.xpath

        logger.info('%5s: context:wrap-subnodes: xpath=%r', self.sourceline, xpath)

        root = lxml.etree.Element('wrapper', nsmap=context.nsmap)

        selected = context.xpath(xpath, namespaces=context.nsmap)

        def additem(item):
            if hasattr(item, 'tag'):
                root.append(deepcopy(item))
            elif hasattr(item, 'is_attribute') and item.is_attribute:
                root.set(item.attrname, item)
            elif hasattr(item, 'is_text') and item.is_text:
                root.append(item)

        if isinstance(selected, list):
            for item in selected:
                additem(item)
        else:
            additem(selected)

        return root


@context_handler(CONTEXT, 'xslt')
class context_xslt(ContextTransform):

    @classmethod
    def params_from_elem(cls, proc, elem):
        stylesheet = elem.get('href', proc.stylesheet)
        assert stylesheet is not None
        stylesheet_path = proc.resolve_stylesheet_path(stylesheet)
        logger.debug('%5s: import xsl from: %r',
                     elem.sourceline, stylesheet_path)
        wrap = elem.get('wrap')
        mode = elem.get('mode')
        select = elem.get('select')
        return dict(stylesheet_path=stylesheet_path,
                    wrap=wrap, mode=mode, select=select)

    def __call__(self, parent_context):
        context = parent_context

        stylesheet_path = self.stylesheet_path
        wrap = self.wrap
        mode = self.mode
        select = self.select

        logger.info('%5s: context:xslt: xsl=%r, select=%r, mode=%r, wrap=%r',
                    self.sourceline, stylesheet_path, select, mode, wrap)

        import sys
        if sys.platform == 'win32':
            stylesheet_url = 'file:///' + stylesheet_path.replace('\\', '/')
        else:
            stylesheet_url = 'file://' + stylesheet_path

        # Get namespace map of the stylesheet
        with file(stylesheet_path) as stylesheet_file:
            stylesheet_doc = lxml.etree.parse(stylesheet_file)
            stylesheet_root = stylesheet_doc.getroot()
            stylesheet_nsmap = stylesheet_root.nsmap

        if wrap is None and mode is None and select is None:
            xsl = stylesheet_root
        else:
            xsl = Element(XSL+'stylesheet', version='1.0')
            SubElement(xsl, XSL+'import', href=stylesheet_url)

            SubElement(xsl, XSL+'output', method='xml',
                       encoding='utf-8', indent='no')
            root_template = SubElement(xsl, XSL+'template', match='/')

            if wrap:
                root_template = SubElement(root_template, wrap,
                                           nsmap=stylesheet_nsmap)

            if mode:
                mode_prefix, mode_qname = interpret_as_qname(mode, stylesheet_nsmap)
                apply_templates = SubElement(root_template,
                                             XSL+'apply-templates',
                                             nsmap={mode_prefix: mode_qname.namespace},
                                             mode=mode_prefix+':'+mode_qname.localname)
            else:
                apply_templates = SubElement(root_template,
                                             XSL+'apply-templates')

            if select:
                apply_templates.set('select', select)
            #print lxml.etree.tostring(xsl, pretty_print=True)

        transform = lxml.etree.XSLT(xsl)

        context_doc = lxml.etree.ElementTree(deepcopy(context))
        transformed = transform(context_doc)
        transformed_root = transformed.getroot()
        if transformed_root is None:
            print 'XSLT resulting document is empty. try with "wrap" attribute'
        return transformed_root


def evaluate(elem):
    return elem.text


def get_select(elem):
    xpath = elem.get('select')
    if xpath is None:
        xpath = elem.xpath('xunit:select', namespaces=NAMESPACES)
        if len(xpath) == 0:
            return None
        assert len(xpath) == 1, ('%d: multiple xunit:select found' %
                                 elem.sourceline)
        xpath = xpath[0].text
    return xpath


def interpret_as_qname(value, nsmap):
    value = value.split(':', 1)
    if len(value) == 2:
        prefix, localname = value
    else:
        prefix, localname = None, value[0]
    if prefix is not None:
        assert prefix in nsmap, 'prefix %r not in nsmap %r' % (prefix, nsmap)
        uri = nsmap[prefix]
        return prefix, lxml.etree.QName(uri, localname)
    else:
        uri = nsmap.get(None)
        if uri is None:
            return prefix, lxml.etree.QName(localname)
        else:
            return prefix, lxml.etree.QName(uri, localname)


if __name__ == '__main__':
    main()
