# -*- coding: utf-8 -*-
from setuptools import setup
setup(name='pyhwp.develop.unpack',
      py_modules=['pyhwp_unpack'],
      install_requires=['setuptools'],
      entry_points=dict(console_scripts=['pyhwp-unpack = pyhwp_unpack:main']))
