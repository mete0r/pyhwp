<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
  xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
  xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
  xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
  xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
  xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
  xmlns:math="http://www.w3.org/1998/Math/MathML"
  xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0"
  xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
  xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"
  xmlns:ooo="http://openoffice.org/2004/office"
  xmlns:ooow="http://openoffice.org/2004/writer"
  xmlns:oooc="http://openoffice.org/2004/calc"
  xmlns:dom="http://www.w3.org/2001/xml-events"
  xmlns:xforms="http://www.w3.org/2002/xforms"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:rpt="http://openoffice.org/2005/report"
  xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
  xmlns:xhtml="http://www.w3.org/1999/xhtml"
  xmlns:grddl="http://www.w3.org/2003/g/data-view#"
  xmlns:tableooo="http://openoffice.org/2009/table"
  xmlns:field="urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0"
  xmlns:formx="urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:form:1.0"
  xmlns:css3t="http://www.w3.org/TR/css3-text/"
  office:version="1.2"
  grddl:transformation="http://docs.oasis-open.org/office/1.2/xslt/odf2rdf.xsl"
  office:mimetype="application/vnd.oasis.opendocument.text">
  <xsl:output method="xml" encoding="utf-8" indent="yes" />
  <xsl:template name="parashape-to-paragraph-properties">
    <xsl:param name="parashape"/>
    <xsl:element name="style:paragraph-properties">
      <xsl:attribute name="fo:text-align">
        <xsl:choose>
          <xsl:when test="$parashape/@align = 'both'">justify</xsl:when>
          <xsl:when test="$parashape/@align = 'left'">left</xsl:when>
          <xsl:when test="$parashape/@align = 'right'">right</xsl:when>
          <xsl:when test="$parashape/@align = 'center'">center</xsl:when>
          <xsl:when test="$parashape/@align = 'distribute'">justify</xsl:when>
          <xsl:when test="$parashape/@align = 'distribute-space'">justify</xsl:when>
        </xsl:choose>
      </xsl:attribute>
      <xsl:variable name="margin-left" select="number($parashape/@doubled-margin-left)"/>
      <xsl:variable name="indent" select="number($parashape/@indent)"/>
      <xsl:attribute name="fo:text-indent"><xsl:value-of select="$indent div 200"/>pt</xsl:attribute>
      <xsl:attribute name="fo:margin-left">
        <xsl:choose>
          <xsl:when test="$indent &lt; 0"><xsl:value-of select="($margin-left - $indent) div 200"/>pt</xsl:when>
          <xsl:otherwise><xsl:value-of select="$margin-left div 200"/>pt</xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:attribute name="fo:margin-right"><xsl:value-of select="number($parashape/@doubled-margin-right) div 200"/>pt</xsl:attribute>
      <xsl:attribute name="fo:margin-top"><xsl:value-of select="number($parashape/@doubled-margin-top) div 200"/>pt</xsl:attribute>
      <xsl:attribute name="fo:margin-bottom"><xsl:value-of select="number($parashape/@doubled-margin-bottom) div 200"/>pt</xsl:attribute>
      <!--
        줄 간격
      -->
      <xsl:choose>
        <!--
          줄 간격: 글자에 따라
        -->
        <xsl:when test="$parashape/@linespacing-type = 'ratio'">
          <xsl:attribute name="fo:line-height"><xsl:value-of select="number($parashape/@linespacing-before-2007)"/>%</xsl:attribute>
        </xsl:when>
        <!--
          줄 간격: 고정 값
        -->
        <xsl:when test="$parashape/@linespacing-type = 'fixed'">
          <xsl:attribute name="fo:line-height"><xsl:value-of select="number($parashape/@linespacing-before-2007) div 200"/>pt</xsl:attribute>
          <xsl:attribute name="style:vertical-align">top</xsl:attribute>
        </xsl:when>
        <!--
          줄 간격: 여백만 지정
        -->
        <xsl:when test="$parashape/@linespacing-type = 'spaceonly'">
          <xsl:attribute name="style:line-spacing"><xsl:value-of select="number($parashape/@linespacing-before-2007) div 200 div 2"/>pt</xsl:attribute>
          <xsl:attribute name="style:vertical-align">top</xsl:attribute>
        </xsl:when>
      </xsl:choose>
    </xsl:element>
  </xsl:template>

  <xsl:template name="charshape-to-text-properties">
    <xsl:param name="charshape"/>
    <xsl:variable name="facenames" select="/HwpDoc/DocInfo/IdMappings/FaceName" />
    <xsl:variable name="fontface" select="$charshape/FontFace"/>
    <xsl:variable name="facename-en-id" select="$fontface/@en + 1"/>
    <xsl:variable name="facename-en" select="$facenames[$facename-en-id]/@name"/>
    <xsl:variable name="facename-ko-id" select="$fontface/@ko + 1"/>
    <xsl:variable name="facename-ko" select="$facenames[$facename-ko-id]/@name"/>
    <xsl:element name="style:text-properties">
      <xsl:attribute name="style:font-name"><xsl:value-of select="$facename-en"/></xsl:attribute>
      <xsl:attribute name="style:font-name-asian"><xsl:value-of select="$facename-ko"/></xsl:attribute>
      <xsl:attribute name="fo:font-size"><xsl:value-of select="$charshape/@basesize div 100"/>pt</xsl:attribute>
      <xsl:attribute name="style:font-size-asian"><xsl:value-of select="$charshape/@basesize div 100"/>pt</xsl:attribute>
      <!-- 15.4.25 Font Style -->
      <xsl:if test="$charshape/@italic = 1">
        <xsl:attribute name="fo:font-style">italic</xsl:attribute>
        <xsl:attribute name="style:font-style-asian">italic</xsl:attribute>
        <xsl:attribute name="style:font-style-complex">italic</xsl:attribute>
      </xsl:if>
      <!-- 15.4.28 Underlining Type -->
      <xsl:choose>
        <xsl:when test="$charshape/@underline = 'none'">
          <xsl:attribute name="text:text-underline-type">none</xsl:attribute>
        </xsl:when>
        <xsl:when test="$charshape/@underline = 'underline'">
          <xsl:attribute name="style:text-underline-type">single</xsl:attribute>
          <xsl:attribute name="style:text-underline-style">solid</xsl:attribute>
          <xsl:attribute name="style:text-underline-width">auto</xsl:attribute>
          <!-- 15.4.31 Underline Color -->
          <xsl:attribute name="style:text-underline-color"><xsl:value-of select="$charshape/@underline-color"/></xsl:attribute>
        </xsl:when>
        <xsl:when test="$charshape/@underline = 'upperline'">
          <xsl:attribute name="style:text-overline-type">single</xsl:attribute>
          <xsl:attribute name="style:text-overline-style">solid</xsl:attribute>
          <xsl:attribute name="style:text-overline-width">auto</xsl:attribute>
          <xsl:attribute name="style:text-overline-color"><xsl:value-of select="$charshape/@underline-color"/></xsl:attribute>
        </xsl:when>
        <xsl:otherwise>
        </xsl:otherwise>
      </xsl:choose>
      <!-- 15.4.32 Font Weight -->
      <xsl:if test="$charshape/@bold = 1">
        <xsl:attribute name="fo:font-weight">bold</xsl:attribute>
        <xsl:attribute name="style:font-weight-asian">bold</xsl:attribute>
        <xsl:attribute name="style:font-weight-complex">bold</xsl:attribute>
      </xsl:if>
    </xsl:element>
  </xsl:template>
</xsl:stylesheet>
