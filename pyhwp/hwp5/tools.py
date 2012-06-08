# -*- coding: utf-8 -*-
#
#                    GNU AFFERO GENERAL PUBLIC LICENSE
#                       Version 3, 19 November 2007
#
#    pyhwp : hwp file format parser in python
#    Copyright (C) 2010 mete0r@sarangbang.or.kr
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import logging


logger = logging.getLogger(__name__)


def xsltproc(xsl_filepath):
    ''' create a XSLT function with specified XSL stylesheet file.

        xsl_filepath: a XSL Stylesheet path in filesystem

        returns a transform function
    '''

    def autoclose(p):
        ''' start a detached thread which waits the given subprocess terminates. '''
        import threading
        t = threading.Thread(target=p.wait)
        t.daemon = True
        t.start()

    def transform(infile=None, outfile=None):
        ''' transform file streams with XSL stylesheet at `%s'

            `xsltproc' executable should be in PATH directories.

            transform(infile, outfile)
                : transform infile stream into outfile stream

            transform(infile):
                : returns transformed stream (readable sink)

            transform(outfile=outfile)
                : returns stream to be transformed (writable source)

            transform():
                : returns a tuple of (writable source, readable sink) of transformation
        '''
        import subprocess
        logger.debug('xsltproc process starting')

        stdin = infile or subprocess.PIPE
        stdout = outfile or subprocess.PIPE

        p = subprocess.Popen(['xsltproc', xsl_filepath, '-'], stdin=stdin, stdout=stdout)

        logger.debug('xsltproc process started')

        if infile is None and outfile is None:
            autoclose(p)
            return p.stdin, p.stdout  # transform source, sink
        elif outfile is None:
            autoclose(p)
            return p.stdout  # transformed stream
        elif infile is None:
            autoclose(p)
            return p.stdin  # stream to be transformed
        else:
            p.wait()

        logger.debug('xsltproc process end')
    transform.__doc__ = transform.__doc__ % xsl_filepath
    return transform


class RelaxNGValidationFailed(Exception):
    pass


def relaxng(rng_filepath):
    ''' RelaxNG validator

    :param rng_filepath: RelaxNG schema filepath
    :return: `validate(f)`

    `validate(f)`: validate XML stream against the given RelaxNG schema

    :param f: open file to an XML file
    :return: True if the XML is valid;
             False if `xmllint' program is not found
    :raises RelaxNGValidationFailed: if the XML is not valid

    >>> validate = relaxng(rng_filepath)
    >>> f = file('sample.xml', 'r')
    >>> validate(f)
    '''
    from hwp5.externprogs import xmllint, ProgramNotFound

    kwargs = dict()
    import os
    xmllint_path = os.environ.get('PYHWP_XMLLINT')
    if xmllint_path:
        kwargs['xmllint_path'] = xmllint_path

    transform = xmllint('--noout', '--relaxng', rng_filepath, **kwargs)
    def validate(xml_file):
        from tempfile import TemporaryFile
        tmpf = TemporaryFile()
        try:
            retcode = transform(xml_file, tmpf)
            if retcode != 0:
                raise RelaxNGValidationFailed(tmpf.read())
            return True
        except ProgramNotFound:
            return False
        finally:
            tmpf.close()
    return validate
