<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:import href="hwp5css-common.xsl" />
  <xsl:output method="text" media-type="text/css" encoding="utf-8" indent="no" />
  <xsl:template match="/">
    <xsl:call-template name="css-rule">
      <xsl:with-param name="selector">body</xsl:with-param>
      <xsl:with-param name="declarations">
	<xsl:call-template name="css-declaration">
	  <xsl:with-param name="property">background-color</xsl:with-param>
	  <xsl:with-param name="value">#eee</xsl:with-param>
	</xsl:call-template>
	<xsl:call-template name="css-declaration">
	  <xsl:with-param name="property">padding</xsl:with-param>
	  <xsl:with-param name="value">4px</xsl:with-param>
	</xsl:call-template>
	<xsl:call-template name="css-declaration">
	  <xsl:with-param name="property">margin</xsl:with-param>
	  <xsl:with-param name="value">0</xsl:with-param>
	</xsl:call-template>
      </xsl:with-param>
    </xsl:call-template>
    <xsl:call-template name="css-rule">
      <xsl:with-param name="selector">.Paper</xsl:with-param>
      <xsl:with-param name="declarations">
	<xsl:call-template name="css-declaration">
	  <xsl:with-param name="property">background-color</xsl:with-param>
	  <xsl:with-param name="value">#fff</xsl:with-param>
	</xsl:call-template>
	<xsl:call-template name="css-declaration">
	  <xsl:with-param name="property">border</xsl:with-param>
	  <xsl:with-param name="value">1px solid black</xsl:with-param>
	</xsl:call-template>
	<xsl:call-template name="css-declaration">
	  <xsl:with-param name="property">margin</xsl:with-param>
	  <xsl:with-param name="value">1em auto</xsl:with-param>
	</xsl:call-template>
      </xsl:with-param>
    </xsl:call-template>
    <xsl:call-template name="css-rule">
      <xsl:with-param name="selector">.Paper:first-child</xsl:with-param>
      <xsl:with-param name="declarations">
	<xsl:call-template name="css-declaration">
	  <xsl:with-param name="property">margin-top</xsl:with-param>
	  <xsl:with-param name="value">0</xsl:with-param>
	</xsl:call-template>
      </xsl:with-param>
    </xsl:call-template>
    <xsl:call-template name="css-rule">
      <xsl:with-param name="selector">.Paper:last-child</xsl:with-param>
      <xsl:with-param name="declarations">
	<xsl:call-template name="css-declaration">
	  <xsl:with-param name="property">margin-bottom</xsl:with-param>
	  <xsl:with-param name="value">0</xsl:with-param>
	</xsl:call-template>
      </xsl:with-param>
    </xsl:call-template>
    <xsl:apply-templates select="HwpDoc/DocInfo/IdMappings" mode="css-rule" />
  </xsl:template>
</xsl:stylesheet>
