# -*- coding: utf-8 -*-
from __future__ import with_statement
import logging


logger = logging.getLogger(__name__)


class XsltTestMixin(object):

    xsl = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="utf-8" indent="yes" />
  <xsl:template match="/">
    <xsl:for-each select="inp">
      <xsl:element name="out" />
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>'''

    def test_xslt_compile(self):
        if self.xslt_compile is None:
            logger.warning('%s: skipped', self.id())
            return

        xsl = self.xsl
        xsl_path = self.id() + '.xsl'
        with file(xsl_path, 'w') as f:
            f.write(xsl)

        inp = '<?xml version="1.0" encoding="utf-8"?><inp />'
        inp_path = self.id() + '.inp'
        with file(inp_path, 'w') as f:
            f.write(inp)

        out_path = self.id() + '.out'

        transform = self.xslt_compile(xsl_path)
        self.assertTrue(callable(transform))
        transform(inp_path, out_path)

        from xml.etree import ElementTree as etree
        with file(out_path) as f:
            out_doc = etree.parse(f)
        self.assertEquals('out', out_doc.getroot().tag)

    def test_xslt(self):
        if self.xslt is None:
            logger.warning('%s: skipped', self.id())
            return

        xsl = self.xsl
        xsl_path = self.id() + '.xsl'
        with file(xsl_path, 'w') as f:
            f.write(xsl)

        inp = '<?xml version="1.0" encoding="utf-8"?><inp />'
        inp_path = self.id() + '.inp'
        with file(inp_path, 'w') as f:
            f.write(inp)

        out_path = self.id() + '.out'

        result = self.xslt(xsl_path, inp_path, out_path)
        self.assertTrue('errors' not in result)

        from xml.etree import ElementTree as etree
        with file(out_path) as f:
            out_doc = etree.parse(f)
        self.assertEquals('out', out_doc.getroot().tag)
