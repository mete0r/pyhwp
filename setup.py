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
from setuptools import setup, find_packages
import sys


install_requires = []
if 'java' not in sys.platform and sys.version < '3':
    install_requires.append('OleFileIO_PL >= 0.23')

try:
    __import__('json')
except ImportError:
    install_requires.append('simplejson')

install_requires.append('docopt >= 0.6')
install_requires.append('hypua2jamo >= 0.2')


def read(filename):
    import os.path
    filename = os.path.join(os.path.dirname(__file__), filename)
    f = open(filename, 'r')
    try:
        return f.read()
    finally:
        f.close()


setup(name='pyhwp',
      version=read('VERSION.txt').strip(),
      license='GNU Affero GPL v3+',
      description='hwp file format parser',
      long_description=read('README'),
      author='mete0r',
      author_email='mete0r@sarangbang.or.kr',
      url='http://github.com/mete0r/pyhwp',
      keywords='hwp',
      packages=find_packages('pyhwp'),
      package_dir={'': 'pyhwp'},
      package_data=dict(hwp5=['README',
                              'COPYING',
                              'VERSION.txt',
                              'xsl/*.xsl',
                              'xsl/odt/*.xsl',
                              'odf-relaxng/OpenDocument-v1.2-os-*.rng']),
      install_requires=install_requires,

      entry_points={
          'console_scripts': [
              'hwp5spec=hwp5.binspec:main',
              'hwp5proc=hwp5.proc:main',
              'hwp5odt=hwp5.hwp5odt:main',
              'hwp5txt=hwp5.hwp5txt:main',
              'hwp5html=hwp5.hwp5html:main',
          ]
      },
      zip_safe=False,

      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: Jython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Text Processing',
          'Topic :: Text Processing :: Filters',
      ])
