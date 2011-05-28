# -*- coding: utf-8 -*-
#
#                    GNU AFFERO GENERAL PUBLIC LICENSE
#                       Version 3, 19 November 2007
#
#    pyhwp : hwp file format parser in python
#    Copyright (C) 2010 mete0r@sarangbang.or.kr
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import struct
import logging
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class Eof(Exception):
    def __init__(self, *args):
        self.args = args
class OutOfData(Exception):
    pass

def readn(f, size):
    data = f.read(size)
    datasize = len(data)
    if datasize == 0:
        raise Eof(f.tell())
    return data

def extract_pairs(sequence):
    first = None
    for k in sequence:
        if first == None:
            first = k
        else:
            yield first, k
            first = None
def extract_swapped_pairs(sequence):
    for x, y in extract_pairs(sequence):
        yield y, x

class Primitive(object):
    def __init__(self, basetype, fmt):
        self.basetype = basetype
        self.fmt = fmt
        self.calcsize = struct.calcsize(fmt)
    def read(self, f):
        return struct.unpack(self.fmt, readn(f, self.calcsize))[0]
    def parse(self, f):
        return self, self.read(f)
    def __call__(self, primitive):
        return self.basetype(primitive)

UINT32 = Primitive(long, '<I')
INT32 = Primitive(int, '<i')
UINT16 = Primitive(int, '<H')
INT16 = Primitive(int, '<h')
UINT8 = Primitive(int, '<B')
INT8 = Primitive(int, '<b')
WORD = UINT16
BYTE = UINT8
DOUBLE = Primitive(float, '<d')
WCHAR = UINT16

def decode_utf16le_besteffort(s):
    while True:
        try:
            return s.decode('utf-16le')
        except UnicodeDecodeError, e:
            logging.error('can\'t parse (%d-%d) %s'%(e.start, e.end, hexdump(s)))
            s = s[:e.start] + '.'*(e.end-e.start) + s[e.end:]
            continue

class BSTR(object):
    def read(f):
        size = UINT16.read(f)
        if size == 0:
            return u''
        data = readn(f, 2*size)
        return decode_utf16le_besteffort(data)
    read = staticmethod(read)

    def parse(self, f):
        return self, self.read(f)

    def __call__(self, primitive):
        return primitive
BSTR = BSTR()

inch2mm = lambda x: float(int(x * 25.4 * 100 + 0.5)) / 100
hwp2inch = lambda x: x / 7200.0
hwp2mm = lambda x: inch2mm(hwp2inch(x))
hwp2pt = lambda x: int( (x/100.0)*10 + 0.5)/10.0
HWPUNIT = UINT32
SHWPUNIT = INT32
HWPUNIT16 = INT16

class COLORREF(int):
    read = staticmethod(INT32.read)
    def parse(cls, f):
        return cls, cls.read(f)
    parse = classmethod(parse)
    __slots__ = []
    def __getattr__(self, name):
        if name == 'r': return self & 0xff
        elif name == 'g': return (self & 0xff00) >> 8
        elif name == 'b': return (self & 0xff0000) >> 16
        elif name == 'a': return (self & 0xff000000) >> 24
        elif name == 'rgb': return self.r, self.g, self.b
    def __str__(self): return '#%02x%02x%02x'%(self.r, self.g, self.b)
    def __repr__(self): return self.__class__.__name__+('(0x%02x, 0x%02x, 0x%02x)'%self.rgb)

def Flags(_basetype, _bits):
    d = dict(extract_swapped_pairs(_bits))
    keys = d.keys()
    class _Flags(_basetype.basetype):
        __slots__ = []
        read = staticmethod(_basetype.read)
        def parse(cls, f):
            return cls, cls(cls.read(f))
        parse = classmethod(parse)
        def __str__(self):
            d = dict((name,getattr(self, name)) for name in keys)
            return str(tuple([hex(self), d]))
    class ItemDescriptor(object):
        def __get__(self, instance, owner):
            name = self.name
            valuetype = int
            itemdef = d[name]
            if isinstance(itemdef, tuple):
                if len(itemdef) > 2:
                    l, h, valuetype = itemdef
                else:
                    l, h = itemdef
                h += 1
            else:
                l = itemdef
                h = l + 1
            return valuetype(int(instance >> l) & int( (2**(h-l)) - 1))
    for name in keys:
        desc = ItemDescriptor()
        desc.name = name
        setattr(_Flags, name, desc)
    return _Flags

def Enum(**kwargs):
    d = {}
    class _Enum(int):
        def __repr__(self):
            return d.get(self, '')+'(%d)'%self
    for name, v in kwargs.iteritems():
        d[v] = name
        setattr(_Enum, name, v)
    return _Enum

class ARRAY(object):
    def __init__(self, type, count):
        self.type = type
        self.count = count
    def read(self, f):
        result = []
        for i in range(0, self.count):
            type, value = self.type.parse(f)
            result.append( value )
        return tuple(result)
    def parse(self, f):
        return self, self.read(f)
    def __call__(self, value):
        return value

class N_ARRAY(object):
    def __init__(self, countType, type):
        self.countType = countType
        self.type = type
    def read(self, f):
        result = []
        count = self.countType.read(f)
        for i in range(0, count):
            type, value = self.type.parse(f)
            result.append( value )
        return result
    def parse(self, f):
        return self, self.read(f)
    def __call__(self, value):
        return value

class Matrix(list):
    def read(f):
        return ARRAY(ARRAY(DOUBLE, 3), 2).read(f) + ((0.0, 0.0, 1.0),)
    read = staticmethod(read)

    def parse(cls, f):
        return cls, cls.read(f)
    parse = classmethod(parse)

    def applyTo(self, (x, y)):
        ret = []
        for row in self:
            ret.append(row[0] * x + row[1] * y + row[2] * 1)
        return (ret[0], ret[1])
    def scale(self, (w, h)):
        ret = []
        for row in self:
            ret.append(row[0] * w + row[1] * h + row[2] * 0)
        return (ret[0], ret[1])
    def product(self, mat):
        ret = Matrix()
        rs = [0, 1, 2]
        cs = [0, 1, 2]
        for r in rs:
            row = []
            for c in cs:
                row.append( self[r][c] * mat[c][r])
            ret.append(row)
        return ret

class BYTES(object):
    def __init__(self, size=-1):
        self.size = size
    def read(self, f):
        if self.size < 0:
            return f.read()
        else:
            return f.read(self.size)
    def parse(self, f):
        return BYTES, self.read(f)

    def __call__(self, value):
        return value

class VERSION:
    def read(self, f):
        version = readn(f, 4)
        return (ord(version[3]), ord(version[2]), ord(version[1]), ord(version[0]))
    def parse(self, f):
        return self, self.read(f)
    def __call__(self, value):
        return value

VERSION = VERSION()

def parse_model_attributes(model, attributes, context, stream):
    try:
        gen = model.attributes(context)
    except Exception, e:
        msg = 'can\'t parse %s' % model
        logging.error(msg)
        raise Exception(msg, e)

    try:
        type, identifier = gen.next()
        while True:
            try:
                type, value = type.parse(stream)

            except Exception, e:
                logging.exception(e)
                msg = 'can\'t parse %s named "%s" of %s' % (type, identifier, model)
                raise Exception(msg, e)
            attributes[identifier] = value
            type, identifier = gen.send(type(value))
    except StopIteration:
        pass
    return model, attributes


class BasicModel(object):
    def __init__(self, attributes):
        self.__dict__.update(attributes)

    def parse(cls, f):
        return parse_model_attributes(cls, dict(), None, f)
    parse = classmethod(parse)

    def __str__(self):
        return str(self.__dict__)

def dumpbytes(data, crust=False):
    offsbase = 0
    if crust:
        yield '\t 0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F'
    while len(data) > 16:
        if crust:
            line = '%05x0: '%offsbase
        else:
            line = ''
        line += ' '.join(['%02x'%ord(ch) for ch in data[0:16]]) 
        yield line
        data = data[16:]
        offsbase += 1

    if crust:
        line = '%05x0: '%offsbase
    else:
        line = ''
    line += ' '.join(['%02x'%ord(ch) for ch in data]) 
    yield line

def hexdump(data, crust=False):
    return '\n'.join([line for line in dumpbytes(data, crust)])

class IndentedOutput:
    def __init__(self, base, level):
        self.base = base
        self.level = level
    def write(self, x):
        for line in x.split('\n'):
            if len(line) > 0:
                self.base.write('\t'*self.level)
                self.base.write(line)
                self.base.write('\n')
class Printer:
    def __init__(self, baseout):
        self.baseout = baseout
    def prints(self, *args):
        for x in args:
            self.baseout.write( str(x) + ' ')
        self.baseout.write('\n')
