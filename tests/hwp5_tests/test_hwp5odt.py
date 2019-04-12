# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from unittest import TestCase
import os.path

from hwp5.importhelper import pkg_resources_filename_fallback
from hwp5.utils import hwp5_resources_path


class ResourcesTest(TestCase):

    def test_pkg_resources_filename_fallback(self):
        fname = pkg_resources_filename_fallback('hwp5', 'xsl/odt/styles.xsl')
        self.assertTrue(os.path.exists(fname))

    def test_hwp5_resources_filename(self):
        with hwp5_resources_path('xsl/odt/styles.xsl') as styles_xsl:
            self.assertTrue(os.path.exists(styles_xsl))
