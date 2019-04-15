# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import unittest

from hwp5.errors import ImplementationNotAvailable
from hwp5.plat import _uno

from .mixin_xslt import XsltTestMixin
from .mixin_olestg import OleStorageTestMixin


class TestPlatUNO(unittest.TestCase, XsltTestMixin, OleStorageTestMixin):

    def setUp(self):
        from hwp5.plat._uno import createXSLTFactory
        try:
            factory = createXSLTFactory(None)
        except ImplementationNotAvailable:
            self.xslt_factory = None
        else:
            self.xslt_factory = factory

        try:
            self.olestorage_opener = _uno.createStorageOpener(None)
        except ImplementationNotAvailable:
            self.olestorage_opener = None
