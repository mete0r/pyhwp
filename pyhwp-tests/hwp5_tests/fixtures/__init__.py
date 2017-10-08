# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import io


def get_fixture_path(filename):
    from hwp5.importhelper import pkg_resources_filename
    return pkg_resources_filename(__name__, filename)


def open_fixture(filename, *args, **kwargs):
    path = get_fixture_path(filename)
    return io.open(path, *args, **kwargs)
