# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2014 mete0r <mete0r@sarangbang.or.kr>
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
''' Decode distribute docs.

Based on the algorithm described by Changwoo Ryu
See https://groups.google.com/forum/#!topic/hwp-foss/d2KL2ypR89Q
'''
import logging


logger = logging.getLogger(__name__)


class Random:
    ''' MSVC's srand()/rand() like pseudorandom generator.
    '''

    def __init__(self, seed):
        self.seed = seed

    def rand(self):
        self.seed = (self.seed * 214013 + 2531011) & 0xffffffff
        value = (self.seed >> 16) & 0x7fff
        return value


def decode_head_to_sha1(record_payload):
    ''' Decode HWPTAG_DISTRIBUTE_DOC_DATA.

    It's the sha1 digest of user-supplied password string, i.e.,

        '12345' -> hashlib.sha1('12345').digest()

    '''
    if len(record_payload) != 256:
        raise ValueError('payload size must be 256 bytes')

    data = list(ord(x) for x in record_payload)
    seed = data[3] << 24 | data[2] << 16 | data[1] << 8 | data[0]
    random = Random(seed)

    n = 0
    for i in range(256):
        if n == 0:
            key = random.rand() & 0xff
            n = (random.rand() & 0xf) + 1
        if i >= 4:
            data[i] = data[i] ^ key
        n -= 1

    decoded = ''.join(chr(x) for x in data)
    sha1offset = 4 + (data[0] & 0xf)

    ucs16le = decoded[sha1offset:sha1offset + 80]
    return ucs16le
