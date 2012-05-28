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
  <xsl:output method="xml" encoding="utf-8" indent="no" />
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
                             grddl:transformation="http://docs.oasis-open.org/office/1.2/xslt/odf2rdf.xsl">
      <office:scripts/>
      <office:font-face-decls/>
      <office:automatic-styles>
        <xsl:for-each select="HwpDoc/BodyText/SectionDef/Paragraph">
          <xsl:variable name="paragraph-id" select="@paragraph-id + 1"/>
          <xsl:variable name="style-id" select="@style-id + 1" />
          <xsl:variable name="style" select="/HwpDoc/DocInfo/IdMappings/Style[$style-id]"/>
          <xsl:variable name="style-parashape-id" select="$style/@parashape-id + 1"/>
          <xsl:variable name="parashape-id" select="@parashape-id + 1"/>
          <xsl:variable name="parashapes" select="/HwpDoc/DocInfo/IdMappings/ParaShape" />
          <xsl:variable name="parashape" select="$parashapes[number($parashape-id)]"/>
          <xsl:if test="$style-parashape-id != $parashape-id or @new-page = '1'">
            <xsl:element name="style:style">
              <xsl:attribute name="style:family">paragraph</xsl:attribute>
              <xsl:attribute name="style:class">text</xsl:attribute>
              <xsl:attribute name="style:name">Paragraph-<xsl:value-of select="@paragraph-id + 1" /></xsl:attribute>
              <xsl:attribute name="style:parent-style-name"><xsl:value-of select="translate($style/@local-name, ' ', '_')" /></xsl:attribute>
              <xsl:if test="@new-section = '1'">
                <xsl:attribute name="style:master-page-name">MasterPage-<xsl:value-of select="../@section-id + 1"/></xsl:attribute>
              </xsl:if>
              <xsl:element name="style:paragraph-properties">
              <xsl:call-template name="parashape-to-paragraph-properties">
                <xsl:with-param name="parashape" select="$parashape"/>
              </xsl:call-template>
                <xsl:if test="@new-page = '1'">
                  <xsl:attribute name="fo:break-before">page</xsl:attribute>
                </xsl:if>
              </xsl:element>
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
        <xsl:for-each select="HwpDoc/BodyText/SectionDef//TableControl">
          <xsl:element name="style:style">
            <xsl:attribute name="style:name">Table-<xsl:value-of select="@table-id + 1"/></xsl:attribute>
            <xsl:attribute name="style:family">table</xsl:attribute>
            <!-- 15.8 Table Formatting Properties -->
            <xsl:element name="style:table-properties">
              <xsl:choose>
                <xsl:when test="@width-relto = 'absolute'">
                  <!-- 15.8.1 Table Width -->
                  <xsl:attribute name="style:width"><xsl:value-of select="round(@width div 7200 * 2.54 * 10 * 100) div 100"/>mm</xsl:attribute>
                  <!-- 15.8.2 Table Alignment -->
                  <xsl:attribute name="table:align">margins</xsl:attribute>
                  <!-- 15.8.3 Table Left and Right Margin -->
                  <!-- 15.5.17 Left and Right Margin -->
                  <xsl:attribute name="fo:margin-left"><xsl:value-of select="round(@margin-left div 7200 * 2.54 * 10 * 100) div 100"/>mm</xsl:attribute>
                  <xsl:attribute name="fo:margin-right"><xsl:value-of select="round(@margin-right div 7200 * 2.54 * 10 * 100) div 100"/>mm</xsl:attribute>
                </xsl:when>
                <!--
                <xsl:when test="@width-relto = 'paper'"> </xsl:when>
                <xsl:when test="@width-relto = 'page'"> </xsl:when>
                <xsl:when test="@width-relto = 'column'"> </xsl:when>
                <xsl:when test="@width-relto = 'paragraph'"> </xsl:when>
                -->
              </xsl:choose>

              <!-- 15.8.4 Table Top and Bottom Margin -->
              <!-- 15.5.20 Top and Bottom Margin -->
              <xsl:attribute name="fo:margin-top"><xsl:value-of select="round(@margin-top div 7200 * 2.54 * 10 * 100) div 100"/>mm</xsl:attribute>
              <xsl:attribute name="fo:margin-bottom"><xsl:value-of select="round(@margin-bottom div 7200 * 2.54 * 10 * 100) div 100"/>mm</xsl:attribute>

              <!-- 15.8.12 Border Model Property -->
              <xsl:choose>
                <xsl:when test="TableBody/@cellspacing = 0">
                  <xsl:attribute name="table:border-model">collapsing</xsl:attribute>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:attribute name="table:border-model">separating</xsl:attribute>
                </xsl:otherwise>
              </xsl:choose>

            </xsl:element>
          </xsl:element>
        </xsl:for-each>
        <xsl:for-each select="HwpDoc/BodyText/SectionDef//GShapeObjectControl">
          <xsl:element name="style:style">
            <xsl:attribute name="style:name">DrawFrame-<xsl:value-of select="@gshape-id + 1"/></xsl:attribute>
            <xsl:attribute name="style:family">graphic</xsl:attribute>
            <!-- 15.27 Frame Formatting Properties -->
            <xsl:element name="style:graphic-properties">
              <!-- 15.27.4 Left and Right Margins -->
              <xsl:attribute name="fo:margin-left"><xsl:value-of select="round(@margin-left div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
              <xsl:attribute name="fo:margin-right"><xsl:value-of select="round(@margin-right div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
              <!-- 15.27.5 Top and Bottom Margins -->
              <xsl:attribute name="fo:margin-top"><xsl:value-of select="round(@margin-top div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
              <xsl:attribute name="fo:margin-bottom"><xsl:value-of select="round(@margin-bottom div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
              <xsl:choose>
                <xsl:when test="@inline = 0">
                  <!-- 15.27.21 Wrapping -->
                  <xsl:choose>
                    <xsl:when test="@flow = 'float'">
                      <xsl:choose>
                        <xsl:when test="@text-side = 'both'">
                          <xsl:attribute name="style:wrap">parallel</xsl:attribute>
                        </xsl:when>
                        <xsl:when test="@text-side = 'left'">
                          <xsl:attribute name="style:wrap">left</xsl:attribute>
                        </xsl:when>
                        <xsl:when test="@text-side = 'right'">
                          <xsl:attribute name="style:wrap">right</xsl:attribute>
                        </xsl:when>
                        <xsl:when test="@text-side = 'larger'">
                          <xsl:attribute name="style:wrap">biggest</xsl:attribute>
                        </xsl:when>
                      </xsl:choose>
                    </xsl:when>
                    <xsl:when test="@flow = 'block'">
                      <xsl:attribute name="style:wrap">none</xsl:attribute>
                    </xsl:when>
                    <xsl:when test="@flow = 'back'">
                      <xsl:attribute name="style:wrap">run-through</xsl:attribute>
                    </xsl:when>
                    <xsl:when test="@flow = 'front'">
                      <!-- 해당하는 것이 없음 : 가장 비슷한 run-through를 채택 -->
                      <xsl:attribute name="style:wrap">run-through</xsl:attribute>
                    </xsl:when>
                  </xsl:choose>
                </xsl:when>
                <xsl:otherwise> <!-- when @inline = 1 -->
                  <xsl:attribute name="style:vertical-rel">baseline</xsl:attribute>
                  <xsl:attribute name="style:vertical-pos">top</xsl:attribute>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:element>
          </xsl:element>
        </xsl:for-each>
        <xsl:for-each select="HwpDoc/BodyText/SectionDef//ShapeComponent">
          <xsl:apply-templates select="ShapePicture" mode="style"/>
          <xsl:apply-templates select="ShapeRectangle" mode="style"/>
          <xsl:apply-templates select="ShapeLine" mode="style"/>
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

  <xsl:template match="SectionDef">
    <xsl:apply-templates />
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
          <xsl:when test="$style-parashape-id != $parashape-id or @new-page='1'">
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
    <xsl:element name="table:table">
      <xsl:attribute name="table:style-name">Table-<xsl:value-of select="@table-id + 1"/></xsl:attribute>
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
    </xsl:element>
  </xsl:template>

  <xsl:template match="GShapeObjectControl">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="GShapeObjectControl" mode="style-graphic-properties">
    <!-- 15.27 Frame Formatting Properties -->
    <xsl:element name="style:graphic-properties">
      <!-- 15.27.4 Left and Right Margins -->
      <xsl:attribute name="fo:margin-left"><xsl:value-of select="round(@margin-left div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:attribute name="fo:margin-right"><xsl:value-of select="round(@margin-right div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <!-- 15.27.5 Top and Bottom Margins -->
      <xsl:attribute name="fo:margin-top"><xsl:value-of select="round(@margin-top div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:attribute name="fo:margin-bottom"><xsl:value-of select="round(@margin-bottom div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:choose>
	<xsl:when test="@inline = 0">
	  <!-- 15.27.21 Wrapping -->
	  <xsl:choose>
	    <xsl:when test="@flow = 'float'">
	      <xsl:choose>
		<xsl:when test="@text-side = 'both'">
		  <xsl:attribute name="style:wrap">parallel</xsl:attribute>
		</xsl:when>
		<xsl:when test="@text-side = 'left'">
		  <xsl:attribute name="style:wrap">left</xsl:attribute>
		</xsl:when>
		<xsl:when test="@text-side = 'right'">
		  <xsl:attribute name="style:wrap">right</xsl:attribute>
		</xsl:when>
		<xsl:when test="@text-side = 'larger'">
		  <xsl:attribute name="style:wrap">biggest</xsl:attribute>
		</xsl:when>
	      </xsl:choose>
	    </xsl:when>
	    <xsl:when test="@flow = 'block'">
	      <xsl:attribute name="style:wrap">none</xsl:attribute>
	    </xsl:when>
	    <xsl:when test="@flow = 'back'">
	      <xsl:attribute name="style:wrap">run-through</xsl:attribute>
	    </xsl:when>
	    <xsl:when test="@flow = 'front'">
	      <!-- 해당하는 것이 없음 : 가장 비슷한 run-through를 채택 -->
	      <xsl:attribute name="style:wrap">run-through</xsl:attribute>
	    </xsl:when>
	  </xsl:choose>

	  <xsl:attribute name="style:vertical-rel">
	    <xsl:choose>
	      <xsl:when test="@vrelto = 'page'">
		<xsl:text>page-content</xsl:text>
	      </xsl:when>
	      <xsl:when test="@vrelto = 'paper'">
		<xsl:text>page</xsl:text>
	      </xsl:when>
	      <xsl:when test="@vrelto = 'paragraph'">
		<xsl:text>paragraph</xsl:text>
	      </xsl:when>
	      <xsl:otherwise>
		<xsl:text>paragraph</xsl:text>
	      </xsl:otherwise>
	    </xsl:choose>
	  </xsl:attribute>

	  <xsl:attribute name="style:horizontal-rel">
	    <xsl:choose>
	      <xsl:when test="@hrelto = 'page'">
		<xsl:text>page-content</xsl:text>
	      </xsl:when>
	      <xsl:when test="@hrelto = 'paper'">
		<xsl:text>page</xsl:text>
	      </xsl:when>
	      <xsl:when test="@hrelto = 'column'">
		<!-- TODO -->
		<xsl:text>page-content</xsl:text>
	      </xsl:when>
	      <xsl:otherwise>
		<xsl:text>paragraph</xsl:text>
	      </xsl:otherwise>
	    </xsl:choose>
	  </xsl:attribute>

	  <xsl:attribute name="style:horizontal-pos">
	    <xsl:choose>
	      <xsl:when test="@halign = 'left'">
		<xsl:text>from-left</xsl:text>
	      </xsl:when>
	      <!-- TODO -->
	    </xsl:choose>
	  </xsl:attribute>

	  <xsl:attribute name="style:vertical-pos">
	    <xsl:choose>
	      <xsl:when test="@halign = 'left'">
		<xsl:text>from-top</xsl:text>
	      </xsl:when>
	      <!-- TODO -->
	    </xsl:choose>
	  </xsl:attribute>
	</xsl:when>
	<xsl:otherwise> <!-- when @inline = 1 -->
	  <xsl:attribute name="style:vertical-rel">baseline</xsl:attribute>
	  <xsl:attribute name="style:vertical-pos">top</xsl:attribute>
	</xsl:otherwise>
      </xsl:choose>
      <xsl:for-each select="ShapeComponent">
        <xsl:choose>
          <xsl:when test="@fill-colorpattern = 1">
            <!--
            <xsl:choose>
              <xsl:when test="FillColorPattern/@pattern-type = 'horizontal'"/>
              <xsl:when test="FillColorPattern/@pattern-type = 'vertical'"/>
              <xsl:when test="FillColorPattern/@pattern-type = 'backslash'"/>
              <xsl:when test="FillColorPattern/@pattern-type = 'slash'"/>
              <xsl:when test="FillColorPattern/@pattern-type = 'grid'"/>
              <xsl:when test="FillColorPattern/@pattern-type = 'cross'"/>
              <xsl:otherwise/>
            </xsl:choose>
            -->
            <xsl:attribute name="draw:fill">solid</xsl:attribute>
            <xsl:attribute name="draw:fill-color"><xsl:value-of select="FillColorPattern/@background-color"/></xsl:attribute>
          </xsl:when>
          <!--
          <xsl:when test="@fill-gradation = 1">
            <xsl:attribute name="draw:fill">gradient</xsl:attribute>
          </xsl:when>
          -->
          <xsl:otherwise>
            <xsl:attribute name="draw:fill">none</xsl:attribute>
          </xsl:otherwise>
        </xsl:choose>
	<xsl:for-each select="BorderLine">
	  <xsl:choose>
	    <xsl:when test="@stroke = 'none'">
	      <xsl:attribute name="draw:stroke">none</xsl:attribute>
	    </xsl:when>
	    <xsl:when test="@stroke = 'solid'">
	      <xsl:attribute name="draw:stroke">solid</xsl:attribute>
	    </xsl:when>
	    <xsl:when test="@stroke = 'dashed'">
	      <xsl:attribute name="draw:stroke">dash</xsl:attribute>
	    </xsl:when>
	    <xsl:when test="@stroke = 'dotted'">
	      <xsl:attribute name="draw:stroke">dash</xsl:attribute>
	    </xsl:when>
	    <xsl:otherwise>
	      <xsl:attribute name="draw:stroke">solid</xsl:attribute>
	    </xsl:otherwise>
	  </xsl:choose>
	  <xsl:attribute name="svg:stroke-color">
	    <xsl:value-of select="@color"/>
	  </xsl:attribute>
	  <xsl:attribute name="svg:stroke-width">
	    <xsl:value-of select="round(@width div 7200 * 25.4 * 100) div 100"/><xsl:text>mm</xsl:text>
	  </xsl:attribute>
	</xsl:for-each>
      </xsl:for-each>
    </xsl:element>
  </xsl:template>

  <xsl:template match="GShapeObjectControl/ShapeComponent/ShapePicture" mode="style">
    <xsl:element name="style:style">
      <xsl:attribute name="style:name">ShapePict-<xsl:value-of select="../@shape-id + 1"/></xsl:attribute>
      <xsl:attribute name="style:family">graphic</xsl:attribute>
      <xsl:apply-templates mode="style-graphic-properties" select="../.." />
    </xsl:element>
  </xsl:template>

  <xsl:template match="GShapeObjectControl/ShapeComponent/ShapeRectangle" mode="style">
    <xsl:element name="style:style">
      <xsl:attribute name="style:name">ShapeRect-<xsl:value-of select="../@shape-id + 1"/></xsl:attribute>
      <xsl:attribute name="style:family">graphic</xsl:attribute>
      <xsl:apply-templates mode="style-graphic-properties" select="../.." />
    </xsl:element>
  </xsl:template>

  <xsl:template match="GShapeObjectControl/ShapeComponent/ShapeLine" mode="style">
    <xsl:element name="style:style">
      <xsl:attribute name="style:name">ShapeLine-<xsl:value-of select="../@shape-id + 1"/></xsl:attribute>
      <xsl:attribute name="style:family">graphic</xsl:attribute>
      <xsl:apply-templates mode="style-graphic-properties" select="../.." />
    </xsl:element>
  </xsl:template>

  <!-- ShapeComponent의 transform matrix들로 draw:transform 속성 생성 -->
  <xsl:template name="shapecomponent-transform">
    <xsl:param name="shapecomponent" />
    <xsl:param name="x" />
    <xsl:param name="y" />

    <!-- TODO: 여러 개의 ScaleRotationMatrix가 존재할 때 -->
    <xsl:variable name="scalerot" select="$shapecomponent/Array[@name='scalerotations']/ScaleRotationMatrix[1]"/>
    <xsl:variable name="scaler" select="$scalerot/Matrix[@attribute-name='scaler']"/>
    <xsl:variable name="rotator" select="$scalerot/Matrix[@attribute-name='rotator']"/>
    <xsl:variable name="translator" select="$shapecomponent/Matrix[@attribute-name='translation']"/>
    <xsl:attribute name="draw:transform">

      <!-- 타겟 좌표계에서 ShapeComponent-local 좌표계로 변환 -->
      <xsl:text> translate (</xsl:text>
      <xsl:value-of select="-round($x div 7200 * 25.4 * 100) div 100"/><xsl:text>mm </xsl:text>
      <xsl:value-of select="-round($y div 7200 * 25.4 * 100) div 100"/><xsl:text>mm)</xsl:text>

      <!-- ShapeComponent-local 좌표계 변환: Scaler -->
      <xsl:text> matrix (</xsl:text>
      <xsl:value-of select="$scaler/@a"/><xsl:text> </xsl:text>
      <xsl:value-of select="$scaler/@b"/><xsl:text> </xsl:text>
      <xsl:value-of select="$scaler/@c"/><xsl:text> </xsl:text>
      <xsl:value-of select="$scaler/@d"/><xsl:text> </xsl:text>
      <xsl:value-of select="round($scaler/@e div 7200 * 25.4 * 100) div 100"/><xsl:text>mm </xsl:text>
      <xsl:value-of select="round($scaler/@f div 7200 * 25.4 * 100) div 100"/><xsl:text>mm)</xsl:text>

      <!-- ShapeComponent-local 좌표계 변환: Rotator -->
      <xsl:text> matrix (</xsl:text>
      <xsl:value-of select="$rotator/@a"/><xsl:text> </xsl:text>
      <xsl:value-of select="$rotator/@b"/><xsl:text> </xsl:text>
      <xsl:value-of select="$rotator/@c"/><xsl:text> </xsl:text>
      <xsl:value-of select="$rotator/@d"/><xsl:text> </xsl:text>
      <xsl:value-of select="round($rotator/@e div 7200 * 25.4 * 100) div 100"/><xsl:text>mm </xsl:text>
      <xsl:value-of select="round($rotator/@f div 7200 * 25.4 * 100) div 100"/><xsl:text>mm)</xsl:text>

      <!-- ShapeComponent-local 좌표계 변환: Translator -->
      <xsl:text> matrix (</xsl:text>
      <xsl:value-of select="$translator/@a"/><xsl:text> </xsl:text>
      <xsl:value-of select="$translator/@b"/><xsl:text> </xsl:text>
      <xsl:value-of select="$translator/@c"/><xsl:text> </xsl:text>
      <xsl:value-of select="$translator/@d"/><xsl:text> </xsl:text>
      <xsl:value-of select="round($translator/@e div 7200 * 25.4 * 100) div 100"/><xsl:text>mm </xsl:text>
      <xsl:value-of select="round($translator/@f div 7200 * 25.4 * 100) div 100"/><xsl:text>mm)</xsl:text>

      <!-- ShapeComponent-local 좌표계에서 다시 타겟 좌표계로 변환 -->
      <xsl:text> translate (</xsl:text>
      <xsl:value-of select="round($x div 7200 * 25.4 * 100) div 100"/><xsl:text>mm </xsl:text>
      <xsl:value-of select="round($y div 7200 * 25.4 * 100) div 100"/><xsl:text>mm)</xsl:text>

    </xsl:attribute>
  </xsl:template>

  <xsl:template match="GShapeObjectControl/ShapeComponent/ShapePicture">
    <xsl:variable name="gso" select="../.." />

    <!-- 9.3 Frames -->
    <xsl:element name="draw:frame">
        <!-- common-draw-style-name-attlist -->
	<xsl:attribute name="draw:style-name">ShapePict-<xsl:value-of select="../@shape-id + 1"/></xsl:attribute>
        <!-- common-draw-position-attlist -->
	<xsl:if test="$gso/@inline = 0">
	  <xsl:attribute name="svg:x"><xsl:value-of select="$gso/@x div 100"/>pt</xsl:attribute>
	  <xsl:attribute name="svg:y"><xsl:value-of select="$gso/@y div 100"/>pt</xsl:attribute>
        </xsl:if>
        <!-- common-text-anchor-attlist -->
        <xsl:choose>
	  <xsl:when test="$gso/@inline = 1">
            <xsl:attribute name="text:anchor-type">as-char</xsl:attribute>
          </xsl:when>
          <xsl:otherwise>
            <xsl:attribute name="text:anchor-type">paragraph</xsl:attribute>
          </xsl:otherwise>
        </xsl:choose>
        <!-- common-draw-z-index-attlist -->
	<xsl:attribute name="draw:z-index"><xsl:value-of select="$gso/@z-order"/></xsl:attribute>
        <!-- 15.27.1 Frame Widths -->
        <xsl:choose>
	  <xsl:when test="$gso/@width-relto = 'absolute'">
	    <xsl:attribute name="svg:width"><xsl:value-of select="round($gso/@width div 7200 * 2.54 * 10 * 100) div 100"/>mm</xsl:attribute>
          </xsl:when>
        </xsl:choose>
        <!-- 15.27.2 Frame Heights -->
        <xsl:choose>
	  <xsl:when test="$gso/@height-relto = 'absolute'">
	    <xsl:attribute name="svg:height"><xsl:value-of select="round($gso/@height div 7200 * 2.54 * 10 * 100) div 100"/>mm</xsl:attribute>
          </xsl:when>
        </xsl:choose>

	<xsl:call-template name="shapecomponent-transform">
	  <xsl:with-param name="shapecomponent" select=".." />
	  <xsl:with-param name="x" select="$gso/@x" />
	  <xsl:with-param name="y" select="$gso/@y" />
	</xsl:call-template>

	<xsl:variable name="binpath" select="'bindata/'"/>
	<xsl:variable name="bindataid" select="PictureInfo/@bindata-id"/>
	<xsl:variable name="bindata" select="/HwpDoc/DocInfo/IdMappings/BinData[number($bindataid)]"/>
	<xsl:element name="draw:image">
	    <xsl:choose>
		<xsl:when test="$bindata/@storage = 'embedding'">
		    <xsl:attribute name="xlink:type">simple</xsl:attribute>
		    <xsl:attribute name="xlink:href"><xsl:value-of select="$binpath"/><xsl:value-of select="$bindata/@storage-id"/>.<xsl:value-of select="$bindata/@ext"/></xsl:attribute>
		</xsl:when>
	    </xsl:choose>
	</xsl:element>
    </xsl:element>
  </xsl:template>

  <xsl:template match="GShapeObjectControl/ShapeComponent/ShapeRectangle">

    <!-- 타겟 좌표계에서 이 ShapeComponent의 좌표

    여기(mode="in-gso"에서는 이 ShapeComponent가 GSO 바로 아래에 있으므로
    타겟 좌표계에서 GSO의 좌표가 곧 타겟 좌표계에서 ShapeComponent의 좌표임.

    만약 ShapeComponent가 GSO 바로 아래 있지 않고 ShapeComponent container 밑에
    있다던가 하면 좀 더 정교한 방법이 사용되어야 할 것
    -->
    <xsl:variable name="shapecomponent-x" select="../../@x"/>
    <xsl:variable name="shapecomponent-y" select="../../@y"/>

    <xsl:variable name="width" select="Array/Coord[2]/@x - Array/Coord[1]/@x"/>
    <xsl:variable name="height" select="Array/Coord[3]/@y - Array/Coord[2]/@y"/>
    <xsl:element name="draw:rect">
      <xsl:attribute name="draw:style-name">ShapeRect-<xsl:value-of select="../@shape-id + 1"/></xsl:attribute>
      <!-- TODO -->
      <xsl:attribute name="text:anchor-type">paragraph</xsl:attribute>
      <xsl:attribute name="svg:x"><xsl:value-of select="round($shapecomponent-x div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:attribute name="svg:y"><xsl:value-of select="round($shapecomponent-y div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:attribute name="svg:width"><xsl:value-of select="round($width div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:attribute name="svg:height"><xsl:value-of select="round($height div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>

      <xsl:call-template name="shapecomponent-transform">
	<xsl:with-param name="shapecomponent" select=".." />
	<xsl:with-param name="x" select="$shapecomponent-x" />
	<xsl:with-param name="y" select="$shapecomponent-y" />
      </xsl:call-template>

      <xsl:for-each select="../TextboxParagraphList">
        <xsl:apply-templates />
      </xsl:for-each>
    </xsl:element>
  </xsl:template>

  <xsl:template match="GShapeObjectControl/ShapeComponent/ShapeLine">
    <xsl:variable name="gso" select="../.."/>
    <xsl:variable name="x1" select="$gso/@x"/>
    <xsl:variable name="y1" select="$gso/@y"/>
    <xsl:variable name="cx" select="../Coord[@attribute-name='rotation_center']/@x"/>
    <xsl:variable name="cy" select="../Coord[@attribute-name='rotation_center']/@y"/>
    <xsl:variable name="x2" select="$x1 + 2 * $cx"/>
    <xsl:variable name="y2" select="$y1 + 2 * $cy"/>
    <xsl:element name="draw:line">
      <xsl:attribute name="svg:x1"><xsl:value-of select="round($x1 div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:attribute name="svg:y1"><xsl:value-of select="round($y1 div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:attribute name="svg:x2"><xsl:value-of select="round($x2 div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:attribute name="svg:y2"><xsl:value-of select="round($y2 div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <!-- TODO -->
      <xsl:attribute name="text:anchor-type">paragraph</xsl:attribute>
      <xsl:attribute name="draw:style-name">ShapeLine-<xsl:value-of select="../@shape-id + 1"/></xsl:attribute>
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>
