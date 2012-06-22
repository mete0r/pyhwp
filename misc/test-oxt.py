#!/usr/bin/python
# -*- coding: utf-8 -*-

def main():
    import os
    args = ['${buildout:bin-directory}/oxt-test',
            '${buildout:parts-directory}/test']
    os.system(' '.join(args))


if __name__ == '__main__':
    main()
