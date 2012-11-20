# -*- coding: utf-8 -*-
import os
import os.path
from distutils.core import setup


def main():
    cwd = os.getcwd()
    setupdir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(setupdir)
    try:
        setup(name='discover.lxml',
              py_modules=['discover_lxml'],
              install_requires=['discover.python'],
              entry_points={'zc.buildout':
                            ['default = discover_lxml:DiscoverRecipe']})
    finally:
        os.chdir(cwd)


if __name__ == '__main__':
    main()
