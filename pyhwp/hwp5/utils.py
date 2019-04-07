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
from contextlib import contextmanager
from functools import partial
import codecs
import logging
import os
import shlex
import shutil
import subprocess
import sys
import tempfile

from .importhelper import pkg_resources_filename


PY3 = sys.version_info.major == 3
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
        chunks = self.generate(**kwargs)
        chunks = (chunk.encode('utf-8') for chunk in chunks)
        return GeneratorReader(chunks)

    def dump(self, outfile, **kwargs):
        for s in self.generate(**kwargs):
            outfile.write(s)


def unicode_escape(s):
    '''
    Escape a string.

    :param s:
        a string to escape
    :type s:
        unicode
    :returns:
        escaped string
    :rtype:
        unicode
    '''
    return s.encode('unicode_escape').decode('utf-8')


def unicode_unescape(s):
    '''
    Unescape a string.

    :param s:
        a string to unescape
    :type s:
        unicode
    :returns:
        unescaped string
    :rtype:
        unicode
    '''
    return s.encode('utf-8').decode('unicode_escape')


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
            yield b'hello'
            yield b'world'

        f = GeneratorReader(gen())
        assert 'hell' == f.read(4)
        assert 'oworld' == f.read()
    '''

    def __init__(self, gen):
        self.gen = gen
        self.buffer = b''

    def read(self, size=None):
        if size is None:
            d, self.buffer = self.buffer, b''
            return d + b''.join(self.gen)

        for data in self.gen:
            self.buffer += data
            bufsize = len(self.buffer)
            if bufsize >= size:
                size = min(bufsize, size)
                d, self.buffer = self.buffer[:size], self.buffer[size:]
                return d

        d, self.buffer = self.buffer, b''
        return d

    def close(self):
        self.gen = self.buffer = None


class GeneratorTextReader(object):
    ''' convert a string generator into file-like reader

        def gen():
            yield 'hello'
            yield 'world'

        f = GeneratorTextReader(gen())
        assert 'hell' == f.read(4)
        assert 'oworld' == f.read()
    '''

    def __init__(self, gen):
        self.gen = gen
        self.buffer = ''

    def read(self, size=None):
        if size is None:
            d = self.buffer
            self.buffer = ''
            return d + ''.join(self.gen)

        for data in self.gen:
            self.buffer += data
            bufsize = len(self.buffer)
            if bufsize >= size:
                size = min(bufsize, size)
                d, self.buffer = self.buffer[:size], self.buffer[size:]
                return d

        d = self.buffer
        self.buffer = ''
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
            with open(path, 'wb') as f:
                yield f
        return open_dest_path
    else:
        if PY3:
            @contextmanager
            def open_stdout():
                yield sys.stdout.buffer
            return open_stdout
        else:
            @contextmanager
            def open_stdout():
                yield sys.stdout
            return open_stdout


def wrap_open_dest_for_tty(open_dest, wrappers):
    @contextmanager
    def open_dest_wrapped():
        with open_dest() as output:
            if output.isatty():
                with cascade_contextmanager_filters(output,
                                                    wrappers) as output:
                    yield output
            else:
                yield output
    return open_dest_wrapped


def wrap_open_dest(open_dest, wrappers):
    @contextmanager
    def open_dest_wrapped():
        with open_dest() as output:
            with cascade_contextmanager_filters(output, wrappers) as output:
                yield output
    return open_dest_wrapped


@contextmanager
def cascade_contextmanager_filters(arg, filters):
    if len(filters) == 0:
        yield arg
    else:
        flt, filters = filters[0], filters[1:]
        with flt(arg) as ret:
            with cascade_contextmanager_filters(ret, filters) as ret:
                yield ret


@contextmanager
def null_contextmanager_filter(output):
    yield output


def output_thru_subprocess(cmd):
    @contextmanager
    def filter(output):
        logger.debug('%r', cmd)
        try:
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=output)
        except Exception as e:
            logger.error('%r: %s', ' '.join(cmd), e)
            yield output
        else:
            try:
                yield p.stdin
            except IOError as e:
                import errno
                if e.errno != errno.EPIPE:
                    raise
            finally:
                p.stdin.close()
                p.wait()
                retcode = p.returncode
                logger.debug('%r exit %d', cmd, retcode)
    return filter


def xmllint(c14n=False, encode=None, format=False, nonet=True):
    cmd = ['xmllint']
    if c14n:
        cmd.append('--c14n')
    if encode:
        cmd += ['--encode', encode]
    if format:
        cmd.append('--format')
    if nonet:
        cmd.append('--nonet')
    cmd.append('-')
    return output_thru_subprocess(cmd)


def syntaxhighlight(mimetype):
    try:
        return syntaxhighlight_pygments(mimetype)
    except Exception as e:
        logger.info(e)
        return null_contextmanager_filter


def syntaxhighlight_pygments(mimetype):
    from pygments import highlight
    from pygments.lexers import get_lexer_for_mimetype
    from pygments.formatters import TerminalFormatter

    lexer = get_lexer_for_mimetype(mimetype, encoding='utf-8')
    formatter = TerminalFormatter(encoding='utf-8')

    @contextmanager
    def filter(output):
        with make_temp_file() as f:
            yield f
            f.seek(0)
            code = f.read()
        highlight(code, lexer, formatter, output)
    return filter


@contextmanager
def make_temp_file():
    fd, name = tempfile.mkstemp()
    with unlink_path(name):
        with os.fdopen(fd, 'w+') as f:
            yield f


@contextmanager
def unlink_path(path):
    import os
    try:
        yield
    finally:
        os.unlink(path)


def pager():
    pager_cmd = os.environ.get('PAGER')
    if pager_cmd:
        pager_cmd = shlex.split(pager_cmd)
        return output_thru_subprocess(pager_cmd)
    return pager_less


pager_less = output_thru_subprocess(['less', '-R'])


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
    except Exception as e:
        logger.exception(e)
        logger.warning('%s cannot be deleted', path)
