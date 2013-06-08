# -*- coding: utf-8 -*-
from __future__ import with_statement
import logging
import os.path
from contextlib import contextmanager


logger = logging.getLogger(__name__)


class FileSystemNode(object):

    def __init__(self, path):
        self.path = path


class FileSystemFile(FileSystemNode):

    def open(self, *args, **kwargs):
        return file(self.path, *args, **kwargs)

    @contextmanager
    def path_on_filesystem(self):
        yield self.path

    def delete(self):
        os.unlink(self.path)


class FileSystemFolder(FileSystemNode):

    def __iter__(self):
        return iter(os.listdir(self.path))

    def __getitem__(self, name):
        if name in self:
            path = os.path.join(self.path, name)
            if os.path.isdir(path):
                return FileSystemFolder(path=path)
            else:
                return FileSystemFile(path=path)
        raise KeyError(name)

    def file(self, name):
        path = os.path.join(self.path, name)
        return FileSystemFile(path)
    
    def folder(self, name):
        path = os.path.join(self.path, name)
        os.mkdir(path)
        return FileSystemFolder(path)


class FileSystemStorage(FileSystemFolder):

    def __init__(self, path, mode='r'):
        if not os.path.exists(path):
            if mode == 'r':
                raise IOError('%s: not found' % path)
            elif mode in ('a', 'w'):
                os.makedirs(path)
        if not os.path.isdir(path):
            raise IOError('%s: not a directory' % path)
        FileSystemFolder.__init__(self, path)

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()
