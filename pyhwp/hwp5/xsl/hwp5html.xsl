<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" encoding="utf-8" indent="yes"
        doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
        doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
        />
    <xsl:template match="/">
        <html>
            <head>
                <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
                <link rel="stylesheet" href="styles.css" type="text/css"/>
            </head>
            <xsl:element name="body">
                <xsl:for-each select="HwpDoc/BodyText">
                    <xsl:apply-templates />
                </xsl:for-each>
            </xsl:element>
        </html>
    </xsl:template>

    <xsl:template match="Paragraph">
        <xsl:element name="p">
            <xsl:variable name="styleid" select="@style-id"/>
            <xsl:attribute name="class"><xsl:value-of select="translate(/HwpDoc/DocInfo/IdMappings/Style[number($styleid)+1]/@name, ' ', '-')" /> parashape-<xsl:value-of select="@parashape-id"/></xsl:attribute>
            <xsl:apply-templates />
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
      <xsl:variable name="binpath" select="'bindata/'"/>
      <xsl:attribute name="src">
        <xsl:value-of select="$binpath"/>
        <xsl:value-of select="@storage-id"/>
        <xsl:text>.</xsl:text>
        <xsl:value-of select="@ext"/>
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
