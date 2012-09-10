# -*- coding: utf-8 -*-
#
#                   GNU AFFERO GENERAL PUBLIC LICENSE
#                      Version 3, 19 November 2007
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


class FileWrapper(object):

    def __init__(self, f):
        self.wrapped = f

    def __iter__(self):
        return self.wrapped.__iter__()

    def __getattr__(self, name):
        return getattr(self.wrapped, name)

    def __enter__(self):
        self.wrapped.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        return self.wrapped.__exit__(type, value, traceback)


class SubprocessError(Exception):
    pass


class SubprocessReadable(FileWrapper):

    def __init__(self, f, subprocess):
        self.wrapped = f
        self.subprocess = subprocess

    def read(self, n=None):
        if n is None:
            data = self.wrapped.read()
            returncode = self.subprocess.wait()
            assert returncode is not None
            if returncode != 0:
                raise SubprocessError(returncode)
        else:
            data = self.wrapped.read(n)
            if len(data) < n:
                # this is the last data
                returncode = self.subprocess.wait()
                assert returncode is not None
                if returncode != 0:
                    raise SubprocessError(returncode)
        return data


def which(program):
    import os, os.path
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file


class ProgramNotFound(Exception):
    pass


def tmpfile():
    import tempfile
    f = tempfile.TemporaryFile()
    try:
        f = f.file # for non-POSIX platform
    except AttributeError:
        pass
    return f


def xmllint(*options, **kwargs):
    ''' create a `xmllint' function

        returns a transform function
    '''

    xmllint_path = kwargs.get('xmllint_path', 'xmllint')
    options += ('-', )
    return external_transform(xmllint_path, *options)


def external_transform(program, *options):
    ''' create a transform function with the specified external program

    :returns: a transform function
    '''

    def autoclose(p):
        ''' start a detached thread which waits the given subprocess terminates. '''
        import threading
        t = threading.Thread(target=p.wait)
        t.daemon = True
        t.start()

    def transform(infile=None, outfile=None):
        ''' transform file streams with `%(program)s' program

            `%(program)s' executable should be in PATH directories.

            transform(infile, outfile) -> returncode
                : transform infile stream into outfile stream

            transform(infile) -> readable
                : returns transformed stream (readable sink)

            transform(outfile=outfile) -> writable
                : returns stream to be transformed (writable source)

            transform() -> (readable, writable)
                : returns a tuple of (writable source, readable sink) of transformation
        ''' % dict(program=program)
        import subprocess

        stdin = infile.fileno() if infile is not None else subprocess.PIPE
        stdout = outfile.fileno() if outfile is not None else subprocess.PIPE
        stderr = tmpfile()

        program_found = which(program)
        if not program_found:
            raise ProgramNotFound(program)

        logger.info('program %s: found at %s ', program, program_found)

        popen_args = [program_found] + list(options)
        p = subprocess.Popen(popen_args,
                             stdin=stdin,
                             stdout=stdout,
                             stderr=stderr)

        logger.info('program %s started', program_found)

        if infile is None and outfile is None:
            return SubprocessReadable(p.stdout, p), p.stdin # readable, writable
        elif outfile is None:
            return SubprocessReadable(p.stdout) # readable transformed stream
        elif infile is None:
            return p.stdin # writable stream to be transformed
        else:
            try:
                return p.wait()
            finally:
                logger.info('program %s exited', program_found)

    return transform


def xmllint_readable(f, *options, **kwargs):

    transform = xmllint(*options, **kwargs)

    try:
        try:
            f.fileno
            return transform(infile=f)
        except AttributeError:
            r, w = transform()
            assert isinstance(r, SubprocessReadable)
            def pump():
                try:
                    while True:
                        data = f.read(4096)
                        if len(data) == 0:
                            return
                        w.write(data)
                finally:
                    w.close()
            import threading
            t = threading.Thread(target=pump)
            t.start()
            return r
    except ProgramNotFound:
        return f
