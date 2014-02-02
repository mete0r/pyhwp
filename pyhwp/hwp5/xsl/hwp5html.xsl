<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.w3.org/1999/xhtml">
  <xsl:import href="hwp5css-common.xsl" />
  <xsl:output method="xml" encoding="utf-8" indent="yes"
      doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
      doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
      />

  <xsl:param name="embed-styles-css" select="0" />

  <xsl:template match="/">
    <xsl:apply-templates select="HwpDoc" mode="html" />
  </xsl:template>

  <xsl:template match="HwpDoc" mode="html">
    <xsl:element name="html">
      <xsl:element name="head">
        <xsl:element name="meta">
          <xsl:attribute name="http-equiv">content-type</xsl:attribute>
          <xsl:attribute name="content">text/html; charset=utf-8</xsl:attribute>
        </xsl:element>
        <xsl:apply-templates select="HwpSummaryInfo" mode="head" />
        <xsl:apply-templates select="DocInfo" mode="head" />
      </xsl:element>
      <xsl:apply-templates select="BodyText" mode="body" />
    </xsl:element>
  </xsl:template>

  <xsl:template match="HwpSummaryInfo" mode="head">
    <xsl:element name="title">
      <xsl:value-of select="Property[@name='PIDSI_TITLE']/@value" />
    </xsl:element>
  </xsl:template>

  <xsl:template match="DocInfo" mode="head">
    <xsl:choose>
      <xsl:when test="$embed-styles-css = '1'">
        <xsl:apply-templates select="IdMappings" mode="style" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:element name="link">
          <xsl:attribute name="rel">stylesheet</xsl:attribute>
          <xsl:attribute name="href">styles.css</xsl:attribute>
          <xsl:attribute name="type">text/css</xsl:attribute>
        </xsl:element>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="IdMappings" mode="style">
    <xsl:element name="style">
      <xsl:attribute name="type">text/css</xsl:attribute>
      <xsl:apply-templates select="." mode="content" />
    </xsl:element>
  </xsl:template>

  <xsl:template match="BodyText" mode="body">
    <xsl:element name="body">
      <xsl:apply-templates select="SectionDef" mode="div-section" />
    </xsl:element>
  </xsl:template>

  <xsl:template match="SectionDef" mode="div-section">
    <xsl:element name="div">
      <xsl:attribute name="class">Section</xsl:attribute>
      <xsl:for-each select="Paragraph">
        <xsl:apply-templates select="." mode="p"/>
      </xsl:for-each>
    </xsl:element>
  </xsl:template>

  <xsl:template match="Paragraph" mode="p">
    <xsl:element name="p">
      <xsl:variable name="styleid" select="@style-id"/>
      <xsl:attribute name="class"><xsl:value-of select="translate(/HwpDoc/DocInfo/IdMappings/Style[number($styleid)+1]/@name, ' ', '-')" /> parashape-<xsl:value-of select="@parashape-id"/></xsl:attribute>
      <xsl:for-each select="LineSeg">
        <xsl:apply-templates />
      </xsl:for-each>
    </xsl:element>
  </xsl:template>

  <xsl:template match="ControlChar"><xsl:value-of select="@char"/></xsl:template>

  <xsl:template match="Text">
    <xsl:element name="span"><xsl:attribute name="class">charshape-<xsl:value-of select="@charshape-id"/></xsl:attribute><xsl:value-of select="text()"/></xsl:element>
  </xsl:template>

  <xsl:template match="TableCaption">
    <xsl:element name="caption">
      <xsl:attribute name="class">TableCaption</xsl:attribute>
      <xsl:apply-templates />
    </xsl:element>
  </xsl:template>

  <xsl:template match="TableControl">
    <xsl:element name="table">
      <xsl:attribute name="class">borderfill-<xsl:value-of select="TableBody/@borderfill-id"/></xsl:attribute>
      <xsl:attribute name="cellspacing"><xsl:value-of select="TableBody/@cellspacing"/></xsl:attribute>
      <xsl:attribute name="style">border-collapse:collapse;</xsl:attribute>
      <xsl:apply-templates />
    </xsl:element>
  </xsl:template>

  <xsl:template match="TableRow">
    <xsl:element name="tr">
      <xsl:apply-templates />
    </xsl:element>
  </xsl:template>

  <xsl:template match="TableCell">
    <xsl:element name="td">
      <xsl:attribute name="class">borderfill-<xsl:value-of select="@borderfill-id"/></xsl:attribute>
      <xsl:attribute name="style">width:<xsl:value-of select="@width div 100"/>pt; height:<xsl:value-of select="@height div 100"/>pt;</xsl:attribute>
      <xsl:attribute name="rowspan"><xsl:value-of select="@rowspan"/></xsl:attribute>
      <xsl:attribute name="colspan"><xsl:value-of select="@colspan"/></xsl:attribute>
      <xsl:apply-templates />
    </xsl:element>
  </xsl:template>

  <xsl:template match="GShapeObjectControl">
    <xsl:element name="div">
      <xsl:attribute name="class">GShapeObject</xsl:attribute>
      <xsl:apply-templates />
    </xsl:element>
  </xsl:template>

  <xsl:template match="ShapePicture">
    <xsl:variable name="bindataid" select="PictureInfo/@bindata-id"/>
    <xsl:variable name="bindata" select="/HwpDoc/DocInfo/IdMappings/BinData[number($bindataid)]"/>
    <xsl:element name="img">
      <xsl:apply-templates select="$bindata" mode="img-src"/>
      <xsl:attribute name="style">
	<xsl:apply-templates select=".." mode="css-width" />
	<xsl:text> </xsl:text>
	<xsl:apply-templates select=".." mode="css-height" />
      </xsl:attribute>
    </xsl:element>
  </xsl:template>

  <xsl:template match="BinDataEmbedding" mode="img-src">
    <xsl:choose>
      <xsl:when test="@inline = 'true'">
        <xsl:apply-templates select="." mode="img-src-datauri" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="." mode="img-src-external" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="BinDataEmbedding" mode="img-src-external">
    <xsl:variable name="binpath" select="'bindata/'"/>
    <xsl:attribute name="src">
      <xsl:value-of select="$binpath"/>
      <xsl:value-of select="@storage-id"/>
      <xsl:text>.</xsl:text>
      <xsl:value-of select="@ext"/>
    </xsl:attribute>
  </xsl:template>

  <xsl:template match="BinDataEmbedding" mode="img-src-datauri">
    <xsl:attribute name="src">
      <xsl:text>data:;base64,</xsl:text>
      <xsl:value-of select="text()" />
    </xsl:attribute>
  </xsl:template>

  <xsl:template match="ShapeComponent" mode="css-width">
    <xsl:text>width: </xsl:text>
    <xsl:value-of select="@width div 100" />
    <xsl:text>pt;</xsl:text>
  </xsl:template>

  <xsl:template match="ShapeComponent" mode="css-height">
    <xsl:text>height: </xsl:text>
    <xsl:value-of select="@height div 100" />
    <xsl:text>pt;</xsl:text>
  </xsl:template>
</xsl:stylesheet>
