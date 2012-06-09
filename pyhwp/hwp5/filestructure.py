# -*- coding: utf-8 -*-
import os.path
import codecs
import zlib
from OleFileIO_PL import OleFileIO, isOleFile
from .utils import cached_property
from .dataio import UINT32, UINT16, Flags, Struct, ARRAY
from .storage import StorageWrapper
from .storage import ItemConversionStorage
from .importhelper import importStringIO
import logging


logger = logging.getLogger(__name__)


StringIO = importStringIO()


class BYTES(type):
    def __new__(mcs, size):
        return type.__new__(mcs, 'BYTES%d' % size, (str,), dict(size=size))

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
        return (ord(version[3]), ord(version[2]),
                ord(version[1]), ord(version[0]))
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
        unk0 = UINT32.read(f, None)  # 1f
        assert unk0 == 0x1f
        size = UINT32.read(f, None)
        if size > 0:
            data = f.read(2 * size)
        else:
            data = ''
        if size & 1:
            f.read(2)
        return data.decode('utf-16le', 'replace')
    read = classmethod(read)


class SummaryInfo(Struct):
    def attributes(cls, context):
        if context['version'] < (5, 0, 1, 0):
            yield ARRAY(UINT32, 0230 / 4), '_unk0'
        else:
            yield ARRAY(UINT32, 0250 / 4), '_unk0'
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


def recoder(backend_encoding, frontend_encoding, errors='strict'):
    def recode(backend_stream):
        import codecs
        enc = codecs.getencoder(frontend_encoding)
        dec = codecs.getdecoder(frontend_encoding)
        rd = codecs.getreader(backend_encoding)
        wr = codecs.getwriter(backend_encoding)
        return codecs.StreamRecoder(backend_stream, enc, dec, rd, wr, errors)
    return recode


def is_hwp5file(filename):
    if not isOleFile(filename):
        return False
    olefile = OleFileIO(filename)
    return olefile.exists('FileHeader')


def open_fileheader(olefile):
    return olefile.openstream('FileHeader')


def decode_fileheader(f):
    attributes = FileHeader.read(f)
    fileheader = FileHeader()
    fileheader.__dict__.update((name, type(attributes.get(name)))
                               for type, name in FileHeader.attributes(dict()))
    return fileheader


def get_fileheader(olefile):
    f = open_fileheader(olefile)
    return decode_fileheader(f)


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
        f = StringIO(zlib.decompress(f.read(), -15))  # without gzip header
    return f


def open_bodytext(olefile, idx, compressed=True):
    try:
        f = olefile.openstream('BodyText/Section' + str(idx))
    except IOError:
        raise IndexError(idx)
    if compressed:
        f = StringIO(zlib.decompress(f.read(), -15))
    return f


def open_viewtext(olefile, idx):
    try:
        f = olefile.openstream('ViewText/Section' + str(idx))
    except IOError:
        raise IndexError(idx)
    return f


def open_viewtext_head(olefile, idx):
    f = open_viewtext(olefile, idx)
    head = f.read(4 + 256)
    return StringIO(head)


def open_viewtext_tail(olefile, idx):
    f = open_viewtext(olefile, idx)
    f.seek(4 + 256)
    return f


def open_bindata(olefile, name, compressed=True):
    try:
        f = olefile.openstream('BinData/%s' % name)
    except IOError:
        raise KeyError(name)
    if compressed:
        f = StringIO(zlib.decompress(f.read(), -15))
    return f


def open_script(olefile, name, compressed=True):
    try:
        f = olefile.openstream('Scripts/%s' % name)
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
            l.append(int(name[len(prefix):]))
    l.sort()
    return l


def list_bindata(olefile):
    for name in list_streams(olefile):
        prefix = 'BinData/'
        if name.startswith(prefix):
            yield name[len(prefix):]


class BadFormatError(Exception):
    def __str__(self):
        return '%s: \'%s\'' % (self.args)


class GeneratorReader(object):
    ''' convert a string generator into file-like reader

        def gen():
            yield 'hello'
            yield 'world'

        f = GeneratorReader(gen())
        assert 'hell' == f.read(4)
        assert 'oworld' == f.read()
    '''

    def __init__(self, gen):
        self.gen = gen
        self.buffer = ''

    def read(self, size=None):
        if size is None:
            d, self.buffer = self.buffer, ''
            return d + ''.join(self.gen)

        for data in self.gen:
            self.buffer += data
            bufsize = len(self.buffer)
            if bufsize >= size:
                size = min(bufsize, size)
                d, self.buffer = self.buffer[:size], self.buffer[size:]
                return d

        d, self.buffer = self.buffer, ''
        return d

    def close(self):
        self.gen = self.buffer = None


class ZLibIncrementalDecoder(codecs.IncrementalDecoder):
    def __init__(self, errors='strict', wbits=15):
        assert errors == 'strict'
        self.errors = errors
        self.wbits = wbits
        self.reset()

    def decode(self, input, final=False):
        c = self.decompressobj.decompress(input)
        if final:
            c += self.decompressobj.flush()
        return c

    def reset(self):
        self.decompressobj = zlib.decompressobj(self.wbits)


def uncompress_gen(source, bufsize=4096):
    dec = ZLibIncrementalDecoder(wbits=-15)
    exausted = False
    while not exausted:
        input = source.read(bufsize)
        if len(input) < bufsize:
            exausted = True
        yield dec.decode(input, exausted)


def uncompress_experimental(source, bufsize=4096):
    ''' uncompress inputstream

        stream: a file-like readable
        returns a file-like readable
    '''
    return GeneratorReader(uncompress_gen(source, bufsize))


def uncompress(stream):
    ''' uncompress inputstream

        stream: a file-like readable
        returns a file-like readable
    '''
    return StringIO(zlib.decompress(stream.read(), -15))  # without gzip header


class CompressedStream(object):

    def __init__(self, item):
        self.item = item

    def open(self):
        return uncompress(self.item.open())


class CompressedStorage(StorageWrapper):
    ''' uncompress streams in the underlying storage '''
    def __getitem__(self, name):
        from hwp5.storage import is_stream
        item = self.stg[name]
        if is_stream(item):
            return CompressedStream(item)
        else:
            return item


class VersionSensitiveItem(object):

    def __init__(self, item, version):
        self.item = item
        self.version = version

    def open(self):
        return self.item.open()

    def other_formats(self):
        return dict()


class Hwp5FileBase(ItemConversionStorage):

    def resolve_conversion_for(self, name):
        if name == 'FileHeader':
            return HwpFileHeader

    def get_fileheader(self):
        return self['FileHeader']

    fileheader = cached_property(get_fileheader)

    header = fileheader


class Hwp5DistDocStream(VersionSensitiveItem):

    def head_record(self):
        item = self.open()
        from .recordstream import read_record
        return read_record(item, 0)

    def head_record_stream(self):
        from .recordstream import record_to_json
        record = self.head_record()
        json = record_to_json(record)
        return GeneratorReader(iter([json]))

    def head(self):
        record = self.head_record()
        return record['payload']

    def head_stream(self):
        return StringIO(self.head())

    def tail(self):
        item = self.open()
        from .recordstream import read_record
        read_record(item, 0)
        assert 4 + 256 == item.tell()
        return item.read()

    def tail_stream(self):
        return StringIO(self.tail())

    def other_formats(self):
        return {'.head.record': self.head_record_stream,
                '.head': self.head_stream,
                '.tail': self.tail_stream}


class Hwp5DistDocStorage(ItemConversionStorage):

    def resolve_conversion_for(self, name):
        def conversion(item):
            return Hwp5DistDocStream(self.stg[name], None)  # TODO: version
        return conversion


class Hwp5DistDoc(ItemConversionStorage):

    def resolve_conversion_for(self, name):
        if name in ('Scripts', 'ViewText'):
            return Hwp5DistDocStorage


class Hwp5Compression(ItemConversionStorage):
    ''' handle compressed streams in HWPv5 files '''

    def resolve_conversion_for(self, name):
        if name in ('BinData', 'BodyText'):
            return CompressedStorage
        elif name == 'DocInfo':
            return CompressedStream
        elif name == 'Scripts':
            if not self.header.flags.distributable:
                return CompressedStorage


class PreviewText(object):

    def __init__(self, item):
        self.open = item.open

    def other_formats(self):
        return {'.utf8': self.open_utf8}

    def open_utf8(self):
        recode = recoder('utf-16le', 'utf-8')
        return recode(self.open())

    def get_utf8(self):
        f = self.open_utf8()
        try:
            return f.read()
        finally:
            f.close()

    utf8 = cached_property(get_utf8)

    def __str__(self):
        return self.utf8


class Sections(ItemConversionStorage):

    section_class = VersionSensitiveItem

    def __init__(self, stg, version):
        self.stg = stg
        self.version = version

    def resolve_conversion_for(self, name):
        def conversion(item):
            return self.section_class(self.stg[name], self.version)
        return conversion

    def other_formats(self):
        return dict()

    def section(self, idx):
        return self['Section%d' % idx]

    def section_indexes(self):
        def gen():
            for name in self:
                if name.startswith('Section'):
                    idx = name[len('Section'):]
                    try:
                        idx = int(idx)
                    except:
                        pass
                    else:
                        yield idx
        indexes = list(gen())
        indexes.sort()
        return indexes

    @property
    def sections(self):
        return list(self.section(idx)
                    for idx in self.section_indexes())


class HwpFileHeader(object):

    def __init__(self, item):
        self.open = item.open

    def to_dict(self):
        f = self.open()
        try:
            return FileHeader.read(f)
        finally:
            f.close()

    value = cached_property(to_dict)

    def get_version(self):
        return self.value['version']

    version = cached_property(get_version)

    def get_flags(self):
        return FileHeader.Flags(self.value['flags'])

    flags = cached_property(get_flags)

    def open_text(self):
        d = FileHeader.Flags.dictvalue(self.value['flags'])
        d['signature'] = self.value['signature']
        d['version'] = '%d.%d.%d.%d' % self.value['version']
        out = StringIO()
        for k, v in sorted(d.items()):
            print >> out, '%s: %s' % (k, v)
        out.seek(0)
        return out

    def other_formats(self):
        return {'.txt': self.open_text}


class HwpSummaryInfo(VersionSensitiveItem):

    def other_formats(self):
        return {'.txt': self.open_text}

    def to_dict(self):
        f = self.open()
        try:
            context = dict(version=self.version)
            summaryinfo = SummaryInfo.read(f, context)
            return summaryinfo
        finally:
            f.close()

    value = cached_property(to_dict)

    def open_text(self):
        out = StringIO()
        for k, v in sorted(self.value.iteritems()):
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            print >> out, '%20s: %s' % (k, v)

        out.seek(0)
        return out


class Hwp5File(ItemConversionStorage):
    ''' represents HWPv5 File

        Hwp5File(stg)

        stg: an instance of Storage
    '''

    def __init__(self, stg):
        from hwp5.storage import is_storage
        from hwp5.storage.ole import OleStorage
        if not is_storage(stg):
            stg = OleStorage(stg)

        stg = Hwp5FileBase(stg)

        if stg.header.flags.distributable:
            stg = Hwp5DistDoc(stg)

        if stg.header.flags.compressed:
            stg = Hwp5Compression(stg)

        self.stg = stg

    def resolve_conversion_for(self, name):
        if name == 'DocInfo':
            return self.with_version(self.docinfo_class)
        if name == 'BodyText':
            return self.with_version(self.bodytext_class)
        if name == 'PrvText':
            return PreviewText
        if name == '\005HwpSummaryInformation':
            return self.with_version(HwpSummaryInfo)

    def with_version(self, f):
        def wrapped(item):
            return f(item, self.header.version)
        return wrapped

    docinfo_class = VersionSensitiveItem
    bodytext_class = Sections

    @cached_property
    def summaryinfo(self):
        return self['\005HwpSummaryInformation']

    @cached_property
    def docinfo(self):
        return self['DocInfo']

    @cached_property
    def preview_text(self):
        return self['PrvText']

    @cached_property
    def bodytext(self):
        return self['BodyText']

    @cached_property
    def viewtext(self):
        return self['ViewText']
