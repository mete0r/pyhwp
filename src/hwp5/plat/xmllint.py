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

from zope.interface import implementer

from ..errors import ImplementationNotAvailable
from ..errors import ValidationFailed
from ..interfaces import IRelaxNG
from ..interfaces import IRelaxNGFactory


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


def xmllint_is_reachable(executable):
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


def createRelaxNGFactory(registry, **settings):
    xmllint = settings.get('xmllint.path', 'xmllint')
    if not xmllint_is_reachable(xmllint):
        raise ImplementationNotAvailable(
            'relaxng/xmllint: xmllint is not found', xmllint
        )
    return RelaxNGFactory(xmllint)


@implementer(IRelaxNGFactory)
class RelaxNGFactory:

    def __init__(self, executable):
        self.executable = executable

    def relaxng_validator_from_file(self, rng_path):
        return RelaxNG(executable, rng_path)


@implementer(IRelaxNG)
class RelaxNG:

    def __init__(self, executable, rng_path):
        self.executable = executable
        self.rng_path = rng_path

    @contextmanager
    def validating_output(self, output):
        args = [self.executable, '--relaxng', self.rng_path, '-']
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
                raise ValidationFailed('RelaxNG')

    def validate(self, input_path):
        args = [
            self.executable,
            '--relaxng', self.rng_path,
            '--noout',
            input_path
        ]
        p = subprocess.Popen(args)
        p.wait()
        return p.returncode == 0
