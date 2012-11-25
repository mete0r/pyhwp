# -*- coding: utf-8 -*-
from __future__ import with_statement
import unittest
from hwp5.tests.mixin_xslt import XsltTestMixin
from hwp5.tests.mixin_olestg import OleStorageTestMixin


class TestPlatUNO(unittest.TestCase, XsltTestMixin, OleStorageTestMixin):

    def setUp(self):
        from hwp5.plat import _uno
        if _uno.is_enabled():
            self.xslt = _uno.xslt
            self.xslt_compile = None
            self.OleStorage = _uno.OleStorage
        else:
            self.xslt = None
            self.xslt_compile = None
            self.OleStorage = None
