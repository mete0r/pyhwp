# -*- coding: utf-8 -*-
import unittest
from oxt_tool.storage.path import split as path_split
from oxt_tool.storage.path import get_ancestors as path_ancestors


class TestStoragePath(unittest.TestCase):
    
    def test_path_split(self):
        self.assertEquals([], path_split('/'))
        self.assertEquals([], path_split(''))
        self.assertEquals(['name'], path_split('name'))
        self.assertEquals(['dir', 'base'], path_split('dir/base'))
        self.assertEquals(['dir', 'base'], path_split('/dir/base'))
        self.assertEquals(['grand', 'parent', 'child'],
                          path_split('grand/parent/child'))

    def test_path_ancestors(self):
        self.assertEquals(set(['top', 'top/grand', 'top/grand/parent']),
                          set(path_ancestors('top/grand/parent/child')))
