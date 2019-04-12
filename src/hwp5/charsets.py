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


def get_unichr_lang(uch):
    # Hangul Syllables
    # U+AC00..U+D7AF
    # Hangul Jamo Extended-B
    # U+D7B0..D7FF
    if u'\uAC00' <= uch <= u'\uD7FF':
        return 'ko'

    # Control Characters and Numbers in Basic Latin
    if u'\u0000' <= uch <= u'\u0040':
        return None

    # Hangul Jamo
    if u'\u1100' <= uch <= u'\u11FF':
        return 'ko'

    # Hangul Compatibility Jamo
    if u'\u3130' <= uch <= u'\u318F':
        return 'ko'

    # Hangul Jamo Extended-A
    if u'\uA960' <= uch <= u'\uA97F':
        return 'ko'

    # -- en --

    # Basic Latin, Latin Extended-A/B
    if u'\u0040' <= uch <= u'\u024F':
        return 'en'

    # -- cn --

    # CJK Unified Ideographs
    # U+4E00..U+9FFF
    if u'\u4E00' <= uch <= u'\u9FFF':
        return 'cn'

    # CJK Radicals Supplement
    # U+2E80..U+2EFF
    # Kangxi Radicals
    # U+2F00..U+2FDF
    if u'\u2E80' <= uch <= u'\u2FDF':
        return 'cn'

    # CJK Unified Ideographs Extension A
    # U+3400..U+4DBF
    if u'\u3400' <= uch <= u'\u4DBF':
        return 'cn'

    # CJK Compatibility Ideographs
    # U+F900..U+FAFF
    if u'\uF900' <= uch <= u'\uFAFF':
        return 'cn'

    # CJK Symbols and Punctuation
    # U+3000..U+303F
    if u'\u3000' <= uch <= u'\u303F':
        return 'symbol'

    # -- jp --

    # Hiragana + Katakana
    if u'\u3040' <= uch <= u'\u30FF':
        return 'jp'

    return 'other'


def tokenize_unicode_by_lang(text):
    buf = []
    buf_lang = None
    for uch in text:
        lang = get_unichr_lang(uch)
        if lang is None:
            buf.append(uch)
            continue
        if buf_lang == lang or buf_lang is None:
            buf_lang = lang
            buf.append(uch)
            continue
        else:
            yield buf_lang or 'ko', ''.join(buf)
            buf = [uch]
            buf_lang = lang
    if buf:
        yield buf_lang or 'ko', ''.join(buf)
