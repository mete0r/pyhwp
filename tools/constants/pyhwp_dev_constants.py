# -*- coding: utf-8 -*-
import os
import sys


class Recipe(object):

    def __init__(self, buildout, name, options):
        options['pathsep'] = os.pathsep
        options['sep'] = os.sep
        if sys.platform == 'win32':
            options['script_py_suffix'] = '-script.py'
        else:
            options['script_py_suffix'] = ''

    def install(self):
        return []

    def update(self):
        pass
