# -*- coding: utf-8 -*-
from __future__ import with_statement
import logging
from contextlib import contextmanager


logger = logging.getLogger(__name__)


def open_storage(path, mode='r', default_storage_factory=None):
    import os.path
    import zipfile
    import fs
    import _zipfile
    if os.path.exists(path):
        if os.path.isdir(path):
            return fs.FileSystemStorage(path)
        elif zipfile.is_zipfile(path):
            return _zipfile.ZipFileStorage(path, mode)
        raise IOError('%s: unsupported storage' % path)
    elif callable(default_storage_factory):
        return default_storage_factory(path, mode)
    else:
        raise IOError('%s: cannot open' % path)


def resolve_path(folder, path):
    ''' resolve path in a folder

    :param folder: a folder (should have ``__getitem__``)
    :param path: path to resolve
    :returns: a node or None
    '''
    if path in ('', '/'):
        return folder

    import os
    path_segments = path.split(os.sep)
    assert len(path_segments) > 0

    for seg in path_segments:
        if not hasattr(folder, '__getitem__'):
            return None
        try:
            node = folder[seg]
        except KeyError:
            return None
        else:
            folder = node

    return node


def makedirs(folder, path):
    from path import split as path_split
    path_segments = path_split(path)
    for seg in path_segments:
        if seg in folder:
            folder = folder[seg]
        else:
            folder = folder.folder(seg)
    return folder


def makedirs_to_file(folder, path):
    import os.path
    dirname, name = os.path.split(path)
    if name == '':
        msg = '%s: invalid path' % path
        raise ValueError(msg)
    folder = makedirs(folder, dirname)
    return folder.file(name)


def put_file(node, path, **kwargs):
    if hasattr(node, 'put'):
        node.put(path, **kwargs)
    elif hasattr(node, 'open'):
        with file(path, 'rb') as f:
            with node.open('w') as g:
                stream_copy(f, g)
    else:
        raise IOError('node supports neither put nor open')


def get_file(node, path):
    if hasattr(node, 'get'):
        node.get(path)
    elif hasattr(node, 'open'):
        with node.open() as f:
            with file(path, 'wb') as g:
                stream_copy(f, g)
    else:
        raise IOError('node supports neither get nor open')


@contextmanager
def openable_path_on_filesystem(node, writeback=False):
    if hasattr(node, 'path_on_filesystem'):
        with node.path_on_filesystem() as path:
            yield path
    else:
        import os
        from tempfile import mkstemp
        fd, path = mkstemp()
        try:
            with node.open() as f:
                with os.fdopen(fd, 'w+') as g:
                    fd = None
                    stream_copy(f, g)
                # fd closed
            yield path

            if writeback:
                put_file(node, path)
        finally:
            if fd is not None:
                os.close(fd)
            os.unlink(path)


def copy_file(src_node, dst_node):
    if (hasattr(dst_node, 'path_on_filesystem') and
        hasattr(src_node, 'get')):
        with openable_path_on_filesystem(dst_node, writeback=True) as dst_path:
            get_file(src_node, dst_path)
    with openable_path_on_filesystem(src_node) as src_path:
        put_file(dst_node, src_path)


def stream_copy(src, dst):
    while True:
        data = src.read(4096)
        if len(data) == 0:
            return
        dst.write(data)


def iterate_nodes_recursively(folder, folder_path=''):
    import os.path
    for name in folder:
        node = folder[name]
        node_path = os.path.join(folder_path, name)
        yield node_path, node
        if hasattr(node, '__iter__') and hasattr(node, '__getitem__'):
            for x in iterate_nodes_recursively(node, node_path):
                yield x


def iterate_files_recursively(folder, folder_path=''):
    for path, node in iterate_nodes_recursively(folder, folder_path):
        if hasattr(node, 'open'):
            yield path, node


def ls_main():
    doc = '''Usage: storage-ls [options] <storage>

    --help      Show this screen.
    '''

    from docopt import docopt
    args = docopt(doc)

    root_path = args['<storage>'] or '.'
    with open_storage(root_path, 'r') as stg:
        for path, node in iterate_files_recursively(stg):
            print path


def put_main():
    doc = '''Usage: storage-put [options] <storage> <path> <file>

    --help      Show this screen.
    '''

    from docopt import docopt
    args = docopt(doc)

    import os.path
    root_path = args['<storage>'] or '.'
    with open_storage(root_path, 'a') as stg:
        path = args['<path>']
        file_path = args['<file>']

        if os.path.exists(file_path):
            node = makedirs_to_file(stg, path)
            put_file(node, file_path)
        else:
            logger.error('%s: not found', file_path)
            raise SystemExit(1)


def get_main():
    doc = '''Usage: storage-get [options] <storage> <path> <file>

    --help      Show this screen.
    '''

    from docopt import docopt
    args = docopt(doc)

    root_path = args['<storage>'] or '.'
    with open_storage(root_path, 'a') as stg:
        path = args['<path>']
        file_path = args['<file>']

        node = resolve_path(stg, path)
        if node:
            get_file(node, file_path)
        else:
            logger.error('%s: not found', path)
            raise SystemExit(1)
