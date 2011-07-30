<?xml version="1.0" encoding="UTF-8"?><xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
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
  <xsl:import href="odt-common.xsl" />
  <xsl:output method="xml" encoding="utf-8" indent="yes" />
  <xsl:template match="/">
    <office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
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
      <office:scripts/>
      <office:font-face-decls/>
      <office:automatic-styles>
        <xsl:for-each select="HwpDoc/BodyText//Paragraph">
          <xsl:variable name="paragraph-id" select="@paragraph-id + 1"/>
          <xsl:variable name="style-id" select="@style-id + 1" />
          <xsl:variable name="style" select="/HwpDoc/DocInfo/IdMappings/Style[$style-id]"/>
          <xsl:variable name="style-parashape-id" select="$style/@parashape-id + 1"/>
          <xsl:variable name="parashape-id" select="@parashape-id + 1"/>
          <xsl:variable name="parashapes" select="/HwpDoc/DocInfo/IdMappings/ParaShape" />
          <xsl:variable name="parashape" select="$parashapes[number($parashape-id)]"/>
          <xsl:if test="$style-parashape-id != $parashape-id">
            <xsl:element name="style:style">
              <xsl:attribute name="style:family">paragraph</xsl:attribute>
              <xsl:attribute name="style:class">text</xsl:attribute>
              <xsl:attribute name="style:name">Paragraph-<xsl:value-of select="@paragraph-id + 1" /></xsl:attribute>
              <xsl:attribute name="style:parent-style-name"><xsl:value-of select="$style/@local-name" /></xsl:attribute>
              <xsl:call-template name="parashape-to-paragraph-properties">
                <xsl:with-param name="parashape" select="$parashape"/>
              </xsl:call-template>
            </xsl:element>
          </xsl:if>

          <xsl:variable name="style-charshape-id" select="$style/@charshape-id + 1"/>
          <xsl:for-each select="LineSeg">
            <xsl:variable name="lineseg-pos" select="position()" />
            <xsl:for-each select="Text">
              <xsl:variable name="text-pos" select="position()" />
              <xsl:variable name="charshape-id" select="@charshape-id + 1" />
              <xsl:variable name="charshapes" select="/HwpDoc/DocInfo/IdMappings/CharShape" />
              <xsl:variable name="charshape" select="$charshapes[number($charshape-id)]"/>
              <xsl:if test="$style-charshape-id != $charshape-id">
                <xsl:element name="style:style">
                  <xsl:attribute name="style:family">text</xsl:attribute>
                  <xsl:attribute name="style:name">p<xsl:value-of select="$paragraph-id" />-<xsl:value-of select="$lineseg-pos"/>-<xsl:value-of select="$text-pos"/></xsl:attribute>
                  <xsl:call-template name="charshape-to-text-properties">
                    <xsl:with-param name="charshape" select="$charshape"/>
                  </xsl:call-template>
                </xsl:element>
              </xsl:if>
            </xsl:for-each>
          </xsl:for-each>
        </xsl:for-each>
      </office:automatic-styles>
      <office:body>
        <office:text>
          <text:sequence-decls>
            <text:sequence-decl text:display-outline-level="0" text:name="Illustration"/>
            <text:sequence-decl text:display-outline-level="0" text:name="Table"/>
            <text:sequence-decl text:display-outline-level="0" text:name="Text"/>
            <text:sequence-decl text:display-outline-level="0" text:name="Drawing"/>
          </text:sequence-decls>
          <xsl:for-each select="HwpDoc/BodyText">
              <xsl:apply-templates />
          </xsl:for-each>
        </office:text>
      </office:body>
    </office:document-content>
  </xsl:template>

  <xsl:template match="Paragraph">
      <xsl:element name="text:p">
        <xsl:variable name="style-id" select="@style-id + 1" />
        <xsl:variable name="style" select="/HwpDoc/DocInfo/IdMappings/Style[$style-id]"/>
        <xsl:variable name="style-parashape-id" select="$style/@parashape-id + 1"/>
        <xsl:variable name="parashape-id" select="@parashape-id + 1"/>
        <xsl:variable name="parashapes" select="/HwpDoc/DocInfo/IdMappings/ParaShape" />
        <xsl:variable name="parashape" select="$parashapes[number($parashape-id)]"/>
        <xsl:choose>
          <xsl:when test="$style-parashape-id != $parashape-id">
            <xsl:attribute name="text:style-name">Paragraph-<xsl:value-of select="@paragraph-id + 1"/></xsl:attribute>
          </xsl:when>
          <xsl:otherwise>
            <xsl:attribute name="text:style-name"><xsl:value-of select="$style/@local-name"/></xsl:attribute>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:apply-templates select="LineSeg">
          <xsl:with-param name="paragraph" select="."/>
        </xsl:apply-templates>
      </xsl:element>
      <xsl:apply-templates select="LineSeg/TableControl"/>
  </xsl:template>

  <xsl:template match="LineSeg">
    <xsl:param name="paragraph" />
    <xsl:apply-templates select="Text|GShapeObjectControl|ControlChar">
      <xsl:with-param name="paragraph" select="$paragraph"/>
      <xsl:with-param name="lineseg-pos" select="position()"/>
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="Text">
    <xsl:param name="paragraph"/>
    <xsl:param name="lineseg-pos"/>
    <xsl:variable name="text-pos" select="position()"/>
    <xsl:variable name="paragraph-id" select="$paragraph/@paragraph-id + 1" />
    <xsl:variable name="style-id" select="$paragraph/@style-id + 1" />
    <xsl:variable name="style" select="/HwpDoc/DocInfo/IdMappings/Style[$style-id]" />
    <xsl:variable name="style-charshape-id" select="$style/@charshape-id + 1" />
    <xsl:element name="text:span">
      <xsl:variable name="charshape-id" select="@charshape-id + 1" />
      <xsl:if test="$style-charshape-id != $charshape-id">
        <xsl:attribute name="text:style-name">p<xsl:value-of select="$paragraph-id"/>-<xsl:value-of select="$lineseg-pos"/>-<xsl:value-of select="$text-pos"/></xsl:attribute>
      </xsl:if>
      <xsl:value-of select="text()"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="ControlChar"></xsl:template>

  <xsl:template match="TableControl">
    <table:table>
      <table:table-column>
        <xsl:attribute name="table:number-columns-repeated"><xsl:value-of select="TableBody/@cols"/></xsl:attribute>
      </table:table-column>
      <xsl:for-each select="TableBody/TableRow">
        <table:table-row>
          <xsl:for-each select="TableCell">
            <table:table-cell>
              <xsl:attribute name="table:number-columns-spanned"><xsl:value-of select="@colspan"/></xsl:attribute>
              <xsl:attribute name="table:number-rows-spanned"><xsl:value-of select="@rowspan"/></xsl:attribute>
              <xsl:apply-templates />
            </table:table-cell>
          </xsl:for-each>
        </table:table-row>
      </xsl:for-each>
    </table:table>
  </xsl:template>

  <xsl:template match="GShapeObjectControl">
    <xsl:element name="draw:frame">
        <xsl:attribute name="text:anchor-type">paragraph</xsl:attribute>
        <xsl:attribute name="svg:x"><xsl:value-of select="@x div 100"/>pt</xsl:attribute>
        <xsl:attribute name="svg:y"><xsl:value-of select="@y div 100"/>pt</xsl:attribute>
        <xsl:attribute name="svg:width"><xsl:value-of select="@width div 100"/>pt</xsl:attribute>
        <xsl:attribute name="svg:height"><xsl:value-of select="@height div 100"/>pt</xsl:attribute>
        <xsl:attribute name="draw:z-index"><xsl:value-of select="@z-order"/></xsl:attribute>
        <xsl:apply-templates />
    </xsl:element>
  </xsl:template>

  <xsl:template match="ShapeComponent/ShapePicture">
    <xsl:variable name="binpath" select="'bindata/'"/>
    <xsl:variable name="bindataid" select="PictureInfo/@bindata-id"/>
    <xsl:variable name="bindata" select="/HwpDoc/DocInfo/IdMappings/BinData[number($bindataid)]"/>
    <xsl:element name="draw:image">
        <xsl:choose>
            <xsl:when test="$bindata/BinEmbedded">
                <xsl:attribute name="xlink:href"><xsl:value-of select="$binpath"/><xsl:value-of select="$bindata/BinEmbedded/@storage-id"/>.<xsl:value-of select="$bindata/BinEmbedded/@ext"/></xsl:attribute>
            </xsl:when>
        </xsl:choose>
    </xsl:element>
  </xsl:template>
</xsl:stylesheet>
