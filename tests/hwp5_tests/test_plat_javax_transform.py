# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import unittest
import sys

from hwp5.plat import javax_transform

from .mixin_xslt import XsltTestMixin


class TestPlatJavaxTransform(unittest.TestCase, XsltTestMixin):

    def test_is_enabled(self):

        if sys.platform.startswith('java'):
            self.assertTrue(javax_transform.is_enabled())
        else:
            self.assertFalse(javax_transform.is_enabled())

    def setUp(self):
        if javax_transform.is_enabled():
            self.xslt = javax_transform.xslt
            self.xslt_compile = javax_transform.xslt_compile
        else:
            self.xslt = None
            self.xslt_compile = None
