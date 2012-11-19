# -*- coding: utf-8 -*-
from __future__ import with_statement
import unittest
from hwp5.tests.mixin_xslt import XsltTestMixin


class TestPlatXsltProc(unittest.TestCase, XsltTestMixin):
    
    xslt = None
    xslt_compile = None

    def setUp(self):
        from hwp5.plat import xsltproc
        if xsltproc.is_enabled():
            self.xslt = xsltproc.xslt
