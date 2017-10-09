# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import unittest

from hwp5.plat import xmllint

from .mixin_relaxng import RelaxNGTestMixin


class TestPlatXmlLint(unittest.TestCase, RelaxNGTestMixin):

    relaxng = None
    relaxng_compile = None

    def setUp(self):
        if xmllint.is_enabled():
            self.relaxng = xmllint.relaxng
