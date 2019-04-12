# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import unittest

from hwp5.errors import ImplementationNotAvailable
from hwp5.plat import _lxml

from .mixin_xslt import XsltTestMixin
from .mixin_relaxng import RelaxNGTestMixin


class TestPlatLxml(unittest.TestCase, XsltTestMixin, RelaxNGTestMixin):

    def test_is_enabled(self):

        try:
            import lxml
            lxml
        except ImportError:
            self.assertFalse(_lxml.is_enabled())
        else:
            self.assertTrue(_lxml.is_enabled())

    def setUp(self):
        from hwp5.plat._lxml import createXSLTFactory
        from hwp5.plat._lxml import createRelaxNGFactory
        try:
            factory = createXSLTFactory(None)
        except ImplementationNotAvailable:
            self.xslt_factory = None
        else:
            self.xslt_factory = factory

        try:
            factory = createRelaxNGFactory(None)
        except ImplementationNotAvailable:
            self.relaxng_factory = None
        else:
            self.relaxng_factory = factory
