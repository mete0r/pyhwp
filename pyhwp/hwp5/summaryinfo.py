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
from uuid import UUID

from .msoleprops import PropertyIdentifier
from .msoleprops import RESERVED_PROPERTIES
from .msoleprops import SUMMARY_INFORMATION_PROPERTIES


CLSID_HWP_SUMMARY_INFORMATION = UUID(
    '9fa2b660-1061-11d4-b4c6-006097c09d8c'
)

FMTID_HWP_SUMMARY_INFORMATION = CLSID_HWP_SUMMARY_INFORMATION

HWPPIDSI_DATE_STR = PropertyIdentifier(
    id=0x00000014,
    label='HWPPIDSI_DATE_STR',
)

HWPPIDSI_PARACOUNT = PropertyIdentifier(
    id=0x00000015,
    label='HWPPIDSI_PARACOUNT',
)

HWP_PROPERTIES = RESERVED_PROPERTIES + SUMMARY_INFORMATION_PROPERTIES + (
    HWPPIDSI_DATE_STR,
    HWPPIDSI_PARACOUNT,
)


class HwpSummaryInfoTextFormatter(object):

    def formatTextLines(self, hwpsummaryinfo):
        yield 'Title: {}'.format(hwpsummaryinfo.title)
        yield 'Subject: {}'.format(hwpsummaryinfo.subject)
        yield 'Author: {}'.format(hwpsummaryinfo.author)
        yield 'Keywords: {}'.format(hwpsummaryinfo.keywords)
        yield 'Comments: {}'.format(hwpsummaryinfo.comments)
        yield 'Last saved by: {}'.format(hwpsummaryinfo.lastSavedBy)
        yield 'Revision Number: {}'.format(hwpsummaryinfo.revisionNumber)
        yield 'Last Printed at: {}'.format(hwpsummaryinfo.lastPrintedTime)
        yield 'Created at: {}'.format(hwpsummaryinfo.createdTime)
        yield 'Last saved at: {}'.format(hwpsummaryinfo.lastSavedTime)
        yield 'Number of pages: {}'.format(hwpsummaryinfo.numberOfPages)
        yield 'Date: {}'.format(hwpsummaryinfo.dateString)
        yield 'Number of paragraphs: {}'.format(
            hwpsummaryinfo.numberOfParagraphs
        )
