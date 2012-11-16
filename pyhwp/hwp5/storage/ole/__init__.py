# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010 mete0r@sarangbang.or.kr
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

import logging


logger = logging.getLogger(__name__)


def get_implementation():
    from hwp5.plat import jython_poifs
    if jython_poifs.is_enabled():
        logger.info('OleStorage implementation: jython_poifs')
        return jython_poifs.OleStorage

    from hwp5.plat import _uno
    if _uno.is_enabled():
        logger.info('OleStorage implementation: _uno')
        return _uno.OleStorage

    from hwp5.plat import olefileio
    if olefileio.is_enabled():
        logger.info('OleStorage implementation: olefileio')
        return olefileio.OleStorage


class OleStorage(object):

    def __init__(self, *args, **kwargs):
        impl_class = get_implementation()
        self.impl = impl_class(*args, **kwargs)

    def __iter__(self):
        return self.impl.__iter__()

    def __getitem__(self, name):
        return self.impl.__getitem__(name)

    def __getattr__(self, name):
        return getattr(self.impl, name)
