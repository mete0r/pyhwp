# -*- coding: utf-8 -*-


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

    def autoclose(p):
        ''' start a detached thread which waits the given subprocess terminates. '''
        import threading
        t = threading.Thread(target=p.wait)
        t.daemon = True
        t.start()

    def transform(infile=None, outfile=None):
        ''' transform file streams with `xmllint' program

            `xmllint' executable should be in PATH directories.

            transform(infile, outfile) -> returncode
                : transform infile stream into outfile stream

            transform(infile) -> readable
                : returns transformed stream (readable sink)

            transform(outfile=outfile) -> writable
                : returns stream to be transformed (writable source)

            transform() -> (readable, writable)
                : returns a tuple of (writable source, readable sink) of transformation
        '''
        import subprocess
        import logging

        logging.debug('xsltproc process starting')

        stdin = infile.fileno() if infile is not None else subprocess.PIPE
        stdout = outfile.fileno() if outfile is not None else subprocess.PIPE
        stderr = tmpfile()

        xmllint_found = which(xmllint_path)
        if not xmllint_found:
            raise ProgramNotFound(xmllint_path)

        popen_args = [xmllint_found] + list(options) + ['-']
        p = subprocess.Popen(popen_args,
                             stdin=stdin,
                             stdout=stdout,
                             stderr=stderr)

        logging.debug('xmllint process started')

        if infile is None and outfile is None:
            return SubprocessReadable(p.stdout, p), p.stdin # readable, writable
        elif outfile is None:
            return SubprocessReadable(p.stdout) # readable transformed stream
        elif infile is None:
            return p.stdin # writable stream to be transformed
        else:
            return p.wait()

        logging.debug('xmllint process end')
    return transform


def xmllint_readable(f, *options, **kwargs):

    transform = xmllint(*options, **kwargs)

    try:
        try:
            fileno = f.fileno
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
