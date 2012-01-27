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


class ItemModifier(object):
    ''' modifier for a Storage item '''

    def conversion(self, item):
        return item

    def other_formats(self):
        return dict()


class ItemsModifyingStorage(StorageWrapper):
    ''' a Storage class which modifies its base storage items

        It modifies base storage items:
            - by conversion them
            - by adding differently-formatted items based on them
        through `ItemModifier's, which is resolved by resolve_modifier()

        Derived classes may implement resolve_modifier(), which returns
        an ItemModifier for the base storage item specified by the `name'
    '''

    def __iter__(self):
        for name in self.stg:
            yield name
            modifier = self.resolve_modifier(name)
            if modifier:
                for ext in modifier.other_formats():
                    yield name + ext

    def __getitem__(self, name):
        try:
            item = self.stg[name]
        except KeyError:
            # 기반 스토리지에는 없으므로, ItemModifier들이 제공하는
            # other_formats() 아이템들 중에서 찾아본다.
            for root in self.stg:
                modifier = self.resolve_modifier(root)
                if modifier:
                    for ext, func in modifier.other_formats().items():
                        if root + ext == name:
                            return func(self.stg[root])
        else:
            # 기반 스토리지에서 찾은 아이템에 대해, ItemModifier가 있으면
            # conversion()한다.
            modifier = self.resolve_modifier(name)
            if modifier:
                return modifier.conversion(item)
            return item

    def resolve_modifier(self, name):
        ''' return an ItemModifier for the specified storage item '''
        pass


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


def open_storage_item(stg, path):
    if isinstance(path, basestring):
        path_segments = path.split('/')
    else:
        path_segments = path

    item = stg
    for name in path_segments:
        item = item[name]
    return item
