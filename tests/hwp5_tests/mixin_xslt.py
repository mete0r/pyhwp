# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from xml.etree import ElementTree as etree
import io
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
        if self.xslt_factory is None:
            logger.warning('%s: skipped', self.id())
            return

        xsl = self.xsl
        xsl_path = self.id() + '.xsl'
        with io.open(xsl_path, 'w', encoding='utf-8') as f:
            f.write(xsl)

        inp = '<?xml version="1.0" encoding="utf-8"?><inp />'
        inp_path = self.id() + '.inp'
        with io.open(inp_path, 'w', encoding='utf-8') as f:
            f.write(inp)

        out_path = self.id() + '.out'

        transform = self.xslt_factory.xslt_from_file(xsl_path)
        with io.open(out_path, 'wb') as f:
            transform.transform_into_stream(inp_path, f)

        with io.open(out_path, 'rb') as f:
            out_doc = etree.parse(f)
        self.assertEqual('out', out_doc.getroot().tag)

    def test_xslt(self):
        if self.xslt_factory is None:
            logger.warning('%s: skipped', self.id())
            return

        xsl = self.xsl
        xsl_path = self.id() + '.xsl'
        with io.open(xsl_path, 'w', encoding='utf-8') as f:
            f.write(xsl)

        inp = '<?xml version="1.0" encoding="utf-8"?><inp />'
        inp_path = self.id() + '.inp'
        with io.open(inp_path, 'w', encoding='utf-8') as f:
            f.write(inp)

        out_path = self.id() + '.out'

        transform = self.xslt_factory.xslt_from_file(xsl_path)
        result = transform.transform(inp_path, out_path)
        self.assertTrue('errors' not in result)

        with io.open(out_path, 'rb') as f:
            out_doc = etree.parse(f)
        self.assertEqual('out', out_doc.getroot().tag)
