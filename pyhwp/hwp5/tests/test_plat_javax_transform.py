# -*- coding: utf-8 -*-
from __future__ import with_statement
import unittest
from hwp5.tests.mixin_xslt import XsltTestMixin


class TestPlatJavaxTransform(unittest.TestCase, XsltTestMixin):

    def test_is_enabled(self):
        from hwp5.plat import javax_transform
        import sys

        if sys.platform.startswith('java'):
            self.assertTrue(javax_transform.is_enabled())
        else:
            self.assertFalse(javax_transform.is_enabled())

    def setUp(self):
        from hwp5.plat import javax_transform
        if javax_transform.is_enabled():
            self.xslt = javax_transform.xslt
            self.xslt_compile = javax_transform.xslt_compile
        else:
            self.xslt = None
            self.xslt_compile = None
