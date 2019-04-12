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
from contextlib import contextmanager
import logging

from ..errors import ImplementationNotAvailable
from ..plat import get_xslt_compile
from ..utils import hwp5_resources_path
from ..utils import mkstemp_open


logger = logging.getLogger(__name__)


class BaseTransform:

    def __init__(self, xslt_compile=None, embedbin=False):
        self.xslt_compile = xslt_compile or self.get_default_xslt_compile()
        self.embedbin = embedbin

    @classmethod
    def get_default_xslt_compile(cls):
        xslt_compile = get_xslt_compile()
        if not xslt_compile:
            raise ImplementationNotAvailable('xslt')
        return xslt_compile

    def make_transform_hwp5(self, transform_xhwp5):
        def transform_hwp5(hwp5file, output):
            with self.transformed_xhwp5_at_temp(hwp5file) as xhwp5path:
                return transform_xhwp5(xhwp5path, output)
        return transform_hwp5

    def make_xsl_transform(self, resource_path, **params):
        with hwp5_resources_path(resource_path) as xsl_path:
            return self.xslt_compile(xsl_path, **params)

    @contextmanager
    def transformed_xhwp5_at_temp(self, hwp5file):
        with mkstemp_open() as (tmp_path, f):
            hwp5file.xmlevents(embedbin=self.embedbin).dump(f)
            yield tmp_path
