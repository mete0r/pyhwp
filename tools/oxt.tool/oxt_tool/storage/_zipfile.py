# -*- coding: utf-8 -*-
from __future__ import with_statement
import logging
import os.path
from zipfile import ZIP_DEFLATED
from path import split as path_split
from path import get_ancestors as path_ancestors


logger = logging.getLogger(__name__)


def zipfile_nodes(zipfile):
    seen = set()
    for path in zipfile.namelist():
        for anc_path in path_ancestors(path):
            if anc_path not in seen:
                yield anc_path, ZipFileFolder(zipfile, anc_path)
                seen.add(anc_path)
        if path not in seen:
            if path.endswith('/'):
                yield path, ZipFileFolder(zipfile, path)
            else:
                yield path, ZipFileFile(zipfile, path)
            seen.add(path)


class ZipFileNode(object):
    
    def __init__(self, zipfile, path):
        self.zipfile = zipfile
        self.path = path


class ZipFileFile(ZipFileNode):

    def open(self, mode='r', compress_type=ZIP_DEFLATED):
        if mode.startswith('r'):
            return ZipFileStream(self.zipfile.open(self.path, mode))
        elif mode == 'w':
            return ZipFileStream(ZipFileWritable(self.zipfile, self.path,
                                                 compress_type=compress_type))

    def put(self, filesystem_path, compress_type=ZIP_DEFLATED):
        self.zipfile.write(filesystem_path, self.path, compress_type)


class ZipFileFolder(ZipFileNode):

    def childs(self):
        prefix = path_split(self.path)
        prefix_len = len(prefix)
        for path, node in zipfile_nodes(self.zipfile):
            path_segments = path_split(path)
            if len(path_segments) == prefix_len + 1:
                if path_segments[:prefix_len] == prefix:
                    yield path_segments[-1], node

    def __iter__(self):
        for name, node in self.childs():
            yield name

    def __getitem__(self, name):
        for node_name, node in self.childs():
            if node_name == name:
                return node
        raise KeyError(name)

    def file(self, name):
        path = os.path.join(self.path, name)
        return ZipFileFile(self.zipfile, path)

    def folder(self, name):
        path = os.path.join(self.path, name)
        return ZipFileFolder(self.zipfile, path)


class ZipFileStorage(ZipFileFolder):

    def __init__(self, *args, **kwargs):
        import zipfile
        self.zipfile = zipfile.ZipFile(*args, **kwargs)
        self.path = ''

    def childs(self):
        for path, node in zipfile_nodes(self.zipfile):
            path_segments = path_split(path)
            if len(path_segments) == 1:
                yield path_segments[-1], node

    def close(self):
        self.zipfile.close()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()


class ZipFileStream(object):

    def __init__(self, stream):
        self.stream = stream

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def __enter__(self):
        return self.stream

    def __exit__(self, *args, **kwargs):
        self.close()


class ZipFileWritable(object):

    def __init__(self, zipfile, path, compress_type=ZIP_DEFLATED):
        self.zipfile = zipfile
        self.path = path
        self.compress_type = compress_type

        import tempfile
        fd, tmp_path = tempfile.mkstemp()
        self.tmp_f = os.fdopen(fd, 'w')
        self.tmp_path = tmp_path

    def __getattr__(self, name):
        return getattr(self.tmp_f, name)

    def close(self):
        self.tmp_f.close()
        self.zipfile.write(self.tmp_path, self.path, self.compress_type)
        os.unlink(self.tmp_path)
