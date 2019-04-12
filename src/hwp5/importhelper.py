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
import os.path


def pkg_resources_filename(pkg_name, path):
    ''' the equivalent of pkg_resources.resource_filename() '''
    try:
        import pkg_resources
    except ImportError:
        return pkg_resources_filename_fallback(pkg_name, path)
    else:
        return pkg_resources.resource_filename(pkg_name, path)


def pkg_resources_filename_fallback(pkg_name, path):
    ''' a fallback implementation of pkg_resources_filename() '''
    pkg_module = __import__(pkg_name)
    pkg_name = pkg_name.split('.')
    for x in pkg_name[1:]:
        pkg_module = getattr(pkg_module, x)
    pkg_dir = os.path.dirname(pkg_module.__file__)
    return os.path.join(pkg_dir, path)
