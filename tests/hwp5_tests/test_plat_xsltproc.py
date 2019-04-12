# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import unittest

from hwp5.errors import ImplementationNotAvailable
from .mixin_xslt import XsltTestMixin


class TestPlatXsltProc(unittest.TestCase, XsltTestMixin):

    def setUp(self):
        from hwp5.plat.xsltproc import createXSLTFactory
        try:
            factory = createXSLTFactory(None)
        except ImplementationNotAvailable:
            self.xslt_factory = None
        else:
            self.xslt_factory = factory
