def test_suite():
    from unittest import defaultTestLoader as TL
    from unittest import TestSuite as TS
    tests = []
    from hwp5.tests import test_odtxsl as T
    tests.append(T)
    from hwp5.tests import test_xmlformat as T
    tests.append(T)
    from hwp5.tests import test_xmlmodel as T
    tests.append(T)
    from hwp5.tests import test_binmodel as T
    tests.append(T)
    from hwp5.tests import test_recordstream as T
    tests.append(T)
    from hwp5.tests import test_filestructure as T
    tests.append(T)
    from hwp5.tests import test_dataio as T
    tests.append(T)
    from hwp5.tests import test_treeop as T
    tests.append(T)
    from hwp5.tests import test_ole as T
    tests.append(T)
    from hwp5.tests import test_storage as T
    tests.append(T)

    # localtest: a unittest module which resides at the local test site only;
    # should not be checked in the source code repository
    try:
        import localtest
    except ImportError, e:
        print 'localtest import failed: ', e
        pass
    else:
        tests[0:0] = [localtest]

    return TS((TL.loadTestsFromModule(m) for m in tests))


def get_fixture_path(filename):
    import os.path
    path = os.path.join('fixtures', filename)
    from hwp5.importhelper import pkg_resources_filename
    return pkg_resources_filename('hwp5.tests', path)


def open_fixture(filename, *args, **kwargs):
    path = get_fixture_path(filename)
    return open(path, *args, **kwargs)
