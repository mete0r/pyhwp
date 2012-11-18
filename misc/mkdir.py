# -*- coding: utf-8 -*-

import sys
import os.path
import shutil

if __name__ == '__main__':
    d = sys.argv[1]
    if os.path.exists(d):
        print 'rmtree:', d
        shutil.rmtree(d)
    print 'mkdir:', d
    os.makedirs(d)
