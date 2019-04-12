# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import io
import logging
import shutil

from hwp5.errors import ValidationFailed
from hwp5.utils import mkstemp_open


logger = logging.getLogger(__name__)


class RelaxNGTestMixin(object):

    rng = '''<?xml version="1.0" encoding="UTF-8"?>
<grammar
  xmlns="http://relaxng.org/ns/structure/1.0"
  datatypeLibrary="http://www.w3.org/2001/XMLSchema-datatypes">
  <define name="doc">
    <element name="doc" >
      <optional>
        <attribute name="attr">
          <data type="string"/>
        </attribute>
      </optional>
    </element>
  </define>
  <start>
    <choice>
      <ref name="doc"/>
    </choice>
  </start>
</grammar>
'''

    def test_relaxng_compile(self):
        if self.relaxng_compile is None:
            logger.warning('%s: skipped', self.id())
            return

        rng = self.rng
        rng_path = self.id() + '.rng'
        with io.open(rng_path, 'w', encoding='utf-8') as f:
            f.write(rng)

        inp = '<?xml version="1.0" encoding="utf-8"?><doc />'
        inp_path = self.id() + '.inp'
        with io.open(inp_path, 'w', encoding='utf-8') as f:
            f.write(inp)

        bad = '<?xml version="1.0" encoding="utf-8"?><bad />'
        bad_path = self.id() + '.bad'
        with io.open(bad_path, 'w', encoding='utf-8') as f:
            f.write(bad)

        relaxng = self.relaxng_compile(rng_path)
        self.assertTrue(relaxng.validate(inp_path))
        self.assertFalse(relaxng.validate(bad_path))

        with io.open(inp_path, 'rb') as f:
            with mkstemp_open() as (tmp_path, g):
                with relaxng.validating_output(g) as g:
                    shutil.copyfileobj(f, g)

        with io.open(bad_path, 'rb') as f:
            with mkstemp_open() as (tmp_path, g):
                try:
                    with relaxng.validating_output(g) as g:
                        shutil.copyfileobj(f, g)
                except ValidationFailed:
                    pass
                else:
                    assert False, 'ValidationError expected'

    def test_relaxng(self):
        if self.relaxng is None:
            logger.warning('%s: skipped', self.id())
            return

        rng = self.rng
        rng_path = self.id() + '.rng'
        with io.open(rng_path, 'w', encoding='utf-8') as f:
            f.write(rng)

        inp = '<?xml version="1.0" encoding="utf-8"?><doc />'
        inp_path = self.id() + '.inp'
        with io.open(inp_path, 'w', encoding='utf-8') as f:
            f.write(inp)

        bad = '<?xml version="1.0" encoding="utf-8"?><bad />'
        bad_path = self.id() + '.bad'
        with io.open(bad_path, 'w', encoding='utf-8') as f:
            f.write(bad)

        self.assertTrue(self.relaxng(rng_path, inp_path))
        self.assertFalse(self.relaxng(rng_path, bad_path))
