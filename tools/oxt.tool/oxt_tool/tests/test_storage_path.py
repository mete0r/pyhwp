# -*- coding: utf-8 -*-
import unittest
from oxt_tool.storage.path import split as path_split
from oxt_tool.storage.path import get_ancestors as path_ancestors


class TestStoragePath(unittest.TestCase):
    
    def test_path_split(self):
        self.assertEqual([], path_split('/'))
        self.assertEqual([], path_split(''))
        self.assertEqual(['name'], path_split('name'))
        self.assertEqual(['dir', 'base'], path_split('dir/base'))
        self.assertEqual(['dir', 'base'], path_split('/dir/base'))
        self.assertEqual(['grand', 'parent', 'child'],
                          path_split('grand/parent/child'))

    def test_path_ancestors(self):
        self.assertEqual(set(['top', 'top/grand', 'top/grand/parent']),
                          set(path_ancestors('top/grand/parent/child')))
