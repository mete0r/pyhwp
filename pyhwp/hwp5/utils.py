# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2014 mete0r <mete0r@sarangbang.or.kr>
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
from __future__ import with_statement
from contextlib import contextmanager
from functools import partial
import codecs
import logging
import os
import shutil
import sys
import tempfile

from .importhelper import pkg_resources_filename


logger = logging.getLogger(__name__)


class NIL:
    pass


class cached_property(object):

    def __init__(self, func):
        self.func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, NIL)
        if value is NIL:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value

    def __set__(self, obj, value):
        obj.__dict__[self.__name__] = value


def generate_json_array(tokens):
    ''' generate json array with given tokens '''
    first = True
    for token in tokens:
        if first:
            yield '[\n'
            first = False
        else:
            yield ',\n'
        yield token
    yield '\n]'


class JsonObjects(object):

    def __init__(self, objects, object_to_json):
        self.objects = objects
        self.object_to_json = object_to_json

    def generate(self, **kwargs):
        kwargs.setdefault('sort_keys', True)
        kwargs.setdefault('indent', 2)

        tokens = (self.object_to_json(obj, **kwargs)
                  for obj in self.objects)
        return generate_json_array(tokens)

    def open(self, **kwargs):
        return GeneratorReader(self.generate(**kwargs))

    def dump(self, outfile, **kwargs):
        for s in self.generate(**kwargs):
            outfile.write(s)


def transcode(backend_stream, backend_encoding, frontend_encoding,
              errors='strict'):
    enc = codecs.getencoder(frontend_encoding)
    dec = codecs.getdecoder(frontend_encoding)
    rd = codecs.getreader(backend_encoding)
    wr = codecs.getwriter(backend_encoding)
    return codecs.StreamRecoder(backend_stream, enc, dec, rd, wr, errors)


def transcoder(backend_encoding, frontend_encoding, errors='strict'):
    return partial(transcode,
                   backend_encoding=backend_encoding,
                   frontend_encoding=frontend_encoding,
                   errors=errors)


class GeneratorReader(object):
    ''' convert a string generator into file-like reader

        def gen():
            yield 'hello'
            yield 'world'

        f = GeneratorReader(gen())
        assert 'hell' == f.read(4)
        assert 'oworld' == f.read()
    '''

    def __init__(self, gen):
        self.gen = gen
        self.buffer = ''

    def read(self, size=None):
        if size is None:
            d, self.buffer = self.buffer, ''
            return d + ''.join(self.gen)

        for data in self.gen:
            self.buffer += data
            bufsize = len(self.buffer)
            if bufsize >= size:
                size = min(bufsize, size)
                d, self.buffer = self.buffer[:size], self.buffer[size:]
                return d

        d, self.buffer = self.buffer, ''
        return d

    def close(self):
        self.gen = self.buffer = None


@contextmanager
def hwp5_resources_path(res_path):
    try:
        path = pkg_resources_filename('hwp5', res_path)
    except Exception:
        logger.info('%s: pkg_resources_filename failed; using resource_stream',
                    res_path)
        with mkstemp_open() as (path, g):
            import pkg_resources
            f = pkg_resources.resource_stream('hwp5', res_path)
            try:
                shutil.copyfileobj(f, g)
                g.close()
                yield path
            finally:
                f.close()
    else:
        yield path


def make_open_dest_file(path):
    if path:
        @contextmanager
        def open_dest_path():
            with open(path, 'w') as f:
                yield f
        return open_dest_path
    else:
        @contextmanager
        def open_stdout():
            yield sys.stdout
        return open_stdout


@contextmanager
def mkstemp_open(*args, **kwargs):

    if (kwargs.get('text', False) or (len(args) >= 4 and args[3])):
        text = True
    else:
        text = False

    mode = 'w+' if text else 'wb+'
    fd, path = tempfile.mkstemp(*args, **kwargs)
    try:
        f = os.fdopen(fd, mode)
        try:
            yield path, f
        finally:
            try:
                f.close()
            except Exception:
                pass
    finally:
        unlink_or_warning(path)


def unlink_or_warning(path):
    try:
        os.unlink(path)
    except Exception, e:
        logger.exception(e)
        logger.warning('%s cannot be deleted', path)
