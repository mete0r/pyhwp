# -*- coding: utf-8 -*-
from unittest import TestCase

from hwp5.plat import gir_gsf

from hwp5_tests.fixtures import get_fixture_path
from hwp5_tests.mixin_olestg import OleStorageTestMixin


def skip_if_disabled(f):

    def wrapper(*args, **kwargs):
        if not gir_gsf.is_enabled():
            return
        return f(*args, **kwargs)

    return wrapper


class TestGirGsf(TestCase):

    sample_path = get_fixture_path('sample-5017.hwp')

    @skip_if_disabled
    def test_open(self):
        gir_gsf.open(self.sample_path)

    @skip_if_disabled
    def test_listdir(self):
        gsfole = gir_gsf.open(self.sample_path)

        children = list(gir_gsf.listdir(gsfole))
        self.assertEquals(set(['BinData', 'DocInfo', 'PrvText',
                               'Scripts', 'BodyText', 'PrvImage',
                               'DocOptions', 'FileHeader',
                               '\x05HwpSummaryInformation']),
                          set(children))


class TestOleStorageGirGsf(TestCase, OleStorageTestMixin):

    def setUp(self):
        from hwp5.plat import gir_gsf
        if gir_gsf.is_enabled():
            self.OleStorage = gir_gsf.OleStorage
