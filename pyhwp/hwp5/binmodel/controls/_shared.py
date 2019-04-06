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

from six import with_metaclass

from hwp5.binmodel._shared import RecordModelType
from hwp5.binmodel._shared import RecordModel
from hwp5.tagids import HWPTAG_CTRL_HEADER
from hwp5.binmodel.controlchar import CHID


control_models = dict()


class ControlType(RecordModelType):

    def __new__(mcs, name, bases, attrs):
        cls = RecordModelType.__new__(mcs, name, bases, attrs)
        if 'chid' in attrs:
            chid = attrs['chid']
            assert chid not in control_models
            control_models[chid] = cls
        return cls


class Control(with_metaclass(ControlType, RecordModel)):
    ''' 4.2.6. 컨트롤 헤더 '''

    tagid = HWPTAG_CTRL_HEADER

    def attributes():
        yield CHID, 'chid'
    attributes = staticmethod(attributes)

    extension_types = control_models

    def get_extension_key(cls, context, model):
        ''' chid '''
        return model['content']['chid']
    get_extension_key = classmethod(get_extension_key)
