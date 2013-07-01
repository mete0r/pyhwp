# -*- coding: utf-8 -*-

import unittest

from java.lang import System
from java.io import File
from java.io import ByteArrayOutputStream
from javax.xml.parsers import DocumentBuilderFactory
from javax.xml.transform import TransformerFactory
from javax.xml.transform.dom import DOMSource
from javax.xml.transform.stream import StreamSource
from javax.xml.transform.stream import StreamResult

dbfac = DocumentBuilderFactory.newInstance()
dbfac.namespaceAware = True
docfac = dbfac.newDocumentBuilder()
print type(dbfac)

transfac = TransformerFactory.newInstance()

src_dom = docfac.parse('hello.xml')
src_source = DOMSource(src_dom)


def unsigned_byte(x):
    if x < 0:
        return 256 + x
    return x


def Transformer(xsl_source):
    transformer = transfac.newTransformer(xsl_source)
    def transform(src_source):
        outputstream = ByteArrayOutputStream()
        dst_result = StreamResult(outputstream)
        transformer.transform(src_source, dst_result)
        return ''.join(chr(unsigned_byte(x)) for x in outputstream.toByteArray())
    return transform


def transform(xsl_source, src_source):
    transform = Transformer(xsl_source)
    return transform(src_source)


class TestXSLT(unittest.TestCase):

    xsl_path = 'xsl/import-test.xsl'

    def test_xsl_dom(self):

        xsl_dom = docfac.parse(self.xsl_path)
        # DOMSource with System Id
        xsl_source = DOMSource(xsl_dom, self.xsl_path)

        result = transform(xsl_source, src_source)
        #print result
        self.assertTrue('world' in result)

    def test_xsl_stream(self):
        xsl_source = StreamSource(self.xsl_path)

        result = transform(xsl_source, src_source)
        #print result
        self.assertTrue('world' in result)


if __name__ == '__main__':
    unittest.main()
