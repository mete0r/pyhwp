# -*- coding: utf-8 -*-
from __future__ import with_statement
import logging
import os


logger = logging.getLogger(__name__)


def split(path):
    path_segments = path.split(os.sep)
    path_segments = (seg for seg in path_segments if seg)
    path_segments = list(path_segments)
    return path_segments


def get_ancestors(path):
    path_segments = split(path)
    path = ''
    for seg in path_segments[:-1]:
        path = os.path.join(path, seg)
        yield path
