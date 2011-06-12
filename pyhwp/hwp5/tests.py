def test_suite():
    from unittest import defaultTestLoader as TL
    from unittest import TestSuite as TS
    import test_models
    import test_dataio
    import test_hwpxml
    return TS((TL.loadTestsFromModule(m) for m in [test_models, test_dataio, test_hwpxml]))
