# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os.path
import sys
if not sys.platform.startswith('java'):
    raise SystemExit(1)

os.chdir(os.path.dirname(__file__))

console_scripts = ['jxml-annotate = jxml_coverage:annotate_main',
                   'jxml-cov-test = jxml_coverage:cov_test_main']

setup(name='jxml.coverage',
      py_modules=['jxml_coverage'],
      install_requires=['jxml', 'docopt', 'colorama'],
      entry_points=dict(console_scripts=console_scripts))
