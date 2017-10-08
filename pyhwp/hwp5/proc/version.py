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
'''Print HWP file format version of <hwp5file>.

Usage::

    hwp5proc version [options] <hwp5file>
    hwp5proc version --help

Options::

    -h --help              Show this screen
       --loglevel=<level>  Set log level.
       --logfile=<file>    Set log file.

'''
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from ..filestructure import Hwp5File


def main(args):
    hwp5file = Hwp5File(args['<hwp5file>'])
    h = hwp5file.fileheader
    print('%d.%d.%d.%d' % h.version)
