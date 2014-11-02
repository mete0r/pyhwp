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
from __future__ import with_statement
from copy import deepcopy
import sys
import os.path


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


# TODO: load from setup.json
_metadata = {

    # basic information

    'name': 'pyhwp',
    '@version': 'VERSION.txt',
    'description': 'hwp file format parser',
    '@long_description': 'README',

    # authorative

    'author': 'mete0r',
    'author_email': 'mete0r@sarangbang.or.kr',
    'license': 'GNU Affero General Public License v3 or later (AGPLv3+)',
    'url': 'https://github.com/mete0r/pyhwp',

    # classifying

    '@classifiers': 'classifiers.txt',

    'keywords': 'hwp',

    # packaging

    'setup_requires': [],

    '@root_package': 'pyhwp',

    'package_data': {
        'hwp5': [
            'README',
            'COPYING',
            'VERSION.txt',
            'xsl/*.xsl',
            'xsl/odt/*.xsl',
            'odf-relaxng/OpenDocument-v1.2-os-*.rng'
        ]
    },

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

    '@requires': 'requirement.txt',
}


@setupdir
def readfile(filename):
    with file(filename) as f:
        return f.read()


@setupdir
def export_metadata(metadata, filename):
    try:
        import json
    except ImportError:
        return
    with file(filename, 'w') as f:
        json.dump(metadata, f, indent=2, sort_keys=True)


export_metadata(_metadata, 'setup.json')


@setupdir
def preprocess_metadata(template_metadata):

    metadata = deepcopy(template_metadata)

    if '@root_package' in metadata:
        setuptools = import_setuptools()
        find_packages = setuptools.find_packages

        root_dir = metadata.pop('@root_package')
        packages = find_packages(root_dir)
        metadata['packages'] = packages

        package_dir = metadata.get('package_dir', {})
        package_dir[''] = root_dir
        metadata['package_dir'] = package_dir

    if '@version' in metadata:
        version = metadata.pop('@version')
        version = readfile(version)
        version = version.strip()
        metadata['version'] = version

    if '@long_description' in metadata:
        long_description = metadata.pop('@long_description')
        long_description = readfile(long_description)
        metadata['long_description'] = long_description

    if '@classifiers' in metadata:
        classifiers = metadata.pop('@classifiers')
        classifiers = readfile(classifiers)
        classifiers = classifiers.strip()
        classifiers = classifiers.split('\n')
        classifiers = sorted(classifiers)
        metadata['classifiers'] = classifiers

    if '@requires' in metadata:
        requires = metadata.pop('@requires')
        requires = readfile(requires)
        requires = requires.strip()
        requires = requires.split('\n')
        requires = requires_from_requirements(requires)
        requires = list(requires)
        metadata['requires'] = requires

    # TODO:
    # insert/replace 'Development Status' classifier along with alpha/beta tag
    # in version?

    # TODO:
    # check License classifiers?
    # sync License classifiers and license field?

    # TODO:
    # Make os/python version/implementation classifier to reflect CI result
    # automatically?

    return metadata


def requires_from_requirements(requirements):
    for req in requirements:
        name, op, version = req.split(' ')
        yield name, op, version


metadata = preprocess_metadata(_metadata)
export_metadata(metadata, 'setup-static.json')


def prepare_runtime_metadata(metadata):

    metadata = deepcopy(metadata)

    if sys.version_info >= (2, 6):
        setup_requires = metadata.get('setup_requires', [])
        setup_requires += ['wheel']
        metadata['setup_requires'] = setup_requires

    if 'requires' in metadata:
        requires = metadata['requires']
        metadata['requires'] = list(('%s(%s%s)' % req)
                                    for req in requires)

        install_requires = metadata.get('install_requires', [])
        install_requires += list(('%s %s %s') % req
                                 for req in requires)
        metadata['install_requires'] = install_requires

    if 'java' not in sys.platform and sys.version < '3':
        install_requires = metadata.get('install_requires', [])
        if sys.version_info < (2, 6):
            # OleFileIO_PL 0.30 has dropped Python 2.5 support
            olefileio = 'OleFileIO_PL >= 0.23'
            olefileio += ', < 0.30'
        else:
            olefileio = 'olefile >= 0.40'
        install_requires.append(olefileio)
        metadata['install_requires'] = install_requires

    try:
        __import__('json')
    except ImportError:
        install_requires = metadata.get('install_requires', [])
        install_requires.append('simplejson')
        metadata['install_requires'] = install_requires

    return metadata


runtime_metadata = prepare_runtime_metadata(metadata)
export_metadata(runtime_metadata, 'setup-runtime.json')


@setupdir
def main():
    setuptools = import_setuptools()
    setuptools.setup(**runtime_metadata)


if __name__ == '__main__':
    main()
