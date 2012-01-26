# -*- coding: utf-8 -*-

class Storage(object):
    def __iter__(self):
        ''' generates item names '''
        raise NotImplementedError()

    def __getitem__(self, name):
        ''' return the item specified by the name '''
        raise NotImplementedError()


class StorageWrapper(Storage):
    def __init__(self, stg):
        self.stg = stg
    def __iter__(self):
        return iter(self.stg)
    def __getitem__(self, name):
        return self.stg[name]
    def __getattr__(self, name):
        return getattr(self.stg, name)


def iter_storage_leafs(stg, basepath=''):
    ''' iterate every leaf nodes in the storage

        stg: an instance of Storage
    '''
    for name in stg:
        path = basepath + name
        item = stg[name]
        if isinstance(item, Storage):
            for x in iter_storage_leafs(item, path+'/'):
                yield x
        else:
            yield path


def unpack(stg, outbase):
    ''' unpack a storage into outbase directory

        stg: an instance of Storage
        outbase: path to a directory in filesystem (should not end with '/')
    '''
    import os, os.path
    for name in stg:
        outpath = os.path.join(outbase, name)
        item = stg[name]
        if isinstance(item, Storage):
            if not os.path.exists(outpath):
                os.mkdir(outpath)
            unpack(item, outpath)
        else:
            try:
                outfile = file(outpath, 'w')
                try:
                    outfile.write(item.read())
                finally:
                    outfile.close()
            finally:
                item.close()
