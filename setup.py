# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2018 mete0r <mete0r@sarangbang.or.kr>
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
from __future__ import absolute_import
from __future__ import print_function
from distutils.command.build import build as _build
import io
import os.path
import subprocess
import sys


def setupdir(f):
    ''' Decorate f to run inside the directory where setup.py resides.
    '''
    setup_dir = os.path.dirname(os.path.abspath(__file__))

    def wrapped(*args, **kwargs):
        old_dir = os.path.abspath(os.curdir)
        try:
            os.chdir(setup_dir)
            return f(*args, **kwargs)
        finally:
            os.chdir(old_dir)

    return wrapped


@setupdir
def import_setuptools():
    try:
        import setuptools
        return setuptools
    except ImportError:
        pass

    import ez_setup
    ez_setup.use_setuptools()
    import setuptools
    return setuptools


@setupdir
def readfile(filename):
    with io.open(filename, 'r', encoding='utf-8') as f:
        return f.read()


def get_version():
    version = readfile('VERSION.txt')
    version = version.strip()
    return version


def get_long_description():
    long_description = readfile('README')
    return long_description


def get_classifiers():
    classifiers = readfile('classifiers.txt')
    classifiers = classifiers.strip()
    classifiers = classifiers.split('\n')
    classifiers = sorted(classifiers)
    return classifiers


def get_install_requires():
    requires = readfile('requirements.in')
    requires = requires.strip()
    requires = requires.split('\n')
    requires = list(requires)
    return requires


class build(_build):
    def run(self):

        #
        # compile message catalogs
        #
        domains = [
            'hwp5proc',
            'hwp5html',
            'hwp5odt',
            'hwp5txt',
            'hwp5view',
        ]
        for domain in domains:
            args = [
                sys.executable,
                __file__,
                'compile_catalog',
                '--domain={}'.format(domain)
                # ..other common options are provided by setup.cfg
            ]
            subprocess.check_call(args)

        #
        # process to normal build operations
        #
        _build.run(self)


setup_info = {

    # basic information

    'name': 'pyhwp',
    'version': get_version(),
    'description': 'hwp file format parser',
    'long_description': get_long_description(),

    # authorative

    'author': 'mete0r',
    'author_email': 'mete0r@sarangbang.or.kr',
    'license': 'GNU Affero General Public License v3 or later (AGPLv3+)',
    'url': 'https://github.com/mete0r/pyhwp',

    # classifying

    'classifiers': get_classifiers(),

    'keywords': 'hwp',

    # packaging

    'setup_requires': [
        'babel',
    ],

    'packages': [
        'hwp5',
        'hwp5.binmodel',
        'hwp5.binmodel.controls',
        'hwp5.plat',
        'hwp5.plat._uno',
        'hwp5.proc',
        'hwp5.storage',
        'hwp5.transforms',
    ],
    # do not use '.'; just omit to specify setup.py directory
    'package_dir': {
        '': 'pyhwp',
    },

    'package_data': {
        'hwp5': [
            'README',
            'COPYING',
            'VERSION.txt',
            'xsl/*.xsl',
            'xsl/odt/*.xsl',
            'odf-relaxng/OpenDocument-v1.2-os-*.rng',
            'locale/*/*/*.mo',
        ],
    },

    # 'python_requires': '>=2.7, <3',

    # installation

    'zip_safe': False,

    'entry_points': {
        'console_scripts': [
            'hwp5spec=hwp5.binspec:main',
            'hwp5proc=hwp5.proc:main',
            'hwp5odt=hwp5.hwp5odt:main',
            'hwp5txt=hwp5.hwp5txt:main',
            'hwp5html=hwp5.hwp5html:main',
            'hwp5view=hwp5.hwp5view:main',
        ]
    },

    'install_requires': get_install_requires(),
}


@setupdir
def main():
    setuptools = import_setuptools()
    setup_info['cmdclass'] = {
        'build': build,
    }
    setuptools.setup(**setup_info)


if __name__ == '__main__':
    main()
