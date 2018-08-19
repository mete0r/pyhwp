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
'''Generate HWPv5 Binary Spec Document

Usage::

    hwp5spec xml [--loglevel=<loglevel>]
    hwp5spec -h | --help
    hwp5spec --version

Options::

    -h --help       Show this screen
    --version       Show version
    --loglevel=<loglevel>   Set log level [default: warning]
'''

import logging
import xml.etree.ElementTree as ET


logger = logging.getLogger(__name__)


def define_enum_type(enum_type):
    attrs = dict(name=enum_type.__name__)
    if enum_type.scoping_struct:
        attrs['scope'] = enum_type.scoping_struct.__name__
    elem = ET.Element('EnumType', attrs)
    value_names = list((e, e.name) for e in enum_type.instances)
    value_names.sort()
    for value, name in value_names:
        item = ET.Element('item', dict(name=name, value=str(value)))
        elem.append(item)
    return elem


def define_bitfield(bitgroup_name, bitgroup_desc):
    attrs = dict(name=bitgroup_name,
                 lsb=str(bitgroup_desc.lsb),
                 msb=str(bitgroup_desc.msb))
    elem = ET.Element('BitField', attrs)
    elem.append(reference_type(bitgroup_desc.valuetype))
    return elem


def define_flags_type(flags_type):
    elem = ET.Element('FlagsType')
    from hwp5.dataio import BitGroupDescriptor
    base = ET.SubElement(elem, 'base')
    base.append(reference_type(flags_type.basetype))
    bitgroups = flags_type.__dict__.items()
    bitgroups = ((v.lsb, (k, v)) for k, v in bitgroups
                 if isinstance(v, BitGroupDescriptor))
    bitgroups = list(bitgroups)
    bitgroups.sort()
    bitgroups = reversed(bitgroups)
    bitgroups = ((k, v) for lsb, (k, v) in bitgroups)
    bitgroups = (define_bitfield(k, v) for k, v in bitgroups)
    for bitgroup in bitgroups:
        elem.append(bitgroup)
    return elem


def define_fixed_array_type(array_type):
    attrs = dict()
    attrs['size'] = str(array_type.size)
    elem = ET.Element('FixedArrayType', attrs)
    item_type_elem = ET.SubElement(elem, 'item-type')
    item_type_elem.append(reference_type(array_type.itemtype))
    return elem


def define_variable_length_array_type(array_type):
    elem = ET.Element('VariableLengthArrayType')
    count_type_elem = ET.SubElement(elem, 'count-type')
    count_type_elem.append(reference_type(array_type.counttype))
    item_type_elem = ET.SubElement(elem, 'item-type')
    item_type_elem.append(reference_type(array_type.itemtype))
    return elem


def define_x_array_type(t):
    elem = ET.Element('XArrayType', dict(size=t.count_reference.__doc__))
    item_type_elem = ET.SubElement(elem, 'item-type')
    item_type_elem.append(reference_type(t.itemtype))
    return elem


def define_selective_type(t):
    elem = ET.Element('SelectiveType',
                      dict(selector=t.selector_reference.__doc__))
    for k, v in t.selections.items():
        sel = ET.SubElement(elem, 'selection',
                            dict(when=make_condition_value(k)))
        sel.append(reference_type(v))
    return elem


def reference_type(t):
    attrs = dict()
    attrs['name'] = t.__name__
    attrs['meta'] = type(t).__name__
    elem = ET.Element('type-ref', attrs)

    from hwp5.dataio import EnumType
    from hwp5.dataio import FlagsType
    from hwp5.dataio import FixedArrayType
    from hwp5.dataio import X_ARRAY
    from hwp5.dataio import VariableLengthArrayType
    from hwp5.dataio import SelectiveType
    if isinstance(t, EnumType):
        if t.scoping_struct:
            elem.attrib['scope'] = t.scoping_struct.__name__
    elif isinstance(t, FlagsType):
        elem.append(define_flags_type(t))
    elif isinstance(t, FixedArrayType):
        elem.append(define_fixed_array_type(t))
    elif isinstance(t, X_ARRAY):
        elem.append(define_x_array_type(t))
    elif isinstance(t, VariableLengthArrayType):
        elem.append(define_variable_length_array_type(t))
    elif isinstance(t, SelectiveType):
        elem.append(define_selective_type(t))
    return elem


def referenced_types_by_member(member):
    t = member.get('type')
    if t:
        yield t
        for x in direct_referenced_types(t):
            yield x


def define_member(struct_type, member):
    attrs = dict(name=member['name'])

    version = member.get('version')
    if version:
        version = '.'.join(str(x) for x in version)
        attrs['version'] = version

    elem = ET.Element('member', attrs)

    t = member.get('type')
    if t:
        elem.append(reference_type(t))

    condition = member.get('condition')
    if condition:
        condition = condition.__doc__ or condition.__name__ or ''
        condition = condition.strip()
        condition_elem = ET.Element('condition')
        condition_elem.text = condition
        elem.append(condition_elem)

    return elem


def direct_referenced_types(t):
    from hwp5.dataio import FlagsType
    from hwp5.dataio import FixedArrayType
    from hwp5.dataio import X_ARRAY
    from hwp5.dataio import VariableLengthArrayType
    from hwp5.dataio import StructType
    from hwp5.dataio import SelectiveType
    if isinstance(t, FlagsType):
        for k, desc in t.bitfields.items():
            yield desc.valuetype
    elif isinstance(t, FixedArrayType):
        yield t.itemtype
    elif isinstance(t, X_ARRAY):
        yield t.itemtype
    elif isinstance(t, VariableLengthArrayType):
        yield t.counttype
        yield t.itemtype
    elif isinstance(t, StructType):
        if 'members' in t.__dict__:
            for member in t.members:
                for x in referenced_types_by_member(member):
                    yield x
    elif isinstance(t, SelectiveType):
        for selection in t.selections.values():
            yield selection


def referenced_types_by_struct_type(t):
    if 'members' in t.__dict__:
        for member in t.members:
            for x in referenced_types_by_member(member):
                yield x


def extension_sort_key(cls):
    import inspect
    key = inspect.getmro(cls)
    key = list(x.__name__ for x in key)
    key = tuple(reversed(key))
    return key


def sort_extensions(extension_types):
    extension_types = extension_types.items()
    extension_types = list((extension_sort_key(cls), (k, cls))
                           for k, cls in extension_types)
    extension_types.sort()
    extension_types = ((k, cls) for sort_key, (k, cls) in extension_types)
    return extension_types


def extensions_of_tag_model(tag_model):
    extension_types = getattr(tag_model, 'extension_types', None)
    if extension_types:
        extension_types = sort_extensions(extension_types)
        key_condition = getattr(tag_model, 'get_extension_key', None)
        key_condition = key_condition.__doc__.strip()
        for key, extension_type in extension_types:
            yield (key_condition, key), extension_type


def define_struct_type(t):
    elem = ET.Element('StructType',
                      dict(name=t.__name__))
    for extend in get_extends(t):
        elem.append(define_extends(extend))

    if 'members' in t.__dict__:
        for member in t.members:
            elem.append(define_member(t, member))
    return elem


def define_tag_model(tag_id):
    from hwp5.tagids import tagnames
    from hwp5.binmodel import tag_models
    tag_name = tagnames[tag_id]
    tag_model = tag_models[tag_id]
    elem = ET.Element('TagModel',
                      dict(tag_id=str(tag_id),
                           name=tag_name))
    elem.append(define_base_type(tag_model))
    for (name, value), extension_type in extensions_of_tag_model(tag_model):
        elem.append(define_extension(extension_type,
                                     tag_model,
                                     name,
                                     value))
    return elem


def define_base_type(t):
    elem = ET.Element('base', dict(name=t.__name__))
    return elem


def make_condition_value(value):
    from hwp5.dataio import EnumType
    if isinstance(value, tuple):
        value = tuple(make_condition_value(v) for v in value)
        return '('+', '.join(value)+')'
    elif isinstance(type(value), EnumType):
        return repr(value)
    elif isinstance(value, type):
        return value.__name__
    else:
        return str(value)


def define_extension(t, up_to_type, name, value):
    attrs = dict(name=t.__name__)
    elem = ET.Element('extension', attrs)
    condition = ET.Element('condition')
    condition.text = name + ' == ' + make_condition_value(value)
    elem.append(condition)

    for extend in get_extends(t, up_to_type):
        elem.append(define_extends(extend))

    if 'members' in t.__dict__:
        for member in t.members:
            elem.append(define_member(t, member))
    return elem


def get_extends(t, up_to_type=None):
    def take_up_to(up_to_type, mro):
        for t in mro:
            yield t
            if t is up_to_type:
                return
    from itertools import takewhile

    import inspect
    mro = inspect.getmro(t)
    mro = mro[1:]  # exclude self
    # mro = take_up_to(up_to_type, mro)
    mro = takewhile(lambda cls: cls is not up_to_type, mro)
    mro = (t for t in mro if 'members' in t.__dict__)
    mro = list(mro)
    mro = reversed(mro)
    return mro


def define_extends(t):
    attrs = dict(name=t.__name__)
    elem = ET.Element('extends', attrs)
    return elem


def define_primitive_type(t):
    attrs = dict(name=t.__name__)
    fixed_size = getattr(t, 'fixed_size', None)
    if fixed_size:
        attrs['size'] = str(fixed_size)

    elem = ET.Element('PrimitiveType', attrs)

    binfmt = getattr(t, 'binfmt', None)
    if binfmt:
        binfmt_elem = ET.Element('binfmt')
        binfmt_elem.text = binfmt
        elem.append(binfmt_elem)
    return elem


def main():
    from docopt import docopt
    from hwp5 import __version__
    from hwp5.proc import rest_to_docopt

    doc = rest_to_docopt(__doc__)
    args = docopt(doc, version=__version__)

    if '--loglevel' in args:
        loglevel = args['--loglevel'].lower()
        loglevel = dict(error=logging.ERROR,
                        warning=logging.WARNING,
                        info=logging.INFO,
                        debug=logging.DEBUG).get(loglevel, logging.WARNING)
        logger.setLevel(loglevel)
        logger.addHandler(logging.StreamHandler())

    from hwp5 import binmodel
    import sys

    enum_types = set()
    extensions = set()
    struct_types = set()
    primitive_types = set()

    root = ET.Element('binspec', dict(version=__version__))
    for tag_id, tag_model in binmodel.tag_models.items():
        logger.debug('TAG_MODEL: %s', tag_model.__name__)
        root.append(define_tag_model(tag_id))
        struct_types.add(tag_model)

        from hwp5.dataio import EnumType
        from hwp5.dataio import StructType
        from hwp5.dataio import PrimitiveType
        for t in referenced_types_by_struct_type(tag_model):
            if isinstance(t, EnumType):
                enum_types.add(t)
            if isinstance(t, StructType):
                struct_types.add(t)
            if isinstance(t, PrimitiveType):
                logger.debug('- PrimitiveType: %s', t.__name__)
                primitive_types.add(t)

        for _, t in extensions_of_tag_model(tag_model):
            extensions.add(t)

    for t in extensions:
        struct_types.add(t)
        for extends in get_extends(t):
            struct_types.add(extends)

    for struct_type in struct_types:
        for t in referenced_types_by_struct_type(struct_type):
            if isinstance(t, EnumType):
                enum_types.add(t)
            if isinstance(t, PrimitiveType):
                primitive_types.add(t)

    enum_types = list((t.__name__, t) for t in enum_types)
    enum_types.sort()
    enum_types = (t for name, t in enum_types)
    for t in enum_types:
        root.append(define_enum_type(t))

    struct_types = list((t.__name__, t) for t in struct_types)
    struct_types.sort()
    struct_types = (t for name, t in struct_types)
    for t in struct_types:
        root.append(define_struct_type(t))

    primitive_types = list((t.__name__, t) for t in primitive_types)
    primitive_types.sort()
    primitive_types = (t for name, t in primitive_types)
    for t in primitive_types:
        root.append(define_primitive_type(t))

    doc = ET.ElementTree(root)
    doc.write(sys.stdout, 'utf-8')
