# -*- coding: utf-8 -*-
import sys
import os.path
import logging
import tempfile
import shutil

import setuptools.archive_util


logger = logging.getLogger(__name__)


def main():
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)

    src = sys.argv[1]
    dst = sys.argv[2]

    strip_toplevel_dir = True

    if not os.path.exists(dst):
        os.makedirs(dst)

    if not os.path.isdir(dst):
        logger.error('%s: not a directory', dst)

    if strip_toplevel_dir:
        tempdir = tempfile.mkdtemp()
        try:
            setuptools.archive_util.unpack_archive(src, tempdir)
            toplevel_items = os.listdir(tempdir)
            if len(toplevel_items) > 1:
                logger.error('%s has no single top-level directory', src)
                raise SystemExit(1)
            root = os.path.join(tempdir, toplevel_items[0])
            for item in os.listdir(root):
                src_item = os.path.join(root, item)
                dst_item = os.path.join(dst, item)
                if os.path.exists(dst_item):
                    if os.path.isdir(dst_item):
                        shutil.rmtree(dst_item)
                    else:
                        os.unlink(dst_item)
                shutil.move(src_item, dst)
        finally:
            shutil.rmtree(tempdir)
    else:
        setuptools.archive_util.unpack_archive(src, dst)
