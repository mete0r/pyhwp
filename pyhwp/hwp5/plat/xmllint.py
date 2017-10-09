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
from contextlib import contextmanager
from subprocess import CalledProcessError
import logging
import subprocess


logger = logging.getLogger(__name__)

executable = 'xmllint'
enabled = None


def xmllint_reachable():
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
        enabled = xmllint_reachable()
    return enabled


def enable():
    global enabled
    enabled = True


def disable():
    global enabled
    enabled = False


def relaxng(rng_path, inp_path):
    from subprocess import Popen
    args = [executable, '--noout', '--relaxng', rng_path, inp_path]
    p = Popen(args)
    p.wait()
    return p.returncode == 0


def relaxng_compile(rng_path):
    return RelaxNG(rng_path)


class RelaxNG:

    def __init__(self, rng_path):
        self.rng_path = rng_path

    @contextmanager
    def validating_output(self, output):
        args = [executable, '--relaxng', self.rng_path, '-']
        p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=output)
        try:
            yield p.stdin
        except:
            p.stdin.close()
            p.wait()
            raise
        else:
            p.stdin.close()
            p.wait()
            if p.returncode != 0:
                raise Exception('RelaxNG validation failed')
