# -*- coding: utf-8 -*-

def get_fixture_path(filename):
    import os.path
    path = os.path.join('fixtures', filename)
    from hwp5.importhelper import pkg_resources_filename
    return pkg_resources_filename('hwp5.tests', path)


def open_fixture(filename, *args, **kwargs):
    path = get_fixture_path(filename)
    return open(path, *args, **kwargs)
