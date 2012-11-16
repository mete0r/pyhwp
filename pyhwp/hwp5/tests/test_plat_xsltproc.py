# -*- coding: utf-8 -*-
from __future__ import with_statement
import unittest
from hwp5.tests.mixin_xslt import XsltTestMixin


class TestPlatXsltProc(unittest.TestCase, XsltTestMixin):
    
    def setUp(self):
        from hwp5.plat import xsltproc
        xsltproc.enable()
        self.xslt = xsltproc.xslt
        self.xslt_compile = None

    def tearDown(self):
        from hwp5.plat import xsltproc
        xsltproc.disable()
