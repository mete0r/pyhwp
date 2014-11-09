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
''' Transform an HWPv5 file into an XML.

.. note::

   This command is experimental. Its output format is subject to change at any
   time.

Usage::

    hwp5proc xml [--embedbin]
                 [--no-xml-decl]
                 [--output=<file>]
                 [--format=<format>]
                 [--loglevel=<loglevel>] [--logfile=<logfile>]
                 <hwp5file>
    hwp5proc xml --help

Options::

    -h --help               Show this screen
       --loglevel=<level>   Set log level.
       --logfile=<file>     Set log file.

       --embedbin           Embed BinData/* streams in the output XML.
       --no-xml-decl        Don't output <?xml ... ?> XML declaration.
       --output=<file>      Output filename.

    <hwp5file>              HWPv5 files (*.hwp)
    <format>                "flat", "nested" (default: "nested")

Example::

    $ hwp5proc xml samples/sample-5017.hwp > sample-5017.xml
    $ xmllint --format sample-5017.xml

With ``--embedbin`` option, you can embed base64-encoded ``BinData/*`` files in
the output XML.

Example::

    $ hwp5proc xml --embedbin samples/sample-5017.hwp > sample-5017.xml
    $ xmllint --format sample-5017.xml

'''
from __future__ import with_statement
from contextlib import contextmanager
from functools import partial
import logging
import subprocess

from hwp5.proc import entrypoint
from hwp5.xmldump_flat import xmldump_flat


logger = logging.getLogger(__name__)


def xmldump_nested(hwp5file, output, embedbin=False, xml_declaration=True):
    dump = hwp5file.xmlevents(embedbin=embedbin).dump
    dump = partial(dump, xml_declaration=xml_declaration)
    dump(output)


@entrypoint(__doc__)
def main(args):
    ''' Transform <hwp5file> into an XML.
    '''
    import sys
    from hwp5.xmlmodel import Hwp5File

    fmt = args['--format'] or 'nested'
    if fmt == 'flat':
        xmldump = partial(xmldump_flat, xml_declaration=args['--no-xml-decl'])
    elif fmt == 'nested':
        xmldump = partial(xmldump_nested, embedbin=args['--embedbin'],
                          xml_declaration=args['--no-xml-decl'])

    if args['--output']:
        output = open(args['--output'], 'w')
    else:
        output = sys.stdout

    hwp5file = Hwp5File(args['<hwp5file>'])
    with output:

        isatty = output.isatty()

        output_wrappers = [
            xmllint(encode='utf-8', format=isatty),
            xmllint(c14n=True),
        ]

        if isatty:
            output_wrappers = [
                pager(),
                syntaxhighlight('application/xml'),
            ] + output_wrappers

        with cascade_contextmanager_filters(output, output_wrappers) as output:
            xmldump(hwp5file, output)


@contextmanager
def cascade_contextmanager_filters(arg, filters):
    if len(filters) == 0:
        yield arg
    else:
        flt, filters = filters[0], filters[1:]
        with flt(arg) as ret:
            with cascade_contextmanager_filters(ret, filters) as ret:
                yield ret


@contextmanager
def null_contextmanager_filter(output):
    yield output


def output_thru_subprocess(cmd):
    @contextmanager
    def filter(output):
        logger.debug('%r', cmd)
        try:
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=output)
        except Exception, e:
            logger.error('%r: %s', ' '.join(cmd), e)
            yield output
        else:
            try:
                yield p.stdin
            except IOError, e:
                import errno
                if e.errno != errno.EPIPE:
                    raise
            finally:
                p.stdin.close()
                p.wait()
                retcode = p.returncode
                logger.debug('%r exit %d', cmd, retcode)
    return filter


def xmllint(c14n=False, encode=None, format=False):
    cmd = ['xmllint']
    if c14n:
        cmd.append('--c14n')
    if encode:
        cmd += ['--encode', encode]
    if format:
        cmd.append('--format')
    cmd.append('-')
    return output_thru_subprocess(cmd)


def syntaxhighlight(mimetype):
    try:
        return syntaxhighlight_pygments(mimetype)
    except Exception, e:
        logger.info(e)
        return null_contextmanager_filter


def syntaxhighlight_pygments(mimetype):
    from pygments import highlight
    from pygments.lexers import get_lexer_for_mimetype
    from pygments.formatters import TerminalFormatter

    lexer = get_lexer_for_mimetype(mimetype, encoding='utf-8')
    formatter = TerminalFormatter(encoding='utf-8')

    @contextmanager
    def filter(output):
        with make_temp_file() as f:
            yield f
            f.seek(0)
            code = f.read()
        highlight(code, lexer, formatter, output)
    return filter


@contextmanager
def make_temp_file():
    import tempfile
    import os
    fd, name = tempfile.mkstemp()
    with unlink_path(name):
        with os.fdopen(fd, 'w+') as f:
            yield f


@contextmanager
def unlink_path(path):
    import os
    try:
        yield
    finally:
        os.unlink(path)


def pager():
    import os
    import shlex
    pager_cmd = os.environ.get('PAGER')
    if pager_cmd:
        pager_cmd = shlex.split(pager_cmd)
        return output_thru_subprocess(pager_cmd)
    return pager_less


pager_less = output_thru_subprocess(['less', '-R'])
