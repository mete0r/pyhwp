# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010,2011,2012 mete0r@sarangbang.or.kr
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
import uno


def unofy_value(value):
    if isinstance(value, dict):
        value = dict_to_propseq(value)
    elif isinstance(value, list):
        value = tuple(value)
    return value


def xenumeration_list(xenum):
    return list(iterate(xenum))


def dict_to_propseq(d):
    from com.sun.star.beans import PropertyValue
    DIRECT_VALUE = uno.Enum('com.sun.star.beans.PropertyState', 'DIRECT_VALUE')
    return tuple(PropertyValue(k, 0, unofy_value(v), DIRECT_VALUE)
                 for k, v in d.iteritems())


def propseq_to_dict(propvalues):
    return dict((p.Name, p.Value) for p in propvalues)


def enumerate(xenumaccess):
    ''' Enumerate an instance of com.sun.star.container.XEnumerationAccess '''
    if hasattr(xenumaccess, 'createEnumeration'):
        xenum = xenumaccess.createEnumeration()
        return iterate(xenum)
    else:
        return iter([])


def iterate(xenum):
    ''' Iterate an instance of com.sun.star.container.XEnumeration '''
    if hasattr(xenum, 'hasMoreElements'):
        while xenum.hasMoreElements():
            yield xenum.nextElement()


def dump(obj):
    from binascii import b2a_hex
    if hasattr(obj, 'ImplementationId'):
        print 'Implementation Id:', b2a_hex(obj.ImplementationId.value)
        print

    if hasattr(obj, 'ImplementationName'):
        print 'Implementation Name:', obj.ImplementationName
        print

    if hasattr(obj, 'SupportedServiceNames'):
        print 'Supported Services:'
        for x in obj.SupportedServiceNames:
            print '', x
        print

    if hasattr(obj, 'Types'):
        print 'Types:'
        for x in obj.Types:
            print '', x.typeClass.value, x.typeName
        print


def dumpdir(obj):
    print 'dir:'
    for e in sorted(dir(obj)):
        print '', e
    print
