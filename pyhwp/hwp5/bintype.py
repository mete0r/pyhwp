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
from collections import deque
from pprint import pprint
import logging
import struct
import sys

from .dataio import BSTR
from .dataio import FixedArrayType
from .dataio import FlagsType
from .dataio import ParseError
from .dataio import SelectiveType
from .dataio import StructType
from .dataio import VariableLengthArrayType
from .dataio import X_ARRAY
from .dataio import readn
from .treeop import STARTEVENT, ENDEVENT
from .treeop import iter_subevents


logger = logging.getLogger(__name__)


def bintype_map_events(bin_item):
    bin_type = bin_item['type']
    if isinstance(bin_type, StructType):
        yield STARTEVENT, bin_item
        if hasattr(bin_type, 'members'):
            for member in bin_type.members:
                for x in bintype_map_events(member):
                    yield x
        yield ENDEVENT, bin_item
    elif isinstance(bin_type, FixedArrayType):
        yield STARTEVENT, bin_item
        item = dict(type=bin_type.itemtype)
        for x in bintype_map_events(item):
            yield x
        yield ENDEVENT, bin_item
    elif isinstance(bin_type, VariableLengthArrayType):
        yield STARTEVENT, bin_item
        item = dict(type=bin_type.itemtype)
        for x in bintype_map_events(item):
            yield x
        yield ENDEVENT, bin_item
    elif isinstance(bin_type, X_ARRAY):
        yield STARTEVENT, bin_item
        item = dict(type=bin_type.itemtype)
        for x in bintype_map_events(item):
            yield x
        yield ENDEVENT, bin_item
    elif isinstance(bin_type, SelectiveType):
        yield STARTEVENT, bin_item
        for k, v in bin_type.selections.items():
            item = dict(bin_item, select_when=k, type=v)
            for x in bintype_map_events(item):
                yield x
        yield ENDEVENT, bin_item
    elif isinstance(bin_type, FlagsType):
        # TODO: this should be done in model definitions
        # bin_type: used in binary reading
        # flags_type: binary value to flags type
        bin_item['bin_type'] = bin_type.basetype
        bin_item['flags_type'] = bin_type
        yield None, bin_item
    else:
        yield None, bin_item


def filter_with_version(events, version):
    for ev, item in events:
        required_version = item.get('version')
        if required_version is not None and version < required_version:
            # just consume and skip this tree
            logger.debug('skip following: (required version: %s)',
                         required_version)
            logger.debug('  %s', (ev, item))
            if ev is STARTEVENT:
                for x in iter_subevents(events):
                    pass
            continue
        yield ev, item


def make_items_immutable(events):
    stack = []
    for ev, item in events:
        if ev is None:
            item = tuple(sorted(item.items()))
        elif ev is STARTEVENT:
            item = tuple(sorted(item.items()))
            stack.append(item)
        elif ev is ENDEVENT:
            item = stack.pop()
        yield ev, item


def compile_type_definition(bin_item):
    events = bintype_map_events(bin_item)
    events = make_items_immutable(events)
    return tuple(events)


master_typedefs = dict()


def get_compiled_typedef(type):
    if type not in master_typedefs:
        logger.info('compile typedef of %s', type)
        typedef_events = compile_type_definition(dict(type=type))
        master_typedefs[type] = typedef_events
    return master_typedefs[type]


versioned_typedefs = dict()


def get_compiled_typedef_with_version(type, version):
    if version not in versioned_typedefs:
        versioned_typedefs[version] = typedefs = dict()
    typedefs = versioned_typedefs[version]

    if type not in typedefs:
        logger.info('filter compiled typedef of %s with version %s',
                    type, version)
        typedef_events = get_compiled_typedef(type)
        events = static_to_mutable(typedef_events)
        events = filter_with_version(events, version)
        events = make_items_immutable(events)
        events = tuple(events)
        typedefs[type] = events

    return typedefs[type]


class ERROREVENT(object):
    pass


def static_to_mutable(events):
    stack = []
    for ev, item in events:
        if ev is None:
            item = dict(item)
        elif ev is STARTEVENT:
            item = dict(item)
            stack.append(item)
        elif ev is ENDEVENT:
            item = stack.pop()
        yield ev, item


def pop_subevents(events_deque):
    level = 0
    while len(events_deque) > 0:
        event, item = events_deque.popleft()
        yield event, item
        if event is STARTEVENT:
            level += 1
        elif event is ENDEVENT:
            if level > 0:
                level -= 1
            else:
                return


def resolve_typedefs(typedef_events, context):

    array_types = (X_ARRAY, VariableLengthArrayType, FixedArrayType)

    stack = []
    selective_stack = []

    events = static_to_mutable(typedef_events)
    events = deque(events)
    while len(events) > 0:
        ev, item = events.popleft()
        if isinstance(item['type'], SelectiveType):
            if ev is STARTEVENT:
                parent_struct = stack[-1]
                struct_value = parent_struct['value']
                selector_reference = item['type'].selector_reference
                select_key = selector_reference(context, struct_value)
                logger.debug('select_key: %s', select_key)
                item['select_key'] = select_key
                selective_stack.append(item)
            elif ev is ENDEVENT:
                selective_stack.pop()
            else:
                assert False
        elif 'select_when' in item:
            assert ev in (None, STARTEVENT)
            select_key = selective_stack[-1]['select_key']
            select_when = item.pop('select_when')
            if select_when != select_key:
                # just consume and skip this tree
                logger.debug('skip following: (select key %r != %r)',
                             select_key, select_when)
                logger.debug('  %s', (ev, item))
                if ev is STARTEVENT:
                    for x in pop_subevents(events):
                        logger.debug('  %s', x)
                        pass
                continue
            logger.debug('selected for: %r', select_when)
            events.appendleft((ev, item))
        elif 'condition' in item:
            assert ev in (STARTEVENT, None)
            condition = item.pop('condition')
            parent_struct = stack[-1]
            if not condition(context, parent_struct['value']):
                # just consume and skip this tree
                logger.debug('skip following: (not matched condition: %s)',
                             condition)
                logger.debug('  %s', (ev, item))
                if ev is STARTEVENT:
                    for x in pop_subevents(events):
                        logger.debug('  %s', x)
                        pass
                continue
            events.appendleft((ev, item))
        elif isinstance(item['type'], array_types) and 'count' not in item:
            assert ev is STARTEVENT

            if isinstance(item['type'], X_ARRAY):
                parent_struct = stack[-1]
                struct_value = parent_struct['value']

                count_reference = item['type'].count_reference
                count = count_reference(context, struct_value)
            elif isinstance(item['type'], VariableLengthArrayType):
                count = dict(type=item['type'].counttype, dontcollect=True)
                yield None, count
                count = count['value']
            elif isinstance(item['type'], FixedArrayType):
                count = item['type'].size
            item['count'] = count

            subevents = list(pop_subevents(events))
            endevent = subevents[-1]
            subevents = subevents[:-1]

            def clone(events):
                stack = []
                for ev, item in events:
                    if ev in (STARTEVENT, None):
                        item = dict(item)
                        if ev is STARTEVENT:
                            stack.append(item)
                    else:
                        item = stack.pop()
                    yield ev, item

            events.appendleft(endevent)
            for _ in range(0, count):
                cloned = list(clone(subevents))
                events.extendleft(reversed(cloned))
            events.appendleft((ev, item))
        else:
            if ev is STARTEVENT:
                stack.append(item)
            elif ev is ENDEVENT:
                stack.pop()
            yield ev, item


def evaluate_bin_values(events):
    for ev, item in events:
        if 'flags_type' in item:
            flags_type = item['flags_type']
            assert isinstance(flags_type, FlagsType)
            item['value'] = flags_type(item['value'])
        yield ev, item


def construct_composite_values(events):

    stack = []

    for ev, item in events:
        if ev is STARTEVENT:
            if isinstance(item['type'], StructType):
                item['value'] = dict()
            elif isinstance(item['type'], (X_ARRAY, VariableLengthArrayType,
                                           FixedArrayType)):
                item['value'] = list()
            else:
                assert False
            stack.append(item)
        elif ev in (None, ENDEVENT):
            if ev is ENDEVENT:
                item = stack.pop()
                if isinstance(item['type'], FixedArrayType):
                    item['value'] = tuple(item['value'])

            if len(stack) > 0:
                if not item.get('dontcollect', False):
                    if isinstance(stack[-1]['type'], StructType):
                        # reduce a struct member into struct value
                        stack[-1]['value'][item['name']] = item['value']
                    elif isinstance(stack[-1]['type'],
                                    (X_ARRAY,
                                     VariableLengthArrayType,
                                     FixedArrayType)):
                        stack[-1]['value'].append(item['value'])
        yield ev, item


def log_events(events, log_fn):
    for ev, item in events:
        if ev in (STARTEVENT, ENDEVENT):
            fmt = ['%s:']
            val = [ev.__name__]
        else:
            fmt = ['  %04x:']
            val = [item['bin_offset']]

        fmt.append('%s')
        val.append(item['type'].__name__)

        if 'name' in item:
            fmt.append('%r')
            val.append(str(item['name']))

        if 'value' in item and ev is None:
            fmt.append('%r')
            val.append(item['value'])

        if 'exception' in item:
            fmt.append('-- Exception: %r')
            val.append(item['exception'])

        log_fn(' '.join(fmt), *val)
        yield ev, item


def eval_typedef_events(typedef_events, context, resolve_values):
    events = static_to_mutable(typedef_events)
    events = resolve_typedefs(events, context)
    events = resolve_values(events)
    events = evaluate_bin_values(events)
    events = construct_composite_values(events)
    events = log_events(events, logger.debug)
    return events


def resolve_values_from_stream(stream):
    def resolve_values(events):
        for ev, item in events:
            if ev is None:
                item['bin_offset'] = stream.tell()
                try:
                    item['value'] = resolve_value_from_stream(item, stream)
                except Exception as e:
                    item['exception'] = e
                    ev = ERROREVENT
            yield ev, item
    return resolve_values


def resolve_value_from_stream(item, stream):
    from hwp5.binmodel import ParaTextChunks
    from hwp5.binmodel import CHID
    if 'bin_type' in item:
        item_type = item['bin_type']
    else:
        item_type = item['type']
    if hasattr(item_type, 'binfmt'):
        binfmt = item_type.binfmt
        binsize = struct.calcsize(binfmt)
        bytes = readn(stream, binsize)
        unpacked = struct.unpack(binfmt, bytes)
        return unpacked[0]
    elif item_type is CHID:
        bytes = readn(stream, 4)
        return CHID.decode(bytes)
    elif item_type is BSTR:
        return BSTR.read(stream)
    elif item_type is ParaTextChunks:
        return ParaTextChunks.read(stream)
    elif hasattr(item_type, 'fixed_size'):
        bytes = readn(stream, item_type.fixed_size)
        if hasattr(item_type, 'decode'):
            return item_type.decode(bytes)
        return bytes
    else:
        assert hasattr(item_type, 'read')
        logger.warning('%s: item type relies on its read() to resolve a value',
                       item_type.__name__)
        return item_type.read(stream)


def resolve_type_events(type, context, resolve_values):
    # get typedef events: if current version is specified in the context,
    # get version specific typedef
    if 'version' in context:
        version = context['version']
        events = get_compiled_typedef_with_version(type, version)
    else:
        events = get_compiled_typedef(type)

    # evaluate with context/stream
    return eval_typedef_events(events, context, resolve_values)


def read_type_events(type, context, stream):
    resolve_values = resolve_values_from_stream(stream)
    events = resolve_type_events(type, context, resolve_values)
    for ev, item in events:
        yield ev, item
        if ev is ERROREVENT:
            e = item['exception']
            msg = 'can\'t parse %s' % type
            pe = ParseError(msg)
            pe.cause = e
            pe.path = context.get('path')
            pe.treegroup = context.get('treegroup')
            pe.record = context.get('record')
            pe.offset = item.get('bin_offset')
            raise pe


def read_type_item(type, context, stream, binevents=None):
    if binevents is None:
        binevents = []
    try:
        binevents.extend(read_type_events(type, context, stream))
    except ParseError as e:
        e.binevents = binevents
        raise
    return binevents[-1][1]


def read_type(type, context, stream, binevents=None):
    item = read_type_item(type, context, stream, binevents)
    return item['value']


def dump_events(events):
    def prefix_level(event_prefixed_items):
        level = 0
        for ev, item in event_prefixed_items:
            if ev is STARTEVENT:
                yield level, item
                level += 1
            elif ev is ENDEVENT:
                level -= 1
            else:
                yield level, item

    def item_to_dict(events):
        for ev, item in events:
            yield ev, dict(item)

    def type_to_string(events):
        for ev, item in events:
            item['type'] = item['type'].__name__
            yield ev, item

    def condition_to_string(events):
        for ev, item in events:
            if 'condition' in item:
                item['condition'] = item['condition'].__name__
            yield ev, item

    events = item_to_dict(events)
    events = type_to_string(events)
    events = condition_to_string(events)
    for level, item in prefix_level(events):
        indents = ''
        if level > 0:
            if level > 1:
                indents = '  ' * (level - 2) + '  '
            indents += '- '
        print('{}{}'.format(indents, item))


def main():
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    import hwp5.binmodel
    name = sys.argv[1]
    type = getattr(hwp5.binmodel, name)
    typedef_events = compile_type_definition(dict(type=type))
    pprint(typedef_events)

    context = {}

    def resolve_values(events):
        for ev, item in events:
            if ev is None:
                print('')
                for k, v in sorted(item.items()):
                    print('- {} : {}'.format(k, v))
                value = raw_input('>> ')
                value = eval(value)
                if isinstance(item['type'], FlagsType):
                    value = item['type'](value)
                item['value'] = value
            yield ev, item
    events = eval_typedef_events(typedef_events, context, resolve_values)
    for ev, item in events:
        print('{} {}'.format(ev, item))
