# -*- coding: utf-8 -*-
import sys
import urlparse
import os.path
import logging
from binascii import a2b_hex
from hashlib import md5

import requests


logger = logging.getLogger(__name__)


def main():
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)

    url = sys.argv[1]
    dst = sys.argv[2]
    md5_given = a2b_hex(sys.argv[3])
    result = urlparse.urlparse(url)

    filename = os.path.basename(result.path)

    if not os.path.exists(dst):
        destination_path = dst
        logger.debug('%s not exists: destination=%s', dst, destination_path)
    else:
        if os.path.isdir(dst):
            destination_path = os.path.join(dst, filename)
            logger.debug('%s is a directory: destination=%s', dst,
                         destination_path)
        else:
            destination_path = dst

    if os.path.exists(destination_path):
        md5_existing = md5_file(destination_path)
        if md5_given == md5_existing:
            logger.debug('%s exists: skipped', destination_path)
            return

    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(destination_path, 'wb') as f:
        copy_stream(response.raw, f)

    md5_downloaded = md5_file(destination_path)
    if md5_given != md5_downloaded:
        logger.error('md5 not match: %s', b2a_hex(md5_downloaded))
        raise SystemExit(1)


def copy_stream(src, dst):
    while True:
        data = src.read(16384)
        if len(data) == 0:
            break
        dst.write(data)


def md5_file(path):
    with open(path, 'rb') as f:
        m = md5('')
        while True:
            data = f.read(16384)
            if len(data) == 0:
                break
            m.update(data)
    return m.digest()
