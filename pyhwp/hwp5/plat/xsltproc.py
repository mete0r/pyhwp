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
from subprocess import CalledProcessError
from subprocess import Popen
import logging
import subprocess


logger = logging.getLogger(__name__)

executable = 'xsltproc'
enabled = None


def xslt_reachable():
    args = [executable, '--version']
    try:
        subprocess.check_output(args)
    except OSError:
        return False
    except CalledProcessError:
        return False
    except Exception as e:
        logger.exception(e)
        return False
    else:
        return True


def is_enabled():
    global enabled
    if enabled is None:
        enabled = xslt_reachable()
    return enabled


def enable():
    global enabled
    enabled = True


def disable():
    global enabled
    enabled = False


def xslt(xsl_path, inp_path, out_path):
    xslt = XSLT(xsl_path)
    return xslt.transform(inp_path, out_path)


class XSLT:

    def __init__(self, xsl_path, **params):
        self.xsl_path = xsl_path
        self.cmd = [executable]
        for name, value in params.items():
            self.cmd.extend(['--stringparam', name, value])

    def transform(self, input, output):
        '''
        >>> T.transform('input.xml', 'output.xml')
        '''
        cmd = self.cmd + ['-o', output, self.xsl_path, input]
        logger.info('%r', cmd)
        p = Popen(cmd)
        p.wait()
        if p.returncode == 0:
            return dict()
        else:
            return dict(errors=[])

    def transform_into_stream(self, input, output):
        '''
        >>> T.transform_into_stream('input.xml', sys.stdout)
        '''
        cmd = self.cmd + [self.xsl_path, input]
        logger.info('%r', cmd)
        p = Popen(cmd, stdout=output)
        p.wait()
        if p.returncode == 0:
            return dict()
        else:
            return dict(errors=[])


def xslt_compile(xsl_path, **params):
    xslt = XSLT(xsl_path, **params)
    return xslt.transform_into_stream
