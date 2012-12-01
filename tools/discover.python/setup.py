# -*- coding: utf-8 -*-
import os
import os.path
from distutils.core import setup

def main():
    cwd = os.getcwd()
    setupdir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(setupdir)
    try:
        setup(name='discover.python',
              py_modules=['discover_python'],
              entry_points={'zc.buildout': ['default = discover_python:Discover']})
    finally:
        os.chdir(cwd)


if __name__ == '__main__':
    main()
