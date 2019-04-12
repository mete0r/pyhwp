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
    chid = CHID.FIELD_UNK


class FieldDate(Field):
    chid = CHID.FIELD_DTE


class FieldDocDate(Field):
    chid = CHID.FIELD_DDT


class FieldPath(Field):
    chid = CHID.FIELD_PAT


class FieldBookmark(Field):
    chid = CHID.FIELD_BMK


class FieldMailMerge(Field):
    chid = CHID.FIELD_MMG


class FieldCrossRef(Field):
    chid = CHID.FIELD_XRF


class FieldFormula(Field):
    chid = CHID.FIELD_FMU


class FieldClickHere(Field):
    chid = CHID.FIELD_CLK


class FieldClickHereData(ControlData):
    parent_model_type = FieldClickHere


class FieldSummary(Field):
    chid = CHID.FIELD_SMR


class FieldUserInfo(Field):
    chid = CHID.FIELD_USR


class FieldHyperLink(Field):
    chid = CHID.FIELD_HLK

    def geturl(self):
        s = self.command.split(';')
        return s[0].replace('\\:', ':')


class FieldRevisionSign(Field):
    chid = CHID.FIELD_REVISION_SIGN


class FieldRevisionDelete(Field):
    chid = CHID.FIELD_REVISION_DELETE


class FieldRevisionAttach(Field):
    chid = CHID.FIELD_REVISION_ATTACH


class FieldRevisionClipping(Field):
    chid = CHID.FIELD_REVISION_CLIPPING


class FieldRevisionSawtooth(Field):
    chid = CHID.FIELD_REVISION_SAWTOOTH


class FieldRevisionThinking(Field):
    chid = CHID.FIELD_REVISION_THINKING


class FieldRevisionPraise(Field):
    chid = CHID.FIELD_REVISION_PRAISE


class FieldRevisionLine(Field):
    chid = CHID.FIELD_REVISION_LINE


class FieldRevisionSimpleChange(Field):
    chid = CHID.FIELD_REVISION_SIMPLECHANGE


class FieldRevisionHyperlink(Field):
    chid = CHID.FIELD_REVISION_HYPERLINK


class FieldRevisionLineAttach(Field):
    chid = CHID.FIELD_REVISION_LINEATTACH


class FieldRevisionLineLink(Field):
    chid = CHID.FIELD_REVISION_LINELINK


class FieldRevisionLineTransfer(Field):
    chid = CHID.FIELD_REVISION_LINETRANSFER


class FieldRevisionRightMove(Field):
    chid = CHID.FIELD_REVISION_RIGHTMOVE


class FieldRevisionLeftMove(Field):
    chid = CHID.FIELD_REVISION_LEFTMOVE


class FieldRevisionTransfer(Field):
    chid = CHID.FIELD_REVISION_TRANSFER


class FieldRevisionSimpleInsert(Field):
    chid = CHID.FIELD_REVISION_SIMPLEINSERT


class FieldRevisionSplit(Field):
    chid = CHID.FIELD_REVISION_SPLIT


class FieldRevisionChange(Field):
    chid = CHID.FIELD_REVISION_CHANGE


class FieldMemo(Field):
    chid = CHID.FIELD_MEMO


class FieldPrivateInfoSecurity(Field):
    chid = CHID.FIELD_PRIVATE_INFO_SECURITY
