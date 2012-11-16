# -*- coding: utf-8 -*-
from __future__ import with_statement
import logging


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
        with file(rng_path, 'w') as f:
            f.write(rng)

        inp = '<?xml version="1.0" encoding="utf-8"?><doc />'
        inp_path = self.id() + '.inp'
        with file(inp_path, 'w') as f:
            f.write(inp)

        bad = '<?xml version="1.0" encoding="utf-8"?><bad />'
        bad_path = self.id() + '.bad'
        with file(bad_path, 'w') as f:
            f.write(bad)

        validate = self.relaxng_compile(rng_path)
        self.assertTrue(callable(validate))
        self.assertTrue(validate(inp_path))
        self.assertFalse(validate(bad_path))

    def test_relaxng(self):
        if self.relaxng is None:
            logger.warning('%s: skipped', self.id())
            return

        rng = self.rng
        rng_path = self.id() + '.rng'
        with file(rng_path, 'w') as f:
            f.write(rng)

        inp = '<?xml version="1.0" encoding="utf-8"?><doc />'
        inp_path = self.id() + '.inp'
        with file(inp_path, 'w') as f:
            f.write(inp)

        bad = '<?xml version="1.0" encoding="utf-8"?><bad />'
        bad_path = self.id() + '.bad'
        with file(bad_path, 'w') as f:
            f.write(bad)

        self.assertTrue(self.relaxng(rng_path, inp_path))
        self.assertFalse(self.relaxng(rng_path, bad_path))
