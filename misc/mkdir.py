# -*- coding: utf-8 -*-

import sys
import os.path
import shutil

if __name__ == '__main__':
    d = sys.argv[1]
    if os.path.exists(d):
        print('rmtree: %s' % d)
        shutil.rmtree(d)
    print('mkdir: %s' % d)
    os.makedirs(d)
