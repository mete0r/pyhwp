# -*- coding: utf-8
from __future__ import with_statement

from contextlib import contextmanager
import logging
from itertools import imap
from itertools import ifilter
from itertools import takewhile
import os.path
from urlparse import urlparse
from urlparse import urljoin
from pkgutil import simplegeneric

from javax.xml import XMLConstants
from javax.xml.parsers import DocumentBuilderFactory
from javax.xml.xpath import XPathFactory
from javax.xml.xpath import XPathConstants
from javax.xml.xpath import XPathExpressionException
from javax.xml.namespace import NamespaceContext
from javax.xml.transform import OutputKeys
from javax.xml.transform import TransformerFactory
from javax.xml.transform import URIResolver
from javax.xml.transform.dom import DOMSource
from javax.xml.transform.dom import DOMResult
from javax.xml.transform.stream import StreamSource
from javax.xml.transform.stream import StreamResult
from org.w3c import dom
from java.io import File
from java.io import InputStream
from java.io import IOException
from java.io import FileInputStream
from java.io import FileOutputStream
from java.io import ByteArrayInputStream
from java.io import ByteArrayOutputStream
from java.io import ByteArrayInputStream
from java.util import Iterator
from java.util import NoSuchElementException


logger = logging.getLogger(__name__)

fac = DocumentBuilderFactory.newInstance()
fac.setNamespaceAware(True)
builder = fac.newDocumentBuilder()
transformfac = TransformerFactory.newInstance()
xpathfac = XPathFactory.newInstance()


class XSLTCoverage(object):

    def __init__(self):
        self.traces = dict()

    def trace(self, systemId, startline, endline):
        files = self.traces
        lines = files.setdefault(systemId, dict())
        lines[startline] = lines.get(startline, 0) + 1
        lines[endline] = lines.get(endline, 0) + 1

    def writeto(self, f):
        trace_root = Element('coverage')
        packages = SubElement(trace_root, 'packages')
        package_attrib = {'name': '', 'branch-rate': '0', 'complexity': '0',
                          'line-rate': '0'}
        package = SubElement(packages, 'package', package_attrib)
        classes = SubElement(package, 'classes')

        for filename in sorted(self.traces):
            if not filename:
                continue
            if filename.startswith('file://'):
                fn = filename[len('file://'):]
            else:
                fn = filename
            class_attrib = dict()
            class_attrib['filename'] = fn
            class_attrib['branch-rate'] = '0'
            class_attrib['complexity'] = '0'
            class_attrib['line-rate'] = '0'
            class_attrib['name'] = os.path.basename(fn)
            clas = SubElement(classes, 'class', class_attrib)
            methods = SubElement(clas, 'methods')
            linesElem = SubElement(clas, 'lines')
            lines = self.traces[filename]
            for lineno in sorted(lines):
                count = lines[lineno]
                lineElem = SubElement(linesElem, 'line',
                                      dict(number=str(lineno),
                                           hits=str(count)))
        s = tostring(trace_root, encoding='utf-8', xml_declaration=True)
        f.write(s)
        f.write('\n')

    def read_from(self, filename):
        tree = parse(filename)
        coverage = tree.getroot()
        assert coverage.tag == 'coverage'
        packages = coverage[0]
        assert packages.tag == 'packages'
        for package in packages:
            if package.tag != 'package':
                continue
            classes = package[0]
            assert classes.tag == 'classes'
            for clas in classes:
                if clas.tag != 'class':
                    continue
                filename = clas.get('filename')
                trace = self.traces.setdefault(filename, dict())
                for lines in clas:
                    if lines.tag != 'lines':
                        continue
                    for line in lines:
                        if line.tag != 'line':
                            continue
                        lineno = int(line.get('number'))
                        hits = int(line.get('hits'))
                        trace[lineno] = trace.get(lineno, 0) + hits


xsltcoverage_trace = None


@contextmanager
def xsltcoverage(output=None):
    xsltcoverage = XSLTCoverage()
    globals()['xsltcoverage_trace'] = xsltcoverage
    yield xsltcoverage
    globals()['xsltcoverage_trace'] = None
    if output is not None:
        if isinstance(output, basestring):
            with open(output, 'w') as f:
                xsltcoverage.writeto(f)
        elif hasattr(output, 'write'):
            xsltcoverage.writeto(output)


def instrument_xalan_transformer_factory(transformfac):
    from javax.xml.transform import Templates
    try:
        from org.apache.xalan.processor import TransformerFactoryImpl
        from org.apache.xalan.transformer import TransformerImpl
        from org.apache.xalan.trace import TraceListenerEx2
    except ImportError:
        logger.warning('Xalan-J is not found: '
                       'check your CLASSPATH. '
                       'there will be no coverage data')
        return transformfac
    if not isinstance(transformfac, TransformerFactoryImpl):
        logger.warning('TransformerFactory implementation is not Xalan-J: '
                       'check system property of '
                       'javax.xml.transform.TransformerFactory. '
                       'there will be no coverage data')
        return transformfac
    if xsltcoverage_trace is None:
        return transformfac

    class XalanTraceListener(TraceListenerEx2):

        def trace(self, ev):
            stylenode = ev.m_styleNode
            systemId = stylenode.getSystemId()
            startline = stylenode.getLineNumber()
            endline = stylenode.getEndLineNumber()

            xsltcoverage_trace.trace(systemId, startline, endline)

    traceListener = XalanTraceListener()

    class XalanTransformerInstrumentImpl(TransformerFactoryImpl):

        def newTemplates(self, source):
            templates = TransformerFactoryImpl.newTemplates(self, source)
            return XalanTemplates(templates, source)

        def newTransformer(self, source=None):
            impl = TransformerFactoryImpl.newTransformer(self, source)
            # add listener
            tracemanager = impl.getTraceManager()
            tracemanager.addTraceListener(traceListener)
            return impl

    class XalanTemplates(Templates):

        def __init__(self, t, s):
            self.templates = t
            self.source = s

        def newTransformer(self):
            transformer = self.templates.newTransformer()
            # add listener
            tracemanager = transformer.getTraceManager()
            tracemanager.addTraceListener(traceListener)
            return transformer

        def getOutputProperties(self):
            return self.templates.getOutputProperties()

    return XalanTransformerInstrumentImpl()


XML_URI = 'http://www.w3.org/XML/1998/namespace'
XMLNS_URI = 'http://www.w3.org/2000/xmlns/'
TRANSIENT_NAMESPACE_PREFIXES = {'xml': XML_URI, 'xmlns': XMLNS_URI}


def split_prefix_and_localName(tag):
    if ':' in tag:
        return tag.split(':', 1)
    else:
        return None, tag


def split_jcnotation(tag):
    ''' Get namespaceURI and localName from a James Clark's notation.

    See http://www.jclark.com/xml/xmlns.htm
    '''
    if tag[0] != '{':
        return None, tag
    pos = tag.find('}')
    if pos == -1:
        raise ValueError(tag)
    return tag[1:pos], tag[pos+1:]


def get_prefix_for_uri(namespaceURI, nsmap):
    for prefix, uri in nsmap.items():
        if uri == namespaceURI:
            return prefix
    if namespaceURI in TRANSIENT_NAMESPACE_PREFIXES:
        return TRANSIENT_NAMESPACE_PREFIXES[namespaceURI]
    prefix = 'ns' + str(len(TRANSIENT_NAMESPACE_PREFIXES))
    TRANSIENT_NAMESPACE_PREFIXES[namespaceURI] = prefix
    return prefix


def dom_element_from_tag(tag, nsmap=None):
    if nsmap is None:
        nsmap = {}
    doc = builder.newDocument()
    namespaceURI, localName = split_jcnotation(tag)
    if namespaceURI is not None:
        prefix = get_prefix_for_uri(namespaceURI, nsmap)
        return doc.createElementNS(namespaceURI, prefix + ':' + localName)
    else:
        return doc.createElement(localName)


def dom_document_from_file(f):
    if hasattr(f, 'name'):
        documentURI = os.path.abspath(f.name)
    else:
        documentURI = None
    bytestring = f.read()

    temp = File.createTempFile('someprefix', 'tmp')

    outputstream = FileOutputStream(temp)
    try:
        outputstream.write(bytestring)
    finally:
        outputstream.close()

    inputstream = FileInputStream(temp)
    try:
        dom_doc = dom_document_from_inputstream(inputstream)
        dom_doc.setDocumentURI(documentURI)
        return dom_doc
    finally:
        inputstream.close()


def dom_document_from_inputstream(inputstream):
    return builder.parse(inputstream)


def dom_tag(dom_element):
    return dom_jcnotation(dom_element)


def dom_jcnotation(dom_node):
    ''' Get node name expressed in James Clark's notation.

    See http://www.jclark.com/xml/xmlns.htm
    '''
    namespaceURI = dom_node.namespaceURI
    if namespaceURI:
        namespace = '{%s}' % namespaceURI
        return namespace + dom_node.localName
    else:
        return dom_node.nodeName


def dom_nsmap_specified_here(dom_element):
    nsmap = {}
    attrs = dom_element.attributes
    for i in range(0, attrs.length):
        attr = attrs.item(i)
        if attr.name.startswith('xmlns:'):
            prefix = attr.name[len('xmlns:'):]
            uri = attr.value
            nsmap[prefix] = uri
        else:
            prefix = attr.prefix
            uri = attr.namespaceURI
            if prefix and uri:
                nsmap[prefix] = uri
    return nsmap


dom_node_is_element = lambda n: n.nodeType == dom.Node.ELEMENT_NODE


def dom_ancestors(dom_node):
    while True:
        dom_node = dom_node.parentNode
        if dom_node:
            yield dom_node
        else:
            return


def dom_ancestor_elements(dom_node):
    return takewhile(dom_node_is_element,
                     dom_ancestors(dom_node))


def dom_siblings_next(dom_node):
    while True:
        dom_node = dom_node.nextSibling
        if dom_node:
            yield dom_node
        else:
            return


def dom_siblings_previous(dom_node):
    while True:
        dom_node = dom_node.previousSibling
        if dom_node:
            yield dom_node
        else:
            return


def dom_nsmap(dom_element):
    assert dom_element.nodeType == dom_element.ELEMENT_NODE
    default_nsmap = dom_nsmap_specified_here(dom_element)
    for ancestor in dom_ancestor_elements(dom_element):
        nsmap = dom_nsmap_specified_here(ancestor)
        nsmap.update(default_nsmap)
        default_nsmap = nsmap
    return default_nsmap


def dom_set_attr(dom_element, key, value, nsmap):
    namespaceURI, localName = split_jcnotation(key)
    if namespaceURI:
        prefix = get_prefix_for_uri(namespaceURI, nsmap)
        qualifiedName = prefix + ':' + localName
        dom_element.setAttributeNS(namespaceURI, qualifiedName, value)
    else:
        dom_element.setAttribute(key, value)


def Element(tag, attrib=None, nsmap=None, **extra):
    assert isinstance(tag, basestring)
    dom_element = dom_element_from_tag(tag, nsmap)
    nsmap = nsmap or {}

    dom_document = dom_element.getOwnerDocument() 
    for prefix, namespaceURI in nsmap.items():
        dom_element.setAttributeNS(XMLNS_URI, 'xmlns:'+prefix, namespaceURI)

    if attrib:
        extra.update(attrib)
    if extra:
        for k, v in extra.items():
            dom_set_attr(dom_element, k, v, nsmap)
    return _Element(dom_element)


def SubElement(parent, tag, attrib=None, nsmap=None, **extra):
    element = Element(tag, attrib, nsmap, **extra)
    parent.append(element)
    return element


def ElementTree(element=None, file=None, parser=None):
    if parser is not None:
        raise NotImplementedError('parser is not supported')
    elif element is not None:
        dom_doc = builder.newDocument()
        dom_doc.documentURI = element._dom_element.ownerDocument.documentURI
        dom_root = dom_doc.importNode(element._dom_element, True)
        dom_doc.appendChild(dom_root)
        _Element(dom_root)
    elif file is not None:
        dom_doc = dom_document_from_file(file)
    else:
        raise ValueError('element and file is None')
    return _ElementTree(dom_doc)


class _Element(object):

    def __init__(self, dom_element):
        if dom_element.nodeType != dom_element.ELEMENT_NODE:
            raise ValueError('ELEMENT_NODE(%d) required: %d' %
                             (dom_element.ELEMENT_NODE, dom_element.nodeType))
        self._dom_element = dom_element

    def getroottree(self):
        dom_doc = self._dom_element.getOwnerDocument()
        return _ElementTree(dom_doc)

    @property
    def attrib(self):
        attrib = dict()
        dom_attrib = self._dom_element.getAttributes()
        for i in range(dom_attrib.length):
            child = dom_attrib.item(i)
            name = child.name
            if not name.startswith('xmlns:') and name != 'xmlns':
                attrib[dom_jcnotation(child)] = child.value
        return attrib

    @property
    def tag(self):
        return dom_tag(self._dom_element)

    @property
    def nsmap(self):
        return dom_nsmap(self._dom_element)

    @property
    def prefix(self):
        namespaceURI = self._dom_element.namespaceURI
        return self._dom_element.lookupPrefix(namespaceURI)

    @property
    def text(self):
        node = self._dom_element.firstChild
        if node and node.nodeType == node.TEXT_NODE:
            return node.getWholeText()

    @property
    def tail(self):
        node = self._dom_element.nextSibling
        if node and node.nodeType == node.TEXT_NODE:
            return node.getWholeText()

    @property
    def base(self):
        dom_doc = self._dom_element.ownerDocument
        return dom_doc.documentURI

    def __deepcopy__(self, memo):
        dom_doc = builder.newDocument()
        copied = dom_doc.importNode(self._dom_element, True)
        return _Element(copied)

    def __iter__(self):
        childs = self._dom_element.getChildNodes()
        for i in range(childs.length):
            child = childs.item(i)
            if child.nodeType == child.ELEMENT_NODE:
                yield _Element(child)

    def __getitem__(self, index):
        if index >= 0:
            iterable = self.__iter__()
        else:
            iterable = self.__reversed__()
            index = -index - 1
        for child in iterable:
            if index == 0:
                return child
            index -= 1
        raise IndexError(index)

    def __len__(self):
        n = 0
        for _ in self.__iter__():
            n += 1
        return n

    def __reversed__(self):
        childs = self._dom_element.getChildNodes()
        length = childs.length
        for x in range(length):
            i = length - x - 1
            child = childs.item(i)
            if child.nodeType == child.ELEMENT_NODE:
                yield _Element(child)

    def __setitem__(self, index, new_elem):
        old_elem = self.__getitem__(index)

        dom_document = self._dom_element.getOwnerDocument()
        dom_element_new = dom_document.importNode(new_elem._dom_element, True)
        self._dom_element.replaceChild(dom_element_new,
                                       old_elem._dom_element)

    def append(self, element):
        dom_document = self._dom_element.getOwnerDocument()
        dom_element_new = dom_document.importNode(element._dom_element, True)
        self._dom_element.appendChild(dom_element_new)
        element._dom_element = dom_element_new

    def get(self, key):
        return self.attrib.get(key)

    def getchildren(self):
        # TODO: deprecated warning
        return list(self.__iter__())

    def getnext(self):
        sibling = None
        for sibling in dom_siblings_next(self._dom_element):
            if dom_node_is_element(sibling):
                return _Element(sibling)

    def getparent(self):
        dom_parent = self._dom_element.getParentNode()
        if dom_parent and dom_node_is_element(dom_parent):
            return _Element(dom_parent)

    def getprevious(self):
        sibling = None
        for sibling in dom_siblings_previous(self._dom_element):
            if dom_node_is_element(sibling):
                return _Element(sibling)

    def iterancestors(self, *tags):
        parents = imap(_Element, dom_ancestor_elements(self._dom_element))
        if tags:
            parents = ifilter(lambda elem: elem.tag in tags,
                              parents)
        return parents

    def keys(self):
        return self.attrib.keys()

    def set(self, key, value):
        dom_doc = self._dom_element.getOwnerDocument()
        dom_element = self._dom_element
        dom_set_attr(dom_element, key, value, self.nsmap)

    def values(self):
        return self.attrib.values()

    def xpath(self, _path, namespaces=None, extensions=None,
              smart_strings=True, **_variables):
        xpath = XPath(_path, namespaces, extensions, smart_strings)
        return xpath(self, **_variables)


class _ElementTree(object):

    def __init__(self, dom_doc):
        self._set_dom_doc(dom_doc)

    def __copy__(self, dom_doc):
        raise NotImplementedError('__copy__() is not implemented yet')

    def __deepcopy__(self, memo):
        dom_doc = builder.newDocument()
        dom_root = dom_doc.importNode(self.getroot()._dom_element, True)
        return _ElementTree(dom_doc)

    @property
    def docinfo(self):
        dom_doc = self._dom_doc
        return DocInfo(dom_doc)

    def _setroot(self, root):
        self._set_dom_doc(root._dom_element.getOwnerDocument())

    def _set_dom_doc(self, dom_doc):
        if dom_doc.nodeType != dom_doc.DOCUMENT_NODE:
            raise ValueError('DOCUMENT_NODE(%d) required: %d' %
                             (dom.DOCUMENT_NODE, dom_doc.nodeType))
        self._dom_doc = dom_doc

    def getroot(self):
        dom_root = self._dom_doc.getDocumentElement()
        if dom_root is not None:
            return _Element(dom_root)

    def find(self, path, namespaces=None):
        root = self.getroot()
        return root.find(path, namespaces)

    def findall(self, path, namespaces=None):
        root = self.getroot()
        return root.findall(path, namespaces)

    def findtext(self, path, default=None, namespaces=None):
        root = self.getroot()
        return root.findtext(path, default, namespaces)

    def iter(self, **tags):
        root = self.getroot()
        return root.iter(*tags)

    def iterfind(self, path, namespaces=None):
        root = self.getroot()
        return root.iterfind(path)

    def relaxng(self, relaxng):
        raise NotImplementedError('relaxng is not implemented yet')

    def write(self, file, encoding=None, method='xml', pretty_print=False,
              xml_declaration=None, with_tail=True, standalone=None,
              compression=0, exclusive=False, with_comments=True,
              inclusive_ns_prefixes=None):

        if compression != 0:
            raise NotImplementedError('compression should be 0')

        s = tostring(self, encoding=encoding, method=method,
                     pretty_print=pretty_print,
                     xml_declaration=xml_declaration, with_tail=with_tail,
                     standalone=standalone, exclusive=exclusive,
                     with_comments=with_comments,
                     inclusive_ns_prefixes=inclusive_ns_prefixes)
        if isinstance(file, basestring):
            with open(file, 'w') as f:
                f.write(s)
        elif hasattr(file, 'write'):
            file.write(s)

    def write_c14n(self, file, exlusive=False, with_comments=True,
                   compression=0, inclusive_ns_prefixes=None):
        raise NotImplementedError('write_c14n() is not implemented yet')

    def xinclude(self):
        raise NotImplementedError('xinclude() is not implemented yet')

    def xmlschema(self, xmlschema):
        raise NotImplementedError('xmlschema() is not implemented yet')

    def xpath(self, _path, namespaces=None, extensions=None,
              smart_strings=True, **_variables):
        xpath = XPath(_path, namespaces, extensions, smart_strings)
        return xpath(self, **_variables)

    def xslt(self, _xslt, extensions=None, access_control=None, **_kw):
        xslt = XSLT(_xslt, extensions=extensions,
                    access_control=access_control)
        return xslt(self, **_kw)


class DocInfo(object):

    def __init__(self, dom_doc):
        self.dom_doc = dom_doc

    def getURL(self):
        return self.dom_doc.documentURI

    def setURL(self, uri):
        self.dom_doc.documentURI = uri

    URL = property(getURL, setURL)

    @property
    def doctype(self):
        doctype = self.dom_doc.doctype
        if doctype:
            return doctype.name
        return ''

    @property
    def public_id(self):
        doctype = self.dom_doc.doctype
        if doctype:
            return doctype.publicId

    @property
    def system_url(self):
        doctype = self.dom_doc.doctype
        if doctype:
            return doctype.systemId

    @property
    def encoding(self):
        return self.dom_doc.getXmlEncoding()

    @property
    def root_name(self):
        dom_root = self.dom_doc.getDocumentElement()
        if dom_root:
            return dom_root.localName

    @property
    def standalone(self):
        return self.dom_doc.getXmlStandalone()

    @property
    def xml_version(self):
        return self.dom_doc.getXmlVersion()

    @property
    def externalDTD(self):
        # TODO
        return None

    @property
    def internalDTD(self):
        # TODO
        return None


class QName(object):

    def __init__(self, text_or_uri_or_element, tag=None):
        x = text_or_uri_or_element
        if tag is not None:
            if not isinstance(x, basestring):
                raise ValueError('Bad namespace URI: %s' %
                                 text_or_uri_or_element)
            if not isinstance(tag, basestring):
                raise ValueError('Bad tag: %s', tag)
            self.namespace = x
            self.localname = tag
        elif isinstance(x, _Element):
            assert tag is None
            dom_node = x._dom_element
            self.namespace = dom_node.namespaceURI
            self.localname = dom_node.localName
        elif isinstance(x, basestring):
            self.namespace, self.localname = split_jcnotation(x)
        else:
            raise ValueError('Bad argument: %s' % text_or_uri_or_element)

    @property
    def text(self):
        if self.namespace:
            return '{%s}%s' % (self.namespace, self.localname)
        return self.localname


class XPath(object):

    def __init__(self, path, namespaces=None, extensions=None, regexp=True,
                 smart_strings=True):
        if extensions:
            raise NotImplementedError('extensions are not supported')

        xpath = xpathfac.newXPath()
        nscontext = NamespaceContextImpl(namespaces or {})
        xpath.setNamespaceContext(nscontext)
        self.xpathexpr = xpath.compile(path)

    def __call__(self, _etree_or_element, **_variables):
        if len(_variables):
            raise NotImplementedError('variables are not supported')

        if isinstance(_etree_or_element, _ElementTree):
            node = _etree_or_element._dom_doc.getDocumentElement()
        elif isinstance(_etree_or_element, _Element):
            node = _etree_or_element._dom_element
        else:
            logger.error('_etree_or_element should be an instance of '
                         '_Element/_ElementTree')
            raise ValueError()

        # TODO: heuristic
        try:
            return self._eval_nodeset(node)
        except XPathExpressionException, e:
            pass

        try:
            return self._eval_node(node)
        except XPathExpressionException, e:
            pass

        try:
            result = self._eval_number(node)
            if not (isinstance(result, float) and str(result) == 'nan'):
                return result
        except XPathExpressionException, e:
            pass

        try:
            return self._eval_string(node)
        except XPathExpressionException, e:
            pass

        return self._eval_boolean(node)

    def _eval_nodeset(self, node):
        result = self.xpathexpr.evaluate(node, XPathConstants.NODESET)
        return dom_xpath_result(result)

    def _eval_node(self, node):
        result = self.xpathexpr.evaluate(node, XPathConstants.NODE)
        return dom_xpath_result(result)

    def _eval_string(self, node):
        result = self.xpathexpr.evaluate(node, XPathConstants.STRING)
        return dom_xpath_result(result)

    def _eval_number(self, node):
        result = self.xpathexpr.evaluate(node, XPathConstants.NUMBER)
        return dom_xpath_result(result)

    def _eval_boolean(self, node):
        result = self.xpathexpr.evaluate(node, XPathConstants.BOOLEAN)
        return dom_xpath_result(result)


@simplegeneric
def dom_xpath_result(result):
    return result


@dom_xpath_result.register(dom.NodeList)
def dom_xpath_result_nodelist(nodelist):
    resultset = []
    for i in range(nodelist.length):
        item = nodelist.item(i)
        resultset.append(dom_xpath_result(item))
    return resultset


@dom_xpath_result.register(dom.Element)
def dom_xpath_result_element(element):
    return _Element(element)


@dom_xpath_result.register(dom.Attr)
def dom_xpath_result_attr(attr):
    return attr.value


class NamespaceContextImpl(NamespaceContext):

    def __init__(self, nsmap):
        self.nsmap = nsmap

    def getNamespaceURI(self, prefix):
        # TODO: default namespace, etc., not implemented
        if prefix is None:
            raise IllegalArgumentException()
        if prefix in self.nsmap:
            return self.nsmap[prefix]
        return XMLConstants.NULL_NS_URI

    def getPrefixes(self, namespaceURI):
        if namespaceURI is None:
            raise IllegalArgumentException()
        return IteratorImpl(self.iterPrefixes(namespaceURI))

    def getPrefix(self, namespaceURI):
        prefixes = self.getPrefixes(namespaceURI)
        if prefixes is None:
            return None

    def iterPrefixes(self, namespaceURI):
        if namespaceURI is None:
            raise IllegalArgumentException()
        for prefix, uri in self.nsmap.items():
            if uri == namespaceURI:
                yield prefix


class IteratorImpl(Iterator):

    def __init__(self, it):
        self.it = it
        self._goNext()

    def hasNext(self):
        return self._hasNext

    def next(self):
        if self._hasNext:
            try:
                return self._nextItem
            finally:
                self._goNext()
        else:
            raise NoSuchElementException()

    def _goNext(self):
        try:
            self._nextItem = it.next()
            self._hasNext = True
        except StopIteration:
            self._nextItem = None
            self._hasNext = False


class XSLT(object):

    def __init__(self, xsl_input, extensions=None, regexp=True,
                 access_control=None):
        if extensions:
            raise NotImplementedError('extensions is not supported')
        if access_control:
            raise NotImplementedError('access_control is not supported')

        if isinstance(xsl_input, _ElementTree):
            xsl_tree = xsl_input
        elif isinstance(xsl_input, _Element):
            xsl_tree = ElementTree(xsl_input)
        else:
            raise ValueError(xsl_input)

        self.xsl_tree = xsl_tree
        self.xsl_source = DOMSource(xsl_tree._dom_doc, xsl_tree.docinfo.URL)
        self.uri_resolver = __URIResolverImpl(xsl_tree)

        #print tostring(xsl_tree)
        fac = TransformerFactory.newInstance()
        fac.setURIResolver(self.uri_resolver)
        fac = instrument_xalan_transformer_factory(fac)
        self.transformer = fac.newTransformer(self.xsl_source)

    def __call__(self, _input, profile_run=False, **kw):

        nsmap = dict(xsl='http://www.w3.org/1999/XSL/Transform')
        output_method = 'xml'
        output_encoding = 'utf-8'

        nodes = self.xsl_tree.xpath('xsl:output/@method', namespaces=nsmap)
        if len(nodes) > 0:
            output_method = nodes[0]

        nodes = self.xsl_tree.xpath('xsl:output/@encoding', namespaces=nsmap)
        if len(nodes) > 0:
            output_encoding = nodes[0]

        #print tostring(_input)
        if isinstance(_input, _ElementTree):
            doc_source = DOMSource(_input._dom_doc)
        elif isinstance(_input, _Element):
            # Xalan-J 2.7.1 does not support a DOMSource from an Element
            # so we build new document
            dom_doc = builder.newDocument()
            dom_root = dom_doc.importNode(_input._dom_element, True)
            dom_doc.appendChild(dom_root)
            doc_source = DOMSource(dom_doc)
        else:
            raise NotImplementedError()

        if output_method in ('xml', 'html'):

            # TODO: for testing
            outputstream = ByteArrayOutputStream()
            result = StreamResult(outputstream)
            self.transformer.transform(doc_source, result)
            bytes = outputstream.toByteArray()
            inputstream = ByteArrayInputStream(bytes)
            dom_doc = builder.parse(inputstream)
            result_tree = _ElementTree(dom_doc)
            return result_tree

            result = DOMResult()
            self.transformer.transform(doc_source, result)
            dom_doc = result.getNode()
            result_tree = _ElementTree(dom_doc)
            #print tostring(result_tree)
            return result_tree
        else:
            outputstream = ByteArrayOutputStream()
            result = StreamResult(outputstream)
            self.transformer.transform(doc_source, result)

            resultdoc = builder.newDocument()
            resulttree = _XSLTResultTree(resultdoc)
            resulttree._text = outputstream.toString(output_encoding)
            return resulttree


class _XSLTResultTree(_ElementTree):

    def __unicode__(self):
        return self._text

    def __str__(self):
        return self._text.encode(self.docinfo.encoding)


class __URIResolverImpl(URIResolver):

    def __init__(self, tree):
        self.__logger = logging.getLogger(__name__+'.'+type(self).__name__)
        self.base = tree.docinfo.URL

    def resolve(self, href, base):
        self.__logger.debug('default_base: %r', self.base)
        self.__logger.debug('href: %r', href)
        self.__logger.debug('base: %r', base)
        if base is None:
            base = self.base

        if base is not None:
            href = urljoin(base, href)
        else:
            href = href

        href = urlparse(href)

        # if href is not a URL
        if not href.scheme and not href.hostname:
            return StreamSource(File(href.path))


def parse(source, parser=None, base_url=None):
    if base_url is not None:
        raise NotImplementedError('base_url is not supported')

    if isinstance(source, basestring):
        with open(source) as f:
            return ElementTree(file=f)
    if hasattr(source, 'read'):
        return ElementTree(file=source)
    assert False, 'source should be a string or file-like object'


def fromstring(text, parser=None, base_url=None):
    if base_url is not None:
        raise NotImplementedError('base_url is not supported')
    from StringIO import StringIO
    f = StringIO(text)
    return ElementTree(file=f)


def tostring(element_or_tree, encoding=None, method='xml',
             xml_declaration=None, pretty_print=False, with_tail=True,
             standalone=None, doctype=None, exclusive=False,
             with_comments=True, inclusive_ns_prefixes=None):
    if isinstance(element_or_tree, _ElementTree):
        source = DOMSource(element_or_tree._dom_doc)
    else:
        source = DOMSource(element_or_tree._dom_element)

    outputstream = ByteArrayOutputStream()
    result = StreamResult(outputstream)
    transformer = transformfac.newTransformer()
    if xml_declaration:
        transformer.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION,
                                      'no')
    else:
        transformer.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION,
                                      'yes')
    if pretty_print:
        transformer.setOutputProperty(OutputKeys.INDENT, 'yes')
    else:
        transformer.setOutputProperty(OutputKeys.INDENT, 'no')
    transformer.transform(source, result)

    if encoding is None:
        encoding = 'ascii'
    return outputstream.toString(encoding)


def XML(s):
    from StringIO import StringIO
    sio = StringIO(s)
    return parse(sio).getroot()
