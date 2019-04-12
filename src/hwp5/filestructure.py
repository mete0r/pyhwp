# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2015 mete0r <mete0r@sarangbang.or.kr>
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
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from io import BytesIO
import logging
import sys

from .bintype import read_type
from .compressed import decompress
from .dataio import UINT32, Flags, Struct
from .errors import InvalidOleStorageError
from .errors import InvalidHwp5FileError
from .storage import ItemWrapper
from .storage import StorageWrapper
from .storage import ItemConversionStorage
from .storage import is_stream
from .storage.ole import OleStorage
from .summaryinfo import CLSID_HWP_SUMMARY_INFORMATION
from .utils import GeneratorTextReader
from .utils import cached_property
from .utils import transcoder

PY3 = sys.version_info.major == 3
if PY3:
    basestring = str


logger = logging.getLogger(__name__)


HWP5_SIGNATURE = b'HWP Document File' + (b'\x00' * 15)


class BYTES(type):
    def __new__(mcs, size):
        decode = staticmethod(lambda bytes, *args, **kwargs: bytes)
        return type.__new__(mcs, str('BYTES(%d)') % size, (str,),
                            dict(fixed_size=size, decode=decode))


class VERSION(object):
    fixed_size = 4

    if PY3:
        def decode(cls, bytes):
            return (bytes[3], bytes[2], bytes[1], bytes[0])
    else:
        def decode(cls, bytes):
            return (ord(bytes[3]), ord(bytes[2]),
                    ord(bytes[1]), ord(bytes[0]))
    decode = classmethod(decode)


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
                  11, 'ccl')

    def attributes(cls):
        yield BYTES(32), 'signature'
        yield VERSION, 'version'
        yield cls.Flags, 'flags'
        yield BYTES(216), 'reserved'
    attributes = classmethod(attributes)


def is_hwp5file(filename):
    ''' Test whether it is an HWP format v5 file. '''
    try:
        olestg = OleStorage(filename)
    except InvalidOleStorageError:
        return False
    return storage_is_hwp5file(olestg)


def storage_is_hwp5file(stg):
    try:
        fileheader = stg['FileHeader']
    except KeyError:
        logger.info('stg has no FileHeader')
        return False
    fileheader = HwpFileHeader(fileheader)
    if fileheader.signature == HWP5_SIGNATURE:
        return True
    else:
        logger.info('fileheader.signature = %r', fileheader.signature)
        return False


class CompressedStream(ItemWrapper):

    def open(self):
        return decompress(self.wrapped.open())


class CompressedStorage(StorageWrapper):
    ''' decompress streams in the underlying storage '''
    def __getitem__(self, name):
        item = self.wrapped[name]
        if is_stream(item):
            return CompressedStream(item)
        else:
            return item


class PasswordProtectedStream(ItemWrapper):

    def open(self):
        # TODO: 현재로선 암호화된 내용을 그냥 반환
        logger.warning('Password-encrypted stream: currently decryption is '
                       'not supported')
        return self.wrapped.open()


class PasswordProtectedStorage(StorageWrapper):
    def __getitem__(self, name):
        item = self.wrapped[name]
        if is_stream(item):
            return PasswordProtectedStream(item)
        else:
            return item


class Hwp5PasswordProtectedDoc(ItemConversionStorage):

    def resolve_conversion_for(self, name):
        if name in ('BinData', 'BodyText', 'Scripts', 'ViewText'):
            return PasswordProtectedStorage
        elif name in ('DocInfo', ):
            return PasswordProtectedStream


class VersionSensitiveItem(ItemWrapper):

    def __init__(self, item, version):
        ItemWrapper.__init__(self, item)
        self.version = version

    def open(self):
        return self.wrapped.open()

    def other_formats(self):
        return dict()


class Hwp5FileBase(ItemConversionStorage):
    ''' Base of an Hwp5File.

    Hwp5FileBase checks basic validity of an HWP format v5 and provides
    `fileheader` property.

    :param stg: an OLE2 structured storage.
    :type stg: an instance of storage, OleFileIO or filename
    :raises InvalidHwp5FileError: `stg` is not a valid HWP format v5 document.
    '''

    def __init__(self, stg):
        if isinstance(stg, basestring):
            try:
                stg = OleStorage(stg)
            except InvalidOleStorageError:
                raise InvalidHwp5FileError('Not an OLE2 Compound Binary File.')

        if not storage_is_hwp5file(stg):
            errormsg = 'Not an HWP Document format v5 storage.'
            raise InvalidHwp5FileError(errormsg)

        ItemConversionStorage.__init__(self, stg)

    def resolve_conversion_for(self, name):
        if name == 'FileHeader':
            return HwpFileHeader

    def get_fileheader(self):
        return self['FileHeader']

    fileheader = cached_property(get_fileheader)

    header = fileheader


class Hwp5DistDocStream(VersionSensitiveItem):

    def open(self):
        from hwp5.distdoc import decode
        encodedstream = self.wrapped.open()
        return decode(encodedstream)

    def head_record(self):
        item = self.wrapped.open()
        from .recordstream import read_record
        return read_record(item, 0)

    def head_record_stream(self):
        from .recordstream import record_to_json
        record = self.head_record()
        json = record_to_json(record)
        return GeneratorTextReader(iter([json]))

    def head(self):
        record = self.head_record()
        return record['payload']

    def head_stream(self):
        return BytesIO(self.head())

    def head_sha1(self):
        from hwp5.distdoc import decode_head_to_sha1
        payload = self.head()
        return decode_head_to_sha1(payload)

    def head_key(self):
        from hwp5.distdoc import decode_head_to_key
        payload = self.head()
        return decode_head_to_key(payload)

    def tail(self):
        item = self.wrapped.open()
        from .recordstream import read_record
        read_record(item, 0)
        assert 4 + 256 == item.tell()
        return item.read()

    def tail_decrypted(self):
        from hwp5.distdoc import decrypt_tail
        key = self.head_key()
        tail = self.tail()
        return decrypt_tail(key, tail)

    def tail_stream(self):
        return BytesIO(self.tail())


class Hwp5DistDocStorage(ItemConversionStorage):

    def resolve_conversion_for(self, name):
        def conversion(item):
            return Hwp5DistDocStream(self.wrapped[name], None)  # TODO: version
        return conversion


class Hwp5DistDoc(ItemConversionStorage):

    def resolve_conversion_for(self, name):
        if name in ('Scripts', 'ViewText'):
            return Hwp5DistDocStorage


class Hwp5Compression(ItemConversionStorage):
    ''' handle compressed streams in HWPv5 files '''

    def resolve_conversion_for(self, name):
        if name in ('BinData', 'BodyText', 'ViewText'):
            return CompressedStorage
        elif name == 'DocInfo':
            return CompressedStream
        elif name == 'Scripts':
            return CompressedStorage


class PreviewText(object):

    def __init__(self, item):
        self.open = item.open

    def other_formats(self):
        return {'.utf8': self.open_utf8}

    def open_utf8(self):
        transcode = transcoder('utf-16le', 'utf-8')
        return transcode(self.open())

    def get_utf8(self):
        f = self.open_utf8()
        try:
            return f.read()
        finally:
            f.close()

    utf8 = cached_property(get_utf8)

    def get_text(self):
        fp = self.open()
        try:
            data = fp.read()
        finally:
            fp.close()
        return data.decode('utf-16le')

    text = cached_property(get_text)

    def __str__(self):
        if PY3:
            return self.text
        return self.utf8

    def __unicode__(self):
        return self.text


class Sections(ItemConversionStorage):

    section_class = VersionSensitiveItem

    def __init__(self, stg, version):
        ItemConversionStorage.__init__(self, stg)
        self.version = version

    def resolve_conversion_for(self, name):
        def conversion(item):
            return self.section_class(self.wrapped[name], self.version)
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
            return read_type(FileHeader, dict(), f)
        finally:
            f.close()

    value = cached_property(to_dict)

    def get_version(self):
        return self.value['version']

    version = cached_property(get_version)

    def get_signature(self):
        return self.value['signature']

    signature = cached_property(get_signature)

    def get_flags(self):
        return FileHeader.Flags(self.value['flags'])

    flags = cached_property(get_flags)

    def open_text(self):
        signature = self.value['signature']
        signature = signature.decode('latin1')
        signature = signature[:len('HWP Document File')]

        d = FileHeader.Flags.dictvalue(self.value['flags'])
        d['signature'] = signature
        d['version'] = '%d.%d.%d.%d' % self.value['version']
        out = BytesIO()
        for k, v in sorted(d.items()):
            out.write('{}: {}\n'.format(k, v).encode('utf-8'))
        out.seek(0)
        return out

    def other_formats(self):
        return {'.txt': self.open_text}


class HwpSummaryInfo(VersionSensitiveItem):

    def other_formats(self):
        return {'.txt': self.open_text}

    def getPropertySetStream(self):
        from .msoleprops import PropertySetFormat
        from .msoleprops import PropertySetStreamReader
        from .summaryinfo import FMTID_HWP_SUMMARY_INFORMATION
        from .summaryinfo import HWP_PROPERTIES

        propertySetFormat = PropertySetFormat(
            FMTID_HWP_SUMMARY_INFORMATION,
            HWP_PROPERTIES
        )
        reader = PropertySetStreamReader([propertySetFormat])
        f = self.open()
        try:
            return reader.read(f)
        finally:
            f.close()

    propertySetStream = cached_property(getPropertySetStream)

    def getHwpSummaryInfoPropertySet(self):
        stream = self.propertySetStream
        if stream.clsid == CLSID_HWP_SUMMARY_INFORMATION:
            return stream.propertysets[0]

    propertySet = cached_property(getHwpSummaryInfoPropertySet)

    @property
    def title(self):
        from .msoleprops import PIDSI_TITLE
        return self.propertySet[PIDSI_TITLE]

    @property
    def subject(self):
        from .msoleprops import PIDSI_SUBJECT
        return self.propertySet[PIDSI_SUBJECT]

    @property
    def author(self):
        from .msoleprops import PIDSI_AUTHOR
        return self.propertySet[PIDSI_AUTHOR]

    @property
    def keywords(self):
        from .msoleprops import PIDSI_KEYWORDS
        return self.propertySet[PIDSI_KEYWORDS]

    @property
    def comments(self):
        from .msoleprops import PIDSI_COMMENTS
        return self.propertySet[PIDSI_COMMENTS]

    @property
    def lastSavedBy(self):
        from .msoleprops import PIDSI_LASTAUTHOR
        return self.propertySet[PIDSI_LASTAUTHOR]

    @property
    def revisionNumber(self):
        from .msoleprops import PIDSI_REVNUMBER
        return self.propertySet[PIDSI_REVNUMBER]

    @property
    def lastPrintedTime(self):
        from .msoleprops import PIDSI_LASTPRINTED
        return self.propertySet[PIDSI_LASTPRINTED]

    @property
    def createdTime(self):
        from .msoleprops import PIDSI_CREATE_DTM
        return self.propertySet[PIDSI_CREATE_DTM]

    @property
    def lastSavedTime(self):
        from .msoleprops import PIDSI_LASTSAVE_DTM
        return self.propertySet[PIDSI_LASTSAVE_DTM]

    @property
    def numberOfPages(self):
        from .msoleprops import PIDSI_PAGECOUNT
        return self.propertySet[PIDSI_PAGECOUNT]

    @property
    def dateString(self):
        from .summaryinfo import HWPPIDSI_DATE_STR
        return self.propertySet[HWPPIDSI_DATE_STR]

    @property
    def numberOfParagraphs(self):
        from .summaryinfo import HWPPIDSI_PARACOUNT
        return self.propertySet[HWPPIDSI_PARACOUNT]

    @property
    def plaintext_lines(self):
        from .msoleprops import PropertySetStreamTextFormatter
        stream = self.getPropertySetStream()
        formatter = PropertySetStreamTextFormatter()
        return formatter.formatTextLines(stream)

    def open_text(self):
        out = BytesIO()
        for line in self.plaintext_lines:
            line = line.encode('utf-8')
            out.write(line + b'\n')
        out.seek(0)
        return out


class Hwp5File(ItemConversionStorage):
    ''' represents HWPv5 File

        Hwp5File(stg)

        stg: an instance of Storage
    '''

    def __init__(self, stg):
        stg = Hwp5FileBase(stg)

        if stg.header.flags.password:
            stg = Hwp5PasswordProtectedDoc(stg)

            # TODO: 현재로선 decryption이 구현되지 않았으므로,
            # 레코드 파싱은 불가능하다. 적어도 encrypted stream에
            # 직접 접근은 가능하도록, 다음 레이어들은 bypass한다.
            ItemConversionStorage.__init__(self, stg)
            return

        if stg.header.flags.distributable:
            stg = Hwp5DistDoc(stg)

        if stg.header.flags.compressed:
            stg = Hwp5Compression(stg)

        ItemConversionStorage.__init__(self, stg)

    def resolve_conversion_for(self, name):
        if name == 'DocInfo':
            return self.with_version(self.docinfo_class)
        if name == 'BodyText':
            return self.with_version(self.bodytext_class)
        if name == 'ViewText':
            return self.with_version(self.bodytext_class)
        if name == 'PrvText':
            return PreviewText
        if name == '\005HwpSummaryInformation':
            return self.with_version(self.summaryinfo_class)

    def with_version(self, f):
        def wrapped(item):
            return f(item, self.header.version)
        return wrapped

    summaryinfo_class = HwpSummaryInfo
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

    @property
    def text(self):
        if self.header.flags.distributable:
            return self.viewtext
        else:
            return self.bodytext
