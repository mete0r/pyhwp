# -*- coding: utf-8 -*-
import os.path
import logging


logger = logging.getLogger('test-cli')


def main():
    logging.basicConfig(level=logging.INFO)

    if not os.path.exists('/bin/sh'):
        logger.warning('/bin/sh: not-found')
        logger.warning('skipping test-cli')
        return 0

    d = os.path.dirname(__file__)
    shscript = os.path.join(d, 'test-cli.sh')

    cmd = ['/bin/sh', shscript]
    cmd = ' '.join(cmd)
    logger.info('running: %s', cmd)
    ret = os.system(cmd)
    logger.info('exit with %d', ret)
    if ret != 0:
        raise SystemExit(-1)


if __name__ == '__main__':
    main()
