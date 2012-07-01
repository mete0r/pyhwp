def test_suite():
    from unittest import defaultTestLoader as TL
    from unittest import TestSuite as TS
    tests = []
    tests.append(__import__('test_odtxsl'))
    tests.append(__import__('test_externprogs'))
    tests.append(__import__('test_xmlformat'))
    tests.append(__import__('test_xmlmodel'))
    tests.append(__import__('test_binmodel'))
    tests.append(__import__('test_recordstream'))
    tests.append(__import__('test_filestructure'))
    tests.append(__import__('test_dataio'))
    tests.append(__import__('test_treeop'))
    tests.append(__import__('test_storage'))

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
