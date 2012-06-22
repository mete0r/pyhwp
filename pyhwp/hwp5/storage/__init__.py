# -*- coding: utf-8 -*-


def is_storage(item):
    return hasattr(item, '__iter__') and hasattr(item, '__getitem__')


def is_stream(item):
    return hasattr(item, 'open') and callable(item.open)


class ItemWrapper(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped
    def __getattr__(self, name):
        return getattr(self.wrapped, name)


class StorageWrapper(ItemWrapper):
    def __iter__(self):
        return iter(self.wrapped)
    def __getitem__(self, name):
        return self.wrapped[name]


class ItemConversionStorage(StorageWrapper):

    def __getitem__(self, name):
        item = self.wrapped[name]
        # 기반 스토리지에서 찾은 아이템에 대해, conversion()한다.
        conversion = self.resolve_conversion_for(name)
        if conversion:
            return conversion(item)
        return item

    def resolve_conversion_for(self, name):
        ''' return a conversion function for the specified storage item '''
        pass


class ExtraItemStorage(StorageWrapper):

    def __iter__(self):
        for name in self.wrapped:
            yield name

            item = self.wrapped[name]
            if hasattr(item, 'other_formats'):
                other_formats = item.other_formats()
                if other_formats:
                    for ext in other_formats:
                        yield name + ext

    def __getitem__(self, name):
        try:
            item = self.wrapped[name]
            if is_storage(item):
                item = ExtraItemStorage(item)
            return item
        except KeyError:
            # 기반 스토리지에는 없으므로, other_formats() 중에서 찾아본다.
            for root in self.wrapped:
                item = self.wrapped[root]
                if hasattr(item, 'other_formats'):
                    other_formats = item.other_formats()
                    if other_formats:
                        for ext, func in other_formats.items():
                            if root + ext == name:
                                return Open2Stream(func)
            raise


class Open2Stream(object):

    def __init__(self, open):
        self.open = open


def iter_storage_leafs(stg, basepath=''):
    ''' iterate every leaf nodes in the storage

        stg: an instance of Storage
    '''
    for name in stg:
        path = basepath + name
        item = stg[name]
        if is_storage(item):
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
        if is_storage(item):
            if not os.path.exists(outpath):
                os.mkdir(outpath)
            unpack(item, outpath)
        else:
            f = item.open()
            try:
                outfile = file(outpath, 'w')
                try:
                    outfile.write(f.read())
                finally:
                    outfile.close()
            finally:
                f.close()


def open_storage_item(stg, path):
    if isinstance(path, basestring):
        path_segments = path.split('/')
    else:
        path_segments = path

    item = stg
    for name in path_segments:
        item = item[name]
    return item

def printstorage(stg, basepath=''):
    names = list(stg)
    names.sort()
    for name in names:
        path = basepath + name
        item = stg[name]
        if is_storage(item):
            printstorage(item, path+'/')
        elif is_stream(item):
            print path.encode('string_escape')
