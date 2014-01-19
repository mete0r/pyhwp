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
''' Extract out streams in the specified <hwp5file> to a directory.

Usage::

    hwp5proc unpack [--loglevel=<loglevel>] [--logfile=<logfile>]
                    [--vstreams | --ole]
                    <hwp5file> [<out-directory>]
    hwp5proc unpack --help

Options::

    -h --help               Show this screen
       --loglevel=<level>   Set log level.
       --logfile=<file>     Set log file.

       --vstreams           Process with virtual streams (i.e. parsed/converted
                            form of real streams)
       --ole                Treat <hwpfile> as an OLE Compound File. As a
                            result, some streams will be presented as-is. (i.e.
                            not decompressed)

Example::

    $ hwp5proc unpack samples/sample-5017.hwp
    $ ls sample-5017

Example::

    $ hwp5proc unpack --vstreams samples/sample-5017.hwp
    $ cat sample-5017/PrvText.utf8

'''
from hwp5.proc import entrypoint


@entrypoint(__doc__)
def main(args):
    from hwp5 import storage
    from hwp5.proc import open_hwpfile
    import os.path

    filename = args['<hwp5file>']
    hwp5file = open_hwpfile(args)

    outdir = args['<out-directory>']
    if outdir is None:
        outdir, ext = os.path.splitext(os.path.basename(filename))
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    storage.unpack(hwp5file, outdir)
