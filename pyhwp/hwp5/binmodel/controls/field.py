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
from hwp5.binmodel.controlchar import CHID
from hwp5.dataio import Flags
from hwp5.dataio import UINT32
from hwp5.dataio import BSTR
from hwp5.dataio import BYTE
from hwp5.binmodel.tagid71_ctrl_data import ControlData
from hwp5.binmodel.controls._shared import Control


class Field(Control):
    ''' 4.2.10.15 필드 시작 '''

    Flags = Flags(UINT32,
                  0, 'editableInReadOnly',
                  11, 14, 'visitedType',
                  15, 'modified')

    def attributes(cls):
        yield cls.Flags, 'flags',
        yield BYTE, 'extra_attr',
        yield BSTR, 'command',
        yield UINT32, 'id',
    attributes = classmethod(attributes)


class FieldUnknown(Field):
    chid = '%unk'


class FieldDate(Field):
    chid = CHID.DTE


class FieldDocDate(Field):
    chid = '%ddt'


class FieldPath(Field):
    chid = '%pat'


class FieldBookmark(Field):
    chid = '%bmk'


class FieldMailMerge(Field):
    chid = '%mmg'


class FieldCrossRef(Field):
    chid = '%xrf'


class FieldFormula(Field):
    chid = '%fmu'


class FieldClickHere(Field):
    chid = '%clk'


class FieldClickHereData(ControlData):
    parent_model_type = FieldClickHere


class FieldSummary(Field):
    chid = '%smr'


class FieldUserInfo(Field):
    chid = '%usr'


class FieldHyperLink(Field):
    chid = CHID.HLK

    def geturl(self):
        s = self.command.split(';')
        return s[0].replace('\\:', ':')


# TODO: FieldRevisionXXX


class FieldMemo(Field):
    chid = '%%me'


class FieldPrivateInfoSecurity(Field):
    chid = '%cpr'
