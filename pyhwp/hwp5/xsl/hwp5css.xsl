<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:import href="hwp5css-common.xsl" />
  <xsl:output method="text" media-type="text/css" encoding="utf-8" indent="no" />
  <xsl:template match="/">
    <xsl:text>
    body {
      background-color: #eee;
      padding: 4px;
      margin: 0;
    }
    .Paper {
      background-color: #fff;
      border:1px solid black;
      margin: 1em auto;
    }
    .Paper:first-child {
      margin-top: 0;
    }
    .Paper:last-child {
      margin-bottom: 0;
    }
</xsl:text>
    <xsl:apply-templates select="HwpDoc/DocInfo/IdMappings" mode="css-rule" />
  </xsl:template>
</xsl:stylesheet>
