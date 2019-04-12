# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2015 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


class STARTEVENT:
    pass


class ENDEVENT:
    pass


def prefix_event(level_prefixed_items, root_item=None):
    ''' convert iterable of (level, item) into iterable of (event, item)
    '''
    baselevel = None
    stack = [root_item]
    for level, item in level_prefixed_items:
        if baselevel is None:
            baselevel = level
            level = 0
        else:
            level -= baselevel

        while level + 1 < len(stack):
            yield ENDEVENT, stack.pop()
        while len(stack) < level + 1:
            raise Exception('invalid level: %d, %d, %s' %
                            (level, len(stack) - 1, item))
        assert(len(stack) == level + 1)

        stack.append(item)
        yield STARTEVENT, item

    while 1 < len(stack):
        yield ENDEVENT, stack.pop()


def prefix_ancestors(event_prefixed_items, root_item=None):
    ''' convert iterable of (event, item) into iterable of (ancestors, item)
    '''
    stack = [root_item]
    for event, item in event_prefixed_items:
        if event is STARTEVENT:
            yield stack, item
            stack.append(item)
        elif event is ENDEVENT:
            stack.pop()


def prefix_ancestors_from_level(level_prefixed_items, root_item=None):
    ''' convert iterable of (level, item) into iterable of (ancestors, item)

        @param level_prefixed items: iterable of tuple(level, item)
        @return iterable of tuple(ancestors, item)
    '''
    baselevel = None
    stack = [root_item]
    for level, item in level_prefixed_items:
        if baselevel is None:
            baselevel = level
            level = 0
        else:
            level -= baselevel

        while level + 1 < len(stack):
            stack.pop()
        while len(stack) < level + 1:
            raise Exception('invalid level: %d, %d, %s' %
                            (level, len(stack) - 1, item))
        assert(len(stack) == level + 1)

        yield stack, item
        stack.append(item)


def build_subtree(event_prefixed_items):
    ''' build a tree from (event, item) stream

        Example Scenario::

           ...
           (STARTEVENT, rootitem)          # should be consumed by the caller
           --- call build_subtree() ---
           (STARTEVENT, child1)            # consumed by build_subtree()
           (STARTEVENT, grandchild)        # (same)
           (ENDEVENT, grandchild)          # (same)
           (ENDEVENT, child1)              # (same)
           (STARTEVENT, child2)            # (same)
           (ENDEVENT, child2)              # (same)
           (ENDEVENT, rootitem)            # same, buildsubtree() returns
           --- build_subtree() returns ---
           (STARTEVENT, another_root)
           ...

        result will be (rootitem, [(child1, [(grandchild, [])]),
                                   (child2, [])])

    '''
    childs = []
    for event, item in event_prefixed_items:
        if event == STARTEVENT:
            childs.append(build_subtree(event_prefixed_items))
        elif event == ENDEVENT:
            return item, childs


def iter_subevents(event_prefixed_items):
    level = 0
    for event, item in event_prefixed_items:
        yield event, item
        if event is STARTEVENT:
            level += 1
        elif event is ENDEVENT:
            if level > 0:
                level -= 1
            else:
                return


def tree_events(rootitem, childs):
    ''' generate tuples of (event, item) from a tree
    '''
    yield STARTEVENT, rootitem
    for k in tree_events_multi(childs):
        yield k
    yield ENDEVENT, rootitem


def tree_events_multi(trees):
    ''' generate tuples of (event, item) from trees
    '''
    for rootitem, childs in trees:
        for k in tree_events(rootitem, childs):
            yield k
