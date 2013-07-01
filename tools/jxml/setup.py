# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os.path
import sys
if not sys.platform.startswith('java'):
    raise SystemExit(1)
os.chdir(os.path.dirname(__file__))
setup(name='jxml',
      packages=find_packages())
