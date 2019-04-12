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

from hwp5.binmodel._shared import RecordModel
from hwp5.tagids import HWPTAG_FACE_NAME
from hwp5.dataio import Flags
from hwp5.dataio import Enum
from hwp5.dataio import BSTR
from hwp5.dataio import BYTE
from hwp5.dataio import Struct


class AlternateFont(Struct):
    def attributes():
        yield BYTE, 'kind'
        yield BSTR, 'name'
    attributes = staticmethod(attributes)


class Panose1(Struct):
    ''' 표 17 글꼴 유형 정보 '''

    FamilyType = Enum('any', 'no_fit', 'text_display', 'script', 'decorative',
                      'pictorial')

    SerifStyle = Enum('any', 'no_fit', 'cove', 'obtuse_cove', 'square_cove',
                      'obtuse_square_cove', 'square', 'thin', 'bone',
                      'exaggerated', 'triangle', 'normal_sans', 'obtuse_sans',
                      'perp_sans', 'flared', 'rounded')

    Weight = Enum('any', 'no_fit', 'very_light', 'light', 'thin', 'book',
                  'medium', 'demi', 'bold', 'heavy', 'black', 'nord')

    Proportion = Enum('any', 'no_fit', 'old_style', 'modern', 'even_width',
                      'expanded', 'condensed', 'very_expanded',
                      'very_condensed', 'monospaced')

    Contrast = Enum('any', 'no_fit', 'none', 'very_low', 'low', 'medium_low',
                    'medium', 'medium_high', 'high', 'very_high')

    StrokeVariation = Enum('any', 'no_fit', 'gradual_diag', 'gradual_tran',
                           'gradual_vert', 'gradual_horz', 'rapid_vert',
                           'rapid_horz', 'instant_vert')

    ArmStyle = Enum('any', 'no_fit', 'straight_horz', 'straight_wedge',
                    'straight_vert', 'straight_single_serif',
                    'straight_double_serif', 'bent_horz', 'bent_wedge',
                    'bent_vert', 'bent_single_serif', 'bent_double_serif')

    Letterform = Enum('any', 'no_fit', 'normal_contact', 'normal_weighted',
                      'normal_boxed', 'normal_flattened', 'normal_rounded',
                      'normal_off_center', 'normal_square', 'oblique_contact',
                      'oblique_weighted', 'oblique_boxed', 'oblique_flattened',
                      'oblique_rounded', 'oblique_off_center',
                      'oblique_square')

    Midline = Enum('any', 'no_fit', 'standard_trimmed', 'standard_pointed',
                   'standard_serifed', 'high_trimmed', 'high_pointed',
                   'high_serifed', 'constant_trimmed', 'constant_pointed',
                   'constant_serifed', 'low_trimmed', 'low_pointed',
                   'low_serifed')

    XHeight = Enum('any', 'no_fit', 'constant_small', 'constant_std',
                   'constant_large', 'ducking_small', 'ducking_std',
                   'ducking_large')

    def attributes():
        yield BYTE, 'family_type',
        yield BYTE, 'serif_style',
        yield BYTE, 'weight',
        yield BYTE, 'proportion',
        yield BYTE, 'contrast',
        yield BYTE, 'stroke_variation',
        yield BYTE, 'arm_style',
        yield BYTE, 'letterform',
        yield BYTE, 'midline',
        yield BYTE, 'x_height',
    attributes = staticmethod(attributes)


class FaceName(RecordModel):
    ''' 4.1.4. 글꼴 '''

    tagid = HWPTAG_FACE_NAME

    # 표 16 대체 글꼴 유형
    FontFileType = Enum(UNKNOWN=0, TTF=1, HFT=2)

    # 표 15 글꼴 속성
    Flags = Flags(BYTE,
                  0, 1, FontFileType, 'font_file_type',
                  5, 'default',
                  6, 'metric',
                  7, 'alternate')

    def attributes(cls):
        ''' 표 14 글꼴 '''
        yield cls.Flags, 'flags'
        yield BSTR, 'name'

        def has_alternate(context, values):
            ''' flags.alternate == 1 '''
            return values['flags'].alternate

        def has_metric(context, values):
            ''' flags.metric == 1 '''
            return values['flags'].metric

        def has_default(context, values):
            ''' flags.default == 1 '''
            return values['flags'].default

        yield dict(type=AlternateFont, name='alternate_font',
                   condition=has_alternate)
        yield dict(type=Panose1, name='panose1', condition=has_metric)
        yield dict(type=BSTR, name='default_font', condition=has_default)
    attributes = classmethod(attributes)
