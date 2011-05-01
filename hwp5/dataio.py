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
    pass
class OutOfData(Exception):
    pass

def readn(f, size):
    data = f.read(size)
    datasize = len(data)
    if datasize == 0:
        raise Eof
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

def parseFields(model, f):
    try:
        fields = model.getFields()
    except:
        logging.debug('no fields definitions for %s : skipped'%(str(model.__class__)))
        fields = []
    for fieldModel, name in fields:
        if fieldModel is None:
            value = None
        else:
            try:
                value = fieldModel.parse(f)
            except Exception, e:
                logging.warning( 'failed to parse a field named `%s\' as `%s\' of `%s\''%(name, fieldModel, model.__class__) )
                logging.warning(str(e))
                value = None
        setattr(model, name, value)

def parseFieldsWithType(Model, f):
    model = Model()
    parseFields(model, f)
    return model

def fixup_parse(cls):
    parse = getattr(cls, 'parse', None)
    if parse is None:
        getFields = getattr(cls, 'getFields', None)
        if getFields is not None:
            cls.parse = classmethod(parseFieldsWithType)
        else:
            cls.parse = classmethod(lambda cls, f: cls())

class UINT32(long):
    def parse(cls, f):
        return cls(struct.unpack('<I', readn(f, 4))[0])
    parse = classmethod(parse)

class INT32(int):
    def parse(cls, f):
        return cls(struct.unpack('<i', readn(f, 4))[0])
    parse = classmethod(parse)

class UINT16(int):
    def parse(cls, f):
        return cls(struct.unpack('<H', readn(f, 2))[0])
    parse = classmethod(parse)

class INT16(int):
    def parse(cls, f):
        return cls(struct.unpack('<h', readn(f, 2))[0])
    parse = classmethod(parse)

class UINT8(int):
    def parse(cls, f):
        return cls(struct.unpack('<B', readn(f, 1))[0])
    parse = classmethod(parse)

class INT8(int):
    def parse(cls, f):
        return cls(struct.unpack('<b', readn(f, 1))[0])
    parse = classmethod(parse)

WORD = UINT16
BYTE = UINT8

class DOUBLE(float):
    def parse(cls, f):
        return cls(struct.unpack('<d', readn(f, 8))[0])
    parse = classmethod(parse)

def Flags(_basetype, _bits):
    d = dict(extract_swapped_pairs(_bits))
    class _Flags(_basetype):
        def __getattr__(self, name):
            try:
                type = int
                bitsdef = d[name]
                if isinstance(bitsdef, tuple):
                    if len(bitsdef) > 2:
                        l, h, type = bitsdef
                    else:
                        l, h = bitsdef
                    h += 1
                else:
                    l = bitsdef
                    h = l + 1
                return type(int(self >> l) & int( (2**(h-l)) - 1))
            except KeyError:
                raise AttributeError('Invalid flag name: %s'%(name))
        def __repr__(self):
            return hex(self)+'='+str(dict([(name,getattr(self, name)) for name in d.keys()]))
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

class ARRAY(list):
    def __init__(self, type, count):
        self.type = type
        self.count = count
    def parse(self, f):
        for i in range(0, self.count):
            self.append( self.type.parse(f) )
        return self
class DICT(dict):
    def __init__(self, keytype, valuetype):
        self.keytype = keytype
        self.valuetype = valuetype
    def parse(self, f):
        try:
            while True:
                key = self.keytype.parse(f)
                value = self.valuetype.parse(f)
                self[key] = value
        except Eof:
            pass
        return self

class N_ARRAY:
    def __init__(self, countType, type):
        self.countType = countType
        self.type = type
    def parse(self, f):
        result = []
        count = self.countType.parse(f)
        for i in range(0, count):
            result.append( self.type.parse(f) )
        return result

class Matrix(list):
    def parse(cls, f):
        return cls(ARRAY(ARRAY(DOUBLE, 3), 2).parse(f) + [[0.0, 0.0, 1.0]])
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

class COLORREF(UINT32):
    def __getattr__(self, name):
        if name == 'r': return self & 0xff
        elif name == 'g': return (self & 0xff00) >> 8
        elif name == 'b': return (self & 0xff0000) >> 16
        elif name == 'a': return (self & 0xff000000) >> 24
        elif name == 'rgb': return self.r, self.g, self.b
    def __str__(self): return '#%02x%02x%02x'%(self.r, self.g, self.b)
    def __repr__(self): return self.__class__.__name__+('(0x%02x, 0x%02x, 0x%02x)'%self.rgb)

def decode_utf16le_besteffort(s):
    while True:
        try:
            return s.decode('utf-16le')
        except UnicodeDecodeError, e:
            logging.error('can\'t parse (%d-%d) %s'%(e.start, e.end, hexdump(s)))
            s = s[:e.start] + '.'*(e.end-e.start) + s[e.end:]
            continue

class WCHAR:
    def parse(cls, f):
        data = readn(f, 2)
        return decode_utf16le_besteffort(data)
    parse = classmethod(parse)

class BSTR:
    def parse(cls, f):
        size = UINT16.parse(f)
        if size == 0:
            return u''
        data = readn(f, 2*size)
        return decode_utf16le_besteffort(data)
    parse = classmethod(parse)

class BYTES:
    def __init__(self, size=-1):
        self.size = size
    def parse(self, f):
        if self.size < 0:
            return f.read()
        else:
            return f.read(self.size)

class BYTESTREAM:
    def parse(cls, f):
        return f.read()
    parse = classmethod(parse)

class VERSION:
    def parse(cls, f):
        version = readn(f, 4)
        return (ord(version[3]), ord(version[2]), ord(version[1]), ord(version[0]))
    parse = classmethod(parse)

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
