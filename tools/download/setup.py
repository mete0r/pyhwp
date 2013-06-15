# -*- coding: utf-8 -*-
from setuptools import setup
setup(name='pyhwp.develop.download',
      py_modules=['pyhwp_download'],
      install_requires=['requests'],
      entry_points=dict(console_scripts=['pyhwp-download = pyhwp_download:main']))
