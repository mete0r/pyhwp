# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import unittest

from hwp5.plat import xsltproc

from .mixin_xslt import XsltTestMixin


class TestPlatXsltProc(unittest.TestCase, XsltTestMixin):

    xslt = None
    xslt_compile = None

    def setUp(self):
        if xsltproc.is_enabled():
            self.xslt = xsltproc.xslt
