<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:import href="hwp5css-common.xsl" />
  <xsl:output method="text" media-type="text/css" encoding="utf-8" indent="no" />
  <xsl:template match="/">
    <xsl:apply-templates select="HwpDoc/DocInfo/IdMappings" mode="content" />
  </xsl:template>
</xsl:stylesheet>
