# -*- coding: utf-8 -*-
''' jenkins job script '''

import os
import os.path

def get_mtime(path):
    st = os.stat(path)
    return st.st_mtime

class ExitError(Exception):
    pass

def system(*args):
    exitcode = os.system(*args)
    if exitcode != 0:
        raise ExitError(exitcode)

def bootstrap():
    if not os.path.exists('bin/buildout'):
        print 'bin/buildout missing'
        system('python bootstrap.py')

def buildout():
    if (not os.path.exists('.installed.cfg')
        or get_mtime('.installed.cfg') < get_mtime('buildout.cfg')):
        print 'running bin/buildout'
        system('bin/buildout')

def test():
    print 'running bin/test'
    system('bin/test')

def pylint():
    print 'running pylint'
    system('bin/pylint -f parseable hwp5 | tee pylint.out')

def main():
    bootstrap()
    buildout()
    test()
    pylint()
    return 0

if __name__ == '__main__':
    exit(main())
