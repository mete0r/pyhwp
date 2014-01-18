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
''' Extract out the specified stream in the <hwp5file> to the standard output.

Usage::

    hwp5proc cat [--loglevel=<loglevel>] [--logfile=<logfile>]
                 [--vstreams | --ole]
                 <hwp5file> <stream>
    hwp5proc cat --help

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

    $ hwp5proc cat samples/sample-5017.hwp BinData/BIN0002.jpg | file -

    $ hwp5proc cat samples/sample-5017.hwp BinData/BIN0002.jpg > BIN0002.jpg

    $ hwp5proc cat samples/sample-5017.hwp PrvText | iconv -f utf-16le -t utf-8

    $ hwp5proc cat --vstreams samples/sample-5017.hwp PrvText.utf8

    $ hwp5proc cat --vstreams samples/sample-5017.hwp FileHeader.txt

    ccl: 0
    cert_drm: 0
    cert_encrypted: 0
    cert_signature_extra: 0
    cert_signed: 0
    compressed: 1
    distributable: 0
    drm: 0
    history: 0
    password: 0
    script: 0
    signature: HWP Document File
    version: 5.0.1.7
    xmltemplate_storage: 0

'''
from hwp5.proc import entrypoint


@entrypoint(__doc__)
def main(args):
    from hwp5.proc import open_hwpfile
    from hwp5.storage import open_storage_item
    import sys
    hwp5file = open_hwpfile(args)
    stream = open_storage_item(hwp5file, args['<stream>'])
    f = stream.open()
    try:
        while True:
            data = f.read(4096)
            if data:
                sys.stdout.write(data)
            else:
                return
    finally:
        if hasattr(f, 'close'):
            f.close()
