# -*- coding: utf-8 -*-
from __future__ import with_statement
import unittest
from hwp5.tests.mixin_relaxng import RelaxNGTestMixin


class TestPlatXmlLint(unittest.TestCase, RelaxNGTestMixin):

    relaxng = None
    relaxng_compile = None

    def setUp(self):
        from hwp5.plat import xmllint
        if xmllint.is_enabled():
            self.relaxng = xmllint.relaxng
