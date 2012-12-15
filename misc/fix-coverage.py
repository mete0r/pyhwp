# -*- coding: utf-8 -*-
''' fix pyhwp source paths in coverage.xml
'''
import re
import sys


def main():
    f = file(sys.argv[2], 'w')
    try:
        for line in file(sys.argv[1]):
            line = re.sub('filename="[^"]*/hwp5/', 'filename="pyhwp/hwp5/', line)
            f.write(line)
    finally:
        f.close()


if __name__ == '__main__':
    main()
