# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import unittest

from hwp5.plat import _uno

from .mixin_xslt import XsltTestMixin
from .mixin_olestg import OleStorageTestMixin


class TestPlatUNO(unittest.TestCase, XsltTestMixin, OleStorageTestMixin):

    def setUp(self):
        if _uno.is_enabled():
            self.xslt = _uno.xslt
            self.xslt_compile = None
            self.OleStorage = _uno.OleStorage
        else:
            self.xslt = None
            self.xslt_compile = None
            self.OleStorage = None
