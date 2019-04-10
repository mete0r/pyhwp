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
import logging
import os

from .storage import ExtraItemStorage
from .storage.ole import OleStorage
from .xmlmodel import Hwp5File


def init_logger(args):
    logger = logging.getLogger('hwp5')
    try:
        from colorlog import ColoredFormatter
    except ImportError:
        formatter = None
    else:
        formatter = ColoredFormatter(
            '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
            datefmt=None, reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red'
            }
        )

    loglevel = args.loglevel
    if not loglevel:
        loglevel = os.environ.get('PYHWP_LOGLEVEL')
    if loglevel:
        levels = dict(debug=logging.DEBUG,
                      info=logging.INFO,
                      warning=logging.WARNING,
                      error=logging.ERROR,
                      critical=logging.CRITICAL)
        loglevel = loglevel.lower()
        loglevel = levels.get(loglevel, logging.WARNING)
        logger.setLevel(loglevel)

    logfile = args.logfile
    if not logfile:
        logfile = os.environ.get('PYHWP_LOGFILE')
    if logfile:
        handler = logging.FileHandler(logfile)
    else:
        handler = logging.StreamHandler()
    if formatter:
        handler.setFormatter(formatter)
    logger.addHandler(handler)


def open_hwpfile(args):
    filename = args.hwp5file
    if args.ole:
        hwpfile = OleStorage(filename)
    else:
        hwpfile = Hwp5File(filename)
        if args.vstreams:
            hwpfile = ExtraItemStorage(hwpfile)
    return hwpfile
