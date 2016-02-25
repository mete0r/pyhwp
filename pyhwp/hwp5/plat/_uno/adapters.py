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
import uno
import unohelper
from com.sun.star.io import XInputStream, XSeekable, XOutputStream


class InputStreamFromFileLike(unohelper.Base, XInputStream, XSeekable):
    ''' Implementation of XInputStream, XSeekable based on a file-like object

    Implements com.sun.star.io.XInputStream and com.sun.star.io.XSeekable

    :param f: a file-like object
    '''
    def __init__(self, f, dontclose=False):
        self.f = f
        self.dontclose = dontclose

    def readBytes(self, aData, nBytesToRead):
        data = self.f.read(nBytesToRead)
        return len(data), uno.ByteSequence(data)

    readSomeBytes = readBytes

    def skipBytes(self, nBytesToSkip):
        self.f.read(nBytesToSkip)

    def available(self):
        return 0

    def closeInput(self):
        if not self.dontclose:
            self.f.close()

    def seek(self, location):
        self.f.seek(location)

    def getPosition(self):
        pos = self.f.tell()
        return pos

    def getLength(self):
        pos = self.f.tell()
        try:
            self.f.seek(0, 2)
            length = self.f.tell()
            return length
        finally:
            self.f.seek(pos)


class OutputStreamToFileLike(unohelper.Base, XOutputStream):
    ''' Implementation of XOutputStream based on a file-like object.

    Implements com.sun.star.io.XOutputStream.

    :param f: a file-like object
    '''
    def __init__(self, f, dontclose=False):
        self.f = f
        self.dontclose = dontclose

    def writeBytes(self, bytesequence):
        self.f.write(bytesequence.value)

    def flush(self):
        self.f.flush()

    def closeOutput(self):
        if not self.dontclose:
            self.f.close()


class FileFromStream(object):
    ''' A file-like object based on XInputStream/XOuputStream/XSeekable

    :param stream: a stream object which implements
    com.sun.star.io.XInputStream, com.sun.star.io.XOutputStream or
    com.sun.star.io.XSeekable
    '''
    def __init__(self, stream):
        self.stream = stream

        if hasattr(stream, 'readBytes'):
            def read(size=None):
                if size is None:
                    data = ''
                    while True:
                        bytes = uno.ByteSequence('')
                        n_read, bytes = stream.readBytes(bytes, 4096)
                        if n_read == 0:
                            return data
                        data += bytes.value
                bytes = uno.ByteSequence('')
                n_read, bytes = stream.readBytes(bytes, size)
                return bytes.value
            self.read = read

        if hasattr(stream, 'seek'):
            self.tell = stream.getPosition

            def seek(offset, whence=0):
                if whence == 0:
                    pass
                elif whence == 1:
                    offset += stream.getPosition()
                elif whence == 2:
                    offset += stream.getLength()
                stream.seek(offset)
            self.seek = seek

        if hasattr(stream, 'writeBytes'):
            def write(s):
                stream.writeBytes(uno.ByteSequence(s))
            self.write = write

            def flush():
                stream.flush()
            self.flush = flush

    def close(self):
        if hasattr(self.stream, 'closeInput'):
            self.stream.closeInput()
        elif hasattr(self.stream, 'closeOutput'):
            self.stream.closeOutput()
