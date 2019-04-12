# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import unittest
import sys

from hwp5.errors import ImplementationNotAvailable
from hwp5.plat import javax_transform

from .mixin_xslt import XsltTestMixin


class TestPlatJavaxTransform(unittest.TestCase, XsltTestMixin):

    def test_is_enabled(self):

        if sys.platform.startswith('java'):
            self.assertTrue(javax_transform.is_enabled())
        else:
            self.assertFalse(javax_transform.is_enabled())

    def setUp(self):
        from hwp5.plat.javax_transform import createXSLTFactory
        try:
            factory = createXSLTFactory(None)
        except ImplementationNotAvailable:
            self.xslt_factory = None
        else:
            self.xslt_factory = factory
