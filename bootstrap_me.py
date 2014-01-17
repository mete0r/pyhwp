# -*- coding: utf-8 -*-

import os.path
import sys


def main():
    role = len(sys.argv) > 1 and sys.argv[1] or 'translator'

    this_dir = os.path.dirname(__file__)
    dst_path = os.path.join(this_dir, 'buildout.cfg')
    with file(dst_path, 'w') as f:
        f.write('[buildout]\n')
        f.write('extends = buildouts/' + role + '.cfg\n')


if __name__ == '__main__':
    main()
