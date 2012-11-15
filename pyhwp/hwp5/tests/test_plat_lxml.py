# -*- coding: utf-8 -*-
from __future__ import with_statement
import unittest
from hwp5.tests.mixin_xslt import XsltTestMixin
from hwp5.tests.mixin_relaxng import RelaxNGTestMixin


class TestPlatLxml(unittest.TestCase, XsltTestMixin, RelaxNGTestMixin):

    def test_is_enabled(self):
        from hwp5.plat import _lxml

        try:
            import lxml; lxml
        except ImportError:
            self.assertFalse(_lxml.is_enabled())
        else:
            self.assertTrue(_lxml.is_enabled())

    def setUp(self):
        from hwp5.plat import _lxml
        if _lxml.is_enabled():
            self.xslt = _lxml.xslt
            self.xslt_compile = _lxml.xslt_compile
            self.relaxng = _lxml.relaxng
            self.relaxng_compile = _lxml.relaxng_compile
        else:
            self.xslt = None
            self.xslt_compile = None
            self.relaxng = None
            self.relaxng_compile = None
