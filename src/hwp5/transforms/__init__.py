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

from ..utils import hwp5_resources_path
from ..utils import mkstemp_open
from ..xmlmodel import XmlEventGenerator


logger = logging.getLogger(__name__)


class BaseTransform:

    def __init__(self, xsltfactory, embedbin=False):
        self.xsltfactory = xsltfactory
        self.embedbin = embedbin

    def make_transform_hwp5(self, transform_xhwp5):
        def transform_hwp5(hwp5file, output):
            with self.transformed_xhwp5_at_temp(hwp5file) as xhwp5path:
                return transform_xhwp5(xhwp5path, output)
        return transform_hwp5

    def make_xsl_transform(self, resource_path, **params):
        with hwp5_resources_path(resource_path) as xsl_path:
            xslt = self.xsltfactory.xslt_from_file(xsl_path, **params)
            return xslt.transform_into_stream

    @contextmanager
    def transformed_xhwp5_at_temp(self, hwp5file):
        with mkstemp_open() as (tmp_path, f):
            xmlevent_gen = XmlEventGenerator(hwp5file)
            xmlevent_gen.xmlevents(embedbin=self.embedbin).dump(f)
            yield tmp_path
