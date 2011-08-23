def test_suite():
    from unittest import defaultTestLoader as TL
    from unittest import TestSuite as TS
    import test_binmodel
    import test_dataio
    import test_hwpxml
    import test_filestructure
    import test_odtxsl
    return TS((TL.loadTestsFromModule(m) for m in [test_filestructure, test_binmodel, test_dataio, test_hwpxml, test_odtxsl]))
