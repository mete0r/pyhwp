# -*- coding: utf-8 -*-
import logging
import os.path


logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])


def find_files(root):
    import os
    import os.path
    for name in os.listdir(root):
        path = os.path.join(root, name)
        yield path
        if os.path.isdir(path):
            for x in find_files(path):
                yield x


def find_pyc_files(root):
    for path in find_files(root):
        if path.endswith('.pyc') or path.endswith('$py.class'):
            yield path


def main():
    import sys
    import os.path

    logging.basicConfig(level=logging.INFO)

    for root in sys.argv[1:]:
        if os.path.isdir(root):
            for path in find_pyc_files(root):
                if not os.path.isdir(path):
                    logger.info('unlink %s', path)
                    os.unlink(path)


if __name__ == '__main__':
    main()
