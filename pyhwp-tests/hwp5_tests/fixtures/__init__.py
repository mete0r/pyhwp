# -*- coding: utf-8 -*-

def get_fixture_path(filename):
    from hwp5.importhelper import pkg_resources_filename
    return pkg_resources_filename(__name__, filename)


def open_fixture(filename, *args, **kwargs):
    path = get_fixture_path(filename)
    return open(path, *args, **kwargs)
