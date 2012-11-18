# -*- coding: utf-8 -*-
from __future__ import with_statement
import unittest
from hwp5.tests.mixin_relaxng import RelaxNGTestMixin


class TestPlatXmlLint(unittest.TestCase, RelaxNGTestMixin):

    def setUp(self):
        from hwp5.plat import xmllint
        xmllint.enable()
        self.relaxng = xmllint.relaxng
        self.relaxng_compile = None

    def tearDown(self):
        from hwp5.plat import xmllint
        xmllint.disable()
