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
''' Print HWP file header.

Usage::

    hwp5proc header [options] <hwp5file>
    hwp5proc header -h

Options::

    -h --help              Show this screen
       --loglevel=<level>  Set log level.
       --logfile=<file>    Set log file.

'''
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import shutil
import sys


PY2 = sys.version_info.major == 2


def main(args):
    if PY2:
        output_fp = sys.stdout
    else:
        output_fp = sys.stdout.buffer

    from hwp5.filestructure import Hwp5File
    hwp5file = Hwp5File(args['<hwp5file>'])
    f = hwp5file.header.open_text()
    try:
        shutil.copyfileobj(f, output_fp)
    finally:
        hwp5file.close()
