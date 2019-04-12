# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import unittest

from hwp5.errors import ImplementationNotAvailable
from hwp5.plat import xmllint

from .mixin_relaxng import RelaxNGTestMixin


class TestPlatXmlLint(unittest.TestCase, RelaxNGTestMixin):

    def setUp(self):
        try:
            factory = xmllint.createRelaxNGFactory(None)
        except ImplementationNotAvailable:
            self.relaxng_factory = None
        else:
            self.relaxng_factory = factory
