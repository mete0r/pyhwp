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
import re
import sys

from six import with_metaclass

from hwp5.dataio import PrimitiveType
from hwp5.dataio import UINT32
from hwp5.dataio import UINT16
from hwp5.dataio import UINT8


PY3 = sys.version_info.major == 3
if PY3:
    unichr = chr


class CHID(with_metaclass(PrimitiveType, str)):

    fixed_size = 4

    # Common controls
    GSO = 'gso '
    TBL = 'tbl '
    LINE = '$lin'
    RECT = '$rec'
    ELLI = '$ell'
    ARC = '$arc'
    POLY = '$pol'
    CURV = '$cur'
    EQED = 'eqed'
    PICT = '$pic'
    OLE = '$ole'
    CONTAINER = '$con'

    # Controls
    SECD = 'secd'
    COLD = 'cold'
    HEADER = 'head'
    FOOTER = 'foot'
    FN = 'fn  '
    EN = 'en  '
    ATNO = 'atno'
    NWNO = 'nwno'
    PGHD = 'pghd'
    PGCT = 'pgct'
    PGNP = 'pgnp'
    IDXM = 'idxm'
    BOKM = 'bokm'
    TCPS = 'tcps'
    TDUT = 'tdut'
    TCMT = 'tcmt'

    # Field starts
    FIELD_UNK = '%unk'
    FIELD_DTE = '%dte'
    FIELD_DDT = '%ddt'
    FIELD_PAT = '%pat'
    FIELD_BMK = '%bmk'
    FIELD_MMG = '%mmg'
    FIELD_XRF = '%xrf'
    FIELD_FMU = '%fmu'
    FIELD_CLK = '%clk'
    FIELD_SMR = '%smr'
    FIELD_USR = '%usr'
    FIELD_HLK = '%hlk'
    FIELD_REVISION_SIGN = '%sig'
    FIELD_REVISION_DELETE = '%%*d'
    FIELD_REVISION_ATTACH = '%%*a'
    FIELD_REVISION_CLIPPING = '%%*C'
    FIELD_REVISION_SAWTOOTH = '%%*S'
    FIELD_REVISION_THINKING = '%%*T'
    FIELD_REVISION_PRAISE = '%%*P'
    FIELD_REVISION_LINE = '%%*L'
    FIELD_REVISION_SIMPLECHANGE = '%%*c'
    FIELD_REVISION_HYPERLINK = '%%*h'
    FIELD_REVISION_LINEATTACH = '%%*A'
    FIELD_REVISION_LINELINK = '%%*i'
    FIELD_REVISION_LINETRANSFER = '%%*t'
    FIELD_REVISION_RIGHTMOVE = '%%*r'
    FIELD_REVISION_LEFTMOVE = '%%*l'
    FIELD_REVISION_TRANSFER = '%%*n'
    FIELD_REVISION_SIMPLEINSERT = '%%*e'
    FIELD_REVISION_SPLIT = '%spl'
    FIELD_REVISION_CHANGE = '%%mr'
    FIELD_MEMO = '%%me'
    FIELD_PRIVATE_INFO_SECURITY = '%cpr'

    def decode(bytes, context=None):
        if PY3:
            return (
                chr(bytes[3]) +
                chr(bytes[2]) +
                chr(bytes[1]) +
                chr(bytes[0])
            )
        else:
            return bytes[3] + bytes[2] + bytes[1] + bytes[0]
    decode = staticmethod(decode)


class ControlChar(object):
    class CHAR(object):
        size = 1

    class INLINE(object):
        size = 8

    class EXTENDED(object):
        size = 8
    chars = {0x00: ('NULL', CHAR),
             0x01: ('CTLCHR01', EXTENDED),
             0x02: ('SECTION_COLUMN_DEF', EXTENDED),
             0x03: ('FIELD_START', EXTENDED),
             0x04: ('FIELD_END', INLINE),
             0x05: ('CTLCHR05', INLINE),
             0x06: ('CTLCHR06', INLINE),
             0x07: ('CTLCHR07', INLINE),
             0x08: ('TITLE_MARK', INLINE),
             0x09: ('TAB', INLINE),
             0x0a: ('LINE_BREAK', CHAR),
             0x0b: ('DRAWING_TABLE_OBJECT', EXTENDED),
             0x0c: ('CTLCHR0C', EXTENDED),
             0x0d: ('PARAGRAPH_BREAK', CHAR),
             0x0e: ('CTLCHR0E', EXTENDED),
             0x0f: ('HIDDEN_EXPLANATION', EXTENDED),
             0x10: ('HEADER_FOOTER', EXTENDED),
             0x11: ('FOOT_END_NOTE', EXTENDED),
             0x12: ('AUTO_NUMBER', EXTENDED),
             0x13: ('CTLCHR13', INLINE),
             0x14: ('CTLCHR14', INLINE),
             0x15: ('PAGE_CTLCHR', EXTENDED),
             0x16: ('BOOKMARK', EXTENDED),
             0x17: ('CTLCHR17', EXTENDED),
             0x18: ('HYPHEN', CHAR),
             0x1e: ('NONBREAK_SPACE', CHAR),
             0x1f: ('FIXWIDTH_SPACE', CHAR)}
    names = dict((unichr(code), name) for code, (name, kind) in chars.items())
    kinds = dict((unichr(code), kind) for code, (name, kind) in chars.items())

    def _populate(cls):
        for ch, name in cls.names.items():
            setattr(cls, name, ch)
    _populate = classmethod(_populate)
    REGEX_CONTROL_CHAR = re.compile(b'[\x00-\x1f]\x00')

    def find(cls, data, start_idx):
        while True:
            m = cls.REGEX_CONTROL_CHAR.search(data, start_idx)
            if m is not None:
                i = m.start()
                if i & 1 == 1:
                    start_idx = i + 1
                    continue
                if PY3:
                    char = unichr(data[i])
                else:
                    char = unichr(ord(data[i]))
                size = cls.kinds[char].size
                return i, i + (size * 2)
            data_len = len(data)
            return data_len, data_len
    find = classmethod(find)

    def decode(cls, bytes):
        code = UINT16.decode(bytes[0:2])
        ch = unichr(code)
        if cls.kinds[ch].size == 8:
            bytes = bytes[2:2 + 12]
            if ch == ControlChar.TAB:
                param = dict(width=UINT32.decode(bytes[0:4]),
                             unknown0=UINT8.decode(bytes[4:5]),
                             unknown1=UINT8.decode(bytes[5:6]),
                             unknown2=bytes[6:])
                return dict(code=code, param=param)
            else:
                chid = CHID.decode(bytes[0:4])
                param = bytes[4:12]
                return dict(code=code, chid=chid, param=param)
        else:
            return dict(code=code)
    decode = classmethod(decode)

    def get_kind_by_code(cls, code):
        ch = unichr(code)
        return cls.kinds[ch]
    get_kind_by_code = classmethod(get_kind_by_code)

    def get_name_by_code(cls, code):
        ch = unichr(code)
        return cls.names.get(ch, 'CTLCHR%02x' % code)
    get_name_by_code = classmethod(get_name_by_code)


ControlChar._populate()
