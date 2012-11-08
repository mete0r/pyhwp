# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010 mete0r@sarangbang.or.kr
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
import logging


logger = logging.getLogger(__name__)


context = None


def is_enabled():
    return context is not None


def enable(context):
    globals()['context'] = context


def oless_from_filename(filename):
    inputstream = inputstream_from_filename(filename)
    return oless_from_inputstream(inputstream)


def inputstream_from_filename(filename):
    f = file(filename, 'rb')
    return inputstream_from_filelike(f)


def inputstream_from_filelike(f):
    InputStreamFromFileLike = inputstream_from_filelike_class()
    return InputStreamFromFileLike(f)


cache = dict()


def inputstream_from_filelike_class():
    InputStreamFromFileLike = cache.get('InputStreamFromFileLike')
    if InputStreamFromFileLike is not None:
        return InputStreamFromFileLike

    import uno, unohelper
    from com.sun.star.io import XInputStream, XSeekable
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
    cache['InputStreamFromFileLike'] = InputStreamFromFileLike
    return InputStreamFromFileLike


def oless_from_inputstream(inputstream):
    sm = context.ServiceManager
    name = 'com.sun.star.embed.OLESimpleStorage'
    args = (inputstream, )
    return sm.createInstanceWithArgumentsAndContext(name, args, context)


class OleStorage(object):

    def __init__(self, stg):
        ''' an OLESimpleStorage to hwp5 storage adapter.

        :param stg: a filename or an instance of OLESimpleStorage
        '''
        if isinstance(stg, basestring):
            self.oless = oless_from_filename(stg)
            try:
                self.oless.getElementNames()
            except:
                from hwp5.errors import InvalidOleStorageError
                raise InvalidOleStorageError('Not a valid OLE2 Compound Binary File.')
        else:
            # TODO assert stg is an instance of OLESimpleStorage
            self.oless = stg

    def __iter__(self):
        return iter(self.oless.getElementNames())

    def __getitem__(self, name):
        from com.sun.star.container import NoSuchElementException
        try:
            elem = self.oless.getByName(name)
        except NoSuchElementException:
            raise KeyError(name)
        services = elem.SupportedServiceNames
        if 'com.sun.star.embed.OLESimpleStorage' in services:
            return OleStorage(elem)
        else:
            elem.closeInput()
            return OleStorageStream(self.oless, name)

    def close(self):
        return
        # TODO
        # if this is root, close underlying olefile
        if self.path == '':
            # old version of OleFileIO has no close()
            if hasattr(self.olefile, 'close'):
                self.olefile.close()


class OleStorageStream(object):

    def __init__(self, oless, name):
        self.oless = oless
        self.name = name

    def open(self):
        stream = self.oless.getByName(self.name)
        return FileFromStream(stream)


class FileFromStream(object):
    ''' A file-like object based on XInputStream/XOuputStream/XSeekable

    :param stream: a stream object which implements
    com.sun.star.io.XInputStream, com.sun.star.io.XOutputStream or
    com.sun.star.io.XSeekable
    '''
    def __init__(self, stream):
        import uno
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
