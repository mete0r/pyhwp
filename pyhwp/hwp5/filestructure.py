# -*- coding: utf-8 -*-
import os.path
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import zlib
from OleFileIO_PL import OleFileIO, isOleFile

from .utils import cached_property
from .dataio import INT32, UINT32, UINT16, Flags, Struct, ARRAY, N_ARRAY
from . import dataio

class BYTES(type):
    def __new__(mcs, size):
        return type.__new__(mcs, 'BYTES%d'%size, (str,), dict(size=size))
    def __init__(self, size):
        return type.__init__(self, None, None, None)
    def read(self, f, context=None):
        if self.size < 0:
            return f.read()
        else:
            return f.read(self.size)

class VERSION(tuple):
    def read(cls, f, context=None):
        version = f.read(4)
        return (ord(version[3]), ord(version[2]), ord(version[1]), ord(version[0]))
    read = classmethod(read)

class FileHeader(Struct):
    Flags = Flags(UINT32,
        0, 'compressed',
        1, 'password',
        2, 'distributable',
        3, 'script',
        4, 'drm',
        5, 'xmltemplate_storage',
        6, 'history',
        7, 'cert_signed',
        8, 'cert_encrypted',
        9, 'cert_signature_extra',
        10, 'cert_drm',
        11, 'ccl',
        )
    def attributes(cls, context):
        yield BYTES(32), 'signature'
        yield VERSION, 'version'
        yield cls.Flags, 'flags'
        yield BYTES(216), 'reserved'
    attributes = classmethod(attributes)

class TextField(unicode):
    def read(cls, f, context=None):
        unk0 = UINT32.read(f, None) # 1f
        assert unk0 == 0x1f
        size = UINT32.read(f, None)
        if size > 0:
            data = f.read(2*(size))
        else:
            data = ''
        if size & 1:
            f.read(2)
        return data.decode('utf-16le', 'replace')
    read = classmethod(read)

class SummaryInfo(Struct):
    def attributes(cls, context):
        if context['version'] < (5, 0, 1, 0):
            yield ARRAY(UINT32, 0230/4), '_unk0'
        else:
            yield ARRAY(UINT32, 0250/4), '_unk0'
        yield TextField, 'title'
        yield TextField, 'subject'
        yield TextField, 'author'
        yield TextField, 'datetime'
        yield TextField, 'keywords'
        yield TextField, 'etc'
        yield TextField, 'hidden_username'
        yield TextField, 'hidden_progversion'
        yield ARRAY(ARRAY(UINT16, 6), 3), '_unk1'
        #yield ARRAY(N_ARRAY(UINT32, UINT32), 2), '_unk2'
    attributes = classmethod(attributes)


def recode(backend_stream, backend_encoding, frontend_encoding, errors='strict'):
    import codecs
    enc = codecs.getencoder(frontend_encoding)
    dec = codecs.getdecoder(frontend_encoding)
    rd = codecs.getreader(backend_encoding)
    wr = codecs.getwriter(backend_encoding)
    return codecs.StreamRecoder(backend_stream, enc, dec, rd, wr, errors)

def is_hwp5file(filename):
    if not isOleFile(filename):
        return False
    olefile = OleFileIO(filename)
    return olefile.exists('FileHeader')

def open_fileheader(olefile):
    return olefile.openstream('FileHeader')

def get_fileheader(olefile):
    f = open_fileheader(olefile)
    attributes = FileHeader.read(f)
    fileheader = FileHeader()
    fileheader.__dict__.update((name, type(attributes.get(name))) for type, name in FileHeader.attributes(dict()))
    return fileheader

def open_summaryinfo(olefile):
    return olefile.openstream('\005HwpSummaryInformation')

def open_previewtext(olefile, charset=None):
    f = olefile.openstream('PrvText')
    if charset:
        f = recode(f, 'utf-16le', charset)
    return f

def open_previewimage(olefile):
    return olefile.openstream('PrvImage')

def open_docinfo(olefile, compressed=True):
    f = olefile.openstream('DocInfo')
    if compressed:
        f = StringIO(zlib.decompress(f.read(), -15)) # without gzip header
    return f

def open_bodytext(olefile, idx, compressed=True):
    try:
        f = olefile.openstream('BodyText/Section'+str(idx))
    except IOError:
        raise IndexError(idx)
    if compressed:
        f = StringIO(zlib.decompress(f.read(), -15))
    return f

def open_viewtext(olefile, idx):
    try:
        f = olefile.openstream('ViewText/Section'+str(idx))
    except IOError:
        raise IndexError(idx)
    return f

def open_viewtext_head(olefile, idx):
    f = open_viewtext(olefile, idx)
    head = f.read(4+256)
    return StringIO(head)

def open_viewtext_tail(olefile, idx):
    f = open_viewtext(olefile, idx)
    f.seek(4+256)
    return f

def open_bindata(olefile, name, compressed=True):
    try:
        f = olefile.openstream('BinData/%s'%name)
    except IOError:
        raise KeyError(name)
    if compressed:
        f = StringIO(zlib.decompress(f.read(), -15))
    return f

def open_script(olefile, name, compressed=True):
    try:
        f = olefile.openstream('Scripts/%s'%name)
    except IOError:
        raise KeyError(name)
    if compressed:
        return StringIO(zlib.decompress(f.read(), -15))
    return f

def list_streams(olefile):
    for e in olefile.listdir():
        yield os.path.join(*e)

def list_sections(olefile):
    prefix = 'BodyText/Section'
    l = []
    for name in list_streams(olefile):
        if name.startswith(prefix):
            l.append( int(name[len(prefix):]) )
    l.sort()
    return l

def list_bindata(olefile):
    for name in list_streams(olefile):
        prefix = 'BinData/'
        if name.startswith(prefix):
            yield name[len(prefix):]

class BadFormatError(Exception):
    def __str__(self):
        return '%s: \'%s\''%(self.args)

def open(filename):
    if not is_hwp5file(filename):
        raise BadFormatError('Not an hwp5 file', filename)
    olefile = OleFileIO(filename)
    return File(olefile)

def walk(hwpfile, dirpath=''):
    if dirpath == '' or dirpath == '/':
        base = ''
    else:
        base = dirpath + '/'
    names = hwpfile.listdir(dirpath)
    files = []
    dirs = []
    for name in names:
        path = base+name
        if hwpfile.is_storage(path):
            dirs.append(name)
        else:
            files.append(name)
    yield dirpath, dirs, files
    for name in dirs:
        path = base+name
        for x in walk(hwpfile, path):
            yield x


class Storage(object):
    def __iter__(self):
        ''' generates item names '''
        raise NotImplementedError()

    def __getitem__(self, name):
        ''' return the item specified by the name '''
        raise NotImplementedError()

def olefile_listdir(olefile, path):
    if path == '' or path == '/':
        # we use a list instead of a set
        # for python 2.3 compatibility
        yielded = []

        for stream in olefile.listdir():
            top_item = stream[0]
            if top_item in yielded:
                continue
            yielded.append(top_item)
            yield top_item
        return

    if not olefile.exists(path):
        raise IOError('%s not exists'%path)
    if olefile.get_type(path) != 1:
        raise IOError('%s not a storage'%path)
    path_segments = path.split('/')
    for stream in olefile.listdir():
        if len(stream) == len(path_segments) + 1:
            if stream[:-1] == path_segments:
                yield stream[-1]

class OleStorage(Storage):

    def __init__(self, olefile, path=''):
        self.olefile = olefile
        self.path = path # path DOES NOT end with '/'

    def __iter__(self):
        return olefile_listdir(self.olefile, self.path)

    def __getitem__(self, name):
        if self.path == '' or self.path == '/':
            path = name
        else:
            path = self.path + '/' + name
        if not self.olefile.exists(path):
            raise KeyError('%s not found'%path)
        t = self.olefile.get_type(path)
        if t == 1: # Storage
            return OleStorage(self.olefile, path)
        elif t == 2: # Stream
            return self.olefile.openstream(path)
        else:
            raise KeyError('%s is invalid'%path)


class StorageWrapper(Storage):
    def __init__(self, stg):
        self.stg = stg
    def __iter__(self):
        return iter(self.stg)
    def __getitem__(self, name):
        return self.stg[name]


def uncompress(stream):
    ''' uncompress inputstream

        stream: a file-like readable
        returns a file-like readable
    '''
    return StringIO(zlib.decompress(stream.read(), -15)) # without gzip header


class CompressedStorage(StorageWrapper):
    ''' uncompress streams in the underlying storage '''
    def __getitem__(self, name):
        item = self.stg[name]
        if not isinstance(item, Storage):
            return uncompress(item)
        else:
            return item


class File(object):

    def __init__(self, olefile):
        self.olefile = olefile

    def close(self):
        if hasattr(self.olefile, 'close'):
            self.olefile.close()

    def listdir(self, path):
        if path == '' or path == '/':
            # we use a list instead of a set
            # for python 2.3 compatibility
            yielded = []

            for stream in self.olefile.listdir():
                top_item = stream[0]
                if top_item in yielded:
                    continue
                yielded.append(top_item)
                yield top_item
            return

        if not self.olefile.exists(path):
            raise IOError('not exists')
        if self.olefile.get_type(path) != 1:
            raise IOError('not a storage')
        path_segments = path.split('/')
        for stream in self.olefile.listdir():
            if len(stream) == len(path_segments) + 1:
                if stream[:-1] == path_segments:
                    yield stream[-1]

    def is_storage(self, path):
        return self.olefile.get_type(path) == 1 # OleFileIO_PL.STGTY_STORAGE

    def is_stream(self, path):
        return self.olefile.get_type(path) == 2# OleFileIO_PL.STGTY_STREAM

    def list_streams(self):
        return list_streams(self.olefile)

    def list_bodytext_sections(self):
        return list_sections(self.olefile)

    def list_bindata(self):
        return list_bindata(self.olefile)

    def _fileheader(self):
        return open_fileheader(self.olefile)
    fileheader = cached_property(lambda self: get_fileheader(self.olefile))

    def _summaryinfo(self):
        return open_summaryinfo(self.olefile)
    def summaryinfo(self):
        f = open_summaryinfo(self.olefile)
        context = dict(version=self.fileheader.version)
        summaryinfo = SummaryInfo.read(f, context)
        #print '#### %o'%f.tell()
        return summaryinfo
    summaryinfo = property(summaryinfo)

    def preview_text(self):
        return open_previewtext(self.olefile, 'utf-8')

    def preview_image(self):
        return open_previewimage(self.olefile)

    def docinfo(self):
        return open_docinfo(self.olefile, self.fileheader.flags.compressed)

    def bodytext(self, idx):
        return open_bodytext(self.olefile, idx, self.fileheader.flags.compressed)

    def viewtext(self, idx):
        return open_viewtext(self.olefile, idx)

    def viewtext_head(self, idx):
        return open_viewtext_head(self.olefile, idx)

    def viewtext_tail(self, idx):
        return open_viewtext_tail(self.olefile, idx)

    def bindata(self, name):
        return open_bindata(self.olefile, name, self.fileheader.flags.compressed)

    def script(self, name):
        return open_script(self.olefile, name, self.fileheader.flags.compressed)

    def pseudostream(self, name):
        args = name.split('/', 1)
        name = args.pop(0)
        pseudostream = getattr(self, name, None)
        if pseudostream:
            return pseudostream(*args)

def iter_storage_leafs(stg, basepath=''):
    ''' iterate every leaf nodes in the storage

        stg: an instance of Storage
    '''
    for name in stg:
        if basepath == '' or basepath == '/':
            path = name
        else:
            path = basepath+'/'+name

        item = stg[name]
        if isinstance(item, Storage):
            for x in iter_storage_leafs(item, path):
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


def unole():
    import sys
    from OleFileIO_PL import OleFileIO
    import os.path

    olefilepath = sys.argv[1]
    olefile = OleFileIO(olefilepath)
    olestg = OleStorage(olefile)
    olefilename = os.path.split(olefilepath)[-1]
    base = '.'.join(olefilename.split('.')[:-1])
    if not os.path.exists(base):
        os.mkdir(base)
    unpack(olestg, base)

def main():
    from ._scriptutils import OptionParser, args_pop, open_or_exit
    op = OptionParser(usage='usage: %prog [options] filename <stream>')
    options, args = op.parse_args()

    filename = args_pop(args, 'filename')
    file = open_or_exit(open, filename)

    if len(args) == 0:
        print 'FileHeader'
        print '----------'
        print 'signature:%s'%file.fileheader.signature
        print '  version: %d.%d.%d.%d'%file.fileheader.version
        print '    flags: 0x%x'%file.fileheader.flags
        for k, v in FileHeader.Flags.dictvalue(file.fileheader.flags).iteritems():
            print '%20s: %d'%(k, v)
        print ''
        print 'Pseudo streams'
        print '--------------'
        print '          _fileheader : synonym of FileHeader'
        print '         _summaryinfo : synonym of \\x05HwpSummaryInformation'
        print '         preview_text : PrvText (UTF-8)'
        print '        preview_image : synonym of PrvImage'
        print '              docinfo : DocInfo (uncompressed, record stream)'
        print '     bodytext/<index> : BodyText/Section<index> (uncompressed, record stream)'
        print '   bindata/<filename> : BIN/<filename> (uncompressed)'
        print '    script/<filename> : Scripts/<filename> (uncompressed)'
        print '     viewtext/<index> : ViewText/Section<index>'
        print 'viewtext_head/<index> : head part of ViewText/Section<index> (a record)'
        print 'viewtext_tail/<index> : tail part of ViewText/Section<index> (block data)'
        print ''
        print 'Raw streams'
        print '-----------'
        for name in file.list_streams():
            print name.encode('string_escape')
        print ''
        print 'SummaryInfo'
        print '-----------'
        for k, v in file.summaryinfo.iteritems():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            print '%20s: %s'%(k, v)
        return 0

    streamname = args_pop(args, '<stream>')
    if streamname == 'list':
        streamname = args_pop(args, 'bindata | bodytext')
        if streamname == 'bindata':
            for name in file.list_bindata():
                print name
        elif streamname == 'bodytext':
            for idx in file.list_bodytext_sections():
                print 'bodytext/%d'%idx
        return 0
    stream = file.pseudostream(streamname)
    if not stream:
        stream = file.openstream(streamname)
    import sys
    sys.stdout.write(stream.read())
