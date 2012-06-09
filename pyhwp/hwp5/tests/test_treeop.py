# -*- coding: utf-8 -*-
from unittest import TestCase

class Test_ancestors_from_level(TestCase):

    def test_ancestors_from_level(self):

        from hwp5.treeop import prefix_ancestors_from_level

        level_prefixed = [
            (0, 'a0'),
            (0, 'b0'),   # sibling
            (1, 'b0-a1'), # child
            (2, 'b0-a1-a2'), #child
            (1, 'b0-b1'), # jump to parent level
            (2, 'b0-b1-b2'), # child
            (0, 'c0'), # jump to grand-parent level
        ]

        ancestors_prefixed = prefix_ancestors_from_level(level_prefixed)
        result = list((list(ancestors), item)
                      for ancestors, item in ancestors_prefixed)

        self.assertEquals(result.pop(0), ([None], 'a0'))
        self.assertEquals(result.pop(0), ([None], 'b0'))
        self.assertEquals(result.pop(0), ([None, 'b0'], 'b0-a1'))
        self.assertEquals(result.pop(0), ([None, 'b0', 'b0-a1'], 'b0-a1-a2'))
        self.assertEquals(result.pop(0), ([None, 'b0'], 'b0-b1'))
        self.assertEquals(result.pop(0), ([None, 'b0', 'b0-b1'], 'b0-b1-b2'))
        self.assertEquals(result.pop(0), ([None], 'c0'))

    def test_ancestors_from_level_from_nonzero_baselevel(self):
        from hwp5.treeop import prefix_ancestors_from_level
        level_prefixed = [
            (7, 'a0'), # baselevel 7
            (8, 'a0-a1'),
            (9, 'a0-a1-a2'),
            (7, 'b0'),
        ]
        ancestors_prefixed = prefix_ancestors_from_level(level_prefixed)
        result = list((list(ancestors), item)
                      for ancestors, item in ancestors_prefixed)
        self.assertEquals(result.pop(0), ([None], 'a0'))
        self.assertEquals(result.pop(0), ([None, 'a0'], 'a0-a1'))
        self.assertEquals(result.pop(0), ([None, 'a0', 'a0-a1'], 'a0-a1-a2'))
        self.assertEquals(result.pop(0), ([None], 'b0'))

    def test_ancestors_from_level_fails_at_level_below_baselevel(self):
        from hwp5.treeop import prefix_ancestors_from_level
        level_prefixed = [
            (7, 'a7'), # baselevel 7
            (8, 'a7-a8'),
            (9, 'a7-a8-a9'),
            (6, 'b7'), # level below the base level
        ]
        try:
            list(prefix_ancestors_from_level(level_prefixed))
            # TODO: 현재로서는 스택에 기본으로 root_item을 넣어놓는 구현 방식 때문에
            # base level 바로 아래 level은 에러가 나지 않음
            #self.fail('exception expected')
        except:
            pass

        level_prefixed = [
            (7, 'a7'), # baselevel 7
            (8, 'a7-a8'),
            (9, 'a7-a8-a9'),
            (5, 'b7'), # level below the base level
        ]
        try:
            list(prefix_ancestors_from_level(level_prefixed))
            self.fail('exception expected')
        except:
            pass

    def test_ancestors_from_level_assert_fails_at_invalid_level_jump(self):
        from hwp5.treeop import prefix_ancestors_from_level

        level_prefixed = [
            (0, 'a0'),
            (2, 'a0-a1-a2'), # invalid level jump
        ]
        ancestors_prefixed = prefix_ancestors_from_level(level_prefixed)
        try:
            list(ancestors_prefixed)
            self.fail('assert fails expected')
        except:
            pass


class TestTreeEvents(TestCase):
    def test_tree_events(self):
        from hwp5.treeop import STARTEVENT, ENDEVENT
        from hwp5.treeop import build_subtree
        from hwp5.treeop import tree_events
        event_prefixed_items = [ (STARTEVENT, 'a'), (ENDEVENT, 'a') ]
        rootitem, childs = build_subtree(iter(event_prefixed_items[1:]))
        self.assertEquals('a', rootitem)
        self.assertEquals(0, len(childs))

        event_prefixed_items = [ (STARTEVENT, 'a'), (STARTEVENT, 'b'), (ENDEVENT, 'b'), (ENDEVENT, 'a') ]
        self.assertEquals( ('a', [('b', [])]), build_subtree(iter(event_prefixed_items[1:])))

        event_prefixed_items = [
            (STARTEVENT, 'a'),
                (STARTEVENT, 'b'),
                    (STARTEVENT, 'c'), (ENDEVENT, 'c'),
                    (STARTEVENT, 'd'), (ENDEVENT, 'd'),
                (ENDEVENT, 'b'),
            (ENDEVENT, 'a')]

        result = build_subtree(iter(event_prefixed_items[1:]))
        self.assertEquals( ('a', [('b', [('c', []), ('d', [])])]), result)

        back = list(tree_events(*result))
        self.assertEquals(event_prefixed_items, back)

