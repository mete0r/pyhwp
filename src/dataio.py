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

class Eof(Exception):
    pass
class OutOfData(Exception):
    pass

def readn(f, size):
    if size == 0:
        return ''
    data = f.read(size)
    datasize = len(data)
    if datasize == 0:
        raise Eof
    if datasize < size:
        raise OutOfData('%d bytes expected, %d bytes read'%(size, datasize))
    return data

def repr(self):
    return '%s.%s(%s)'%(self.__class__.__module__,self.__class__.__name__, str(self.__dict__))

def extract_pairs(sequence):
    first = None
    for k in sequence:
        if first == None:
            first = k
        else:
            yield first, k
            first = None

class ctx_based:
    def __init__(self, bind):
        self.bind = bind

def decode_fields_in(model, fields, f):
    for fieldModel, name in extract_pairs(fields):
        if isinstance(fieldModel, ctx_based):
            fieldModel = fieldModel.bind(model)
        try:
            value = decodeModel(fieldModel, f)
            setattr(model, name, value)
        except Exception, e:
            logging.warning( 'failed to decode a field named `%s\' as `%s\' of `%s\''%(name, fieldModel, model) )
            raise e


def decodeModel(Model, f):
    decode = getattr(Model, 'decode', None)
    if decode is not None:
        return decode(f)

    fields = getattr(Model, 'fields', None)
    if fields is None:
        raise Exception('invalid Model: %s'%str(Model))
    model = Model()
    decode_fields_in(model, Model.fields, f)
    return model

class UINT32(long):
    def decode(cls, f):
        return cls(struct.unpack('<I', readn(f, 4))[0])
    decode = classmethod(decode)

class INT32(int):
    def decode(cls, f):
        return cls(struct.unpack('<i', readn(f, 4))[0])
    decode = classmethod(decode)

class UINT16(int):
    def decode(cls, f):
        return cls(struct.unpack('<H', readn(f, 2))[0])
    decode = classmethod(decode)

class INT16(int):
    def decode(cls, f):
        return cls(struct.unpack('<h', readn(f, 2))[0])
    decode = classmethod(decode)

class UINT8(int):
    def decode(cls, f):
        return cls(struct.unpack('<B', readn(f, 1))[0])
    decode = classmethod(decode)

class INT8(int):
    def decode(cls, f):
        return cls(struct.unpack('<b', readn(f, 1))[0])
    decode = classmethod(decode)

WORD = UINT16
BYTE = UINT8

class DOUBLE(float):
    def decode(cls, f):
        return cls(struct.unpack('<d', readn(f, 8))[0])
    decode = classmethod(decode)

class ARRAY:
    def __init__(self, type, count):
        self.type = type
        self.count = count
    def decode(self, f):
        result = []
        for i in range(0, self.count):
            result.append( decodeModel(self.type, f) )
        return result

class N_ARRAY:
    def __init__(self, countType, type):
        self.countType = countType
        self.type = type
    def decode(self, f):
        result = []
        count = self.countType.decode(f)
        for i in range(0, count):
            result.append( self.type.decode(f) )
        return result

class OBJECTSTREAM:
    def __init__(self, Model):
        self.Model = Model
    def decode(self, f):
        result = []
        try:
            while True:
                result.append( decodeModel(self.Model, f) )
        except Eof:
            pass
        return result

class ENUM:
    def __init__(self, type, mapper):
        self.type = type
        self.mapper = mapper
    def decode(self, f):
        value = decodeModel(self.type, f)
        return self.mapper[value]

class COLORREF(UINT32):
    def __getattr__(self, name):
        if name == 'r': return self & 0xff
        elif name == 'g': return (self & 0xff00) >> 8
        elif name == 'b': return (self & 0xff0000) >> 16
        elif name == 'a': return (self & 0xff000000) >> 24
        elif name == 'rgb': return self.r, self.g, self.b
    def __str__(self): return '#%02x%02x%02x'%(self.r, self.g, self.b)
    def __repr__(self): return self.__class__.__name__+('(0x%02x, 0x%02x, 0x%02x)'%self.rgb)

class WCHAR:
    def decode(cls, f):
        data = readn(f, 2)
        return data.decode('utf-16le')
    decode = classmethod(decode)

class BSTR:
    def decode(cls, f):
        size = UINT16.decode(f)
        data = readn(f, 2*size)
        return data.decode('utf-16le')
    decode = classmethod(decode)

class BYTESTREAM:
    def decode(cls, f):
        return f.read()
    decode = classmethod(decode)

def hexdump(data):
    s = []
    while len(data) > 16:
        s.append( ' '.join(['%02x'%ord(ch) for ch in data[0:16]]) )
        data = data[16:]
    s.append( ' '.join(['%02x'%ord(ch) for ch in data]) )
    return '\n'.join(s)

def BLOB(size):
    class _BLOB:
        def decode(cls, f):
            o = cls()
            o.data = readn(f, size)
            return o
        decode = classmethod(decode)
        def __repr__(self):
            return hexdump(self.data)
    return _BLOB
