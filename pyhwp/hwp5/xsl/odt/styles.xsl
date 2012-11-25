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
  <xsl:import href="common.xsl" />
  <xsl:output method="xml" encoding="utf-8" indent="yes" />
  <xsl:template match="/">
    <office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
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
      <office:font-face-decls>
        <style:font-face style:name="serif" svg:font-family="'Times New Roman'" style:font-family-generic="roman" style:font-pitch="variable"/>
        <style:font-face style:name="sans-serif" svg:font-family="'Arial'" style:font-family-generic="swiss" style:font-pitch="variable"/>
        <style:font-face style:name="명조" svg:font-family="'은 바탕'" style:font-family-generic="roman" style:font-pitch="variable"/>
        <style:font-face style:name="고딕" svg:font-family="'은 돋움'" style:font-family-generic="swiss" style:font-pitch="variable"/>
        <style:font-face style:name="Lohit Hindi" svg:font-family="'Lohit Hindi'" style:font-family-generic="system" style:font-pitch="variable"/>
        <xsl:for-each select="HwpDoc/DocInfo">
          <xsl:apply-templates select="IdMappings/FaceName" />
        </xsl:for-each>
      </office:font-face-decls>
      <office:styles>
        <style:default-style style:family="graphic">
          <style:graphic-properties draw:shadow-offset-x="0.3cm" draw:shadow-offset-y="0.3cm" draw:start-line-spacing-horizontal="0.283cm" draw:start-line-spacing-vertical="0.283cm" draw:end-line-spacing-horizontal="0.283cm" draw:end-line-spacing-vertical="0.283cm" style:flow-with-text="false"/>
          <style:paragraph-properties style:text-autospace="ideograph-alpha" style:line-break="strict" style:writing-mode="lr-tb" style:font-independent-line-spacing="false">
            <style:tab-stops/>
          </style:paragraph-properties>
          <style:text-properties style:use-window-font-color="true" fo:font-size="10pt" fo:language="en" fo:country="US" style:letter-kerning="true" style:font-size-asian="10pt" style:language-asian="ko" style:country-asian="KR" style:font-size-complex="10pt" style:language-complex="hi" style:country-complex="IN"/>
        </style:default-style>
        <style:default-style style:family="paragraph">
          <style:paragraph-properties fo:hyphenation-ladder-count="no-limit" style:text-autospace="ideograph-alpha" style:punctuation-wrap="hanging" style:line-break="strict" style:tab-stop-distance="1.251cm" style:writing-mode="page"/>
          <style:text-properties style:use-window-font-color="true" style:font-name="sans-serif" fo:font-size="10pt" fo:language="en" fo:country="US" style:letter-kerning="true" style:font-name-asian="고딕" style:font-size-asian="10pt" style:language-asian="ko" style:country-asian="KR" style:font-name-complex="Lohit Hindi" style:font-size-complex="10pt" style:language-complex="hi" style:country-complex="IN" fo:hyphenate="false" fo:hyphenation-remain-char-count="2" fo:hyphenation-push-char-count="2"/>
        </style:default-style>
        <style:default-style style:family="table">
          <style:table-properties table:border-model="collapsing"/>
        </style:default-style>
        <style:default-style style:family="table-row">
          <style:table-row-properties fo:keep-together="auto"/>
        </style:default-style>
        <style:style style:name="Standard" style:family="paragraph" style:class="text">
          <style:paragraph-properties style:text-autospace="none"/>
        </style:style>
        <style:style style:name="Heading" style:family="paragraph" style:parent-style-name="Standard" style:next-style-name="Text_20_body" style:class="text">
          <style:paragraph-properties fo:margin-top="0.423cm" fo:margin-bottom="0.212cm" fo:keep-with-next="always"/>
          <style:text-properties style:font-name="sans-serif" fo:font-size="14pt" style:font-name-asian="고딕" style:font-size-asian="14pt" style:font-name-complex="Lohit Hindi" style:font-size-complex="14pt"/>
        </style:style>
        <style:style style:name="Text_20_body" style:display-name="Text body" style:family="paragraph" style:parent-style-name="Standard" style:class="text">
          <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0.212cm"/>
        </style:style>
        <style:style style:name="List" style:family="paragraph" style:parent-style-name="Text_20_body" style:class="list">
          <style:text-properties/>
        </style:style>
        <style:style style:name="Caption" style:family="paragraph" style:parent-style-name="Standard" style:class="extra">
          <style:paragraph-properties fo:margin-top="0.212cm" fo:margin-bottom="0.212cm" text:number-lines="false" text:line-number="0"/>
          <style:text-properties fo:font-size="12pt" fo:font-style="italic" style:font-size-asian="12pt" style:font-style-asian="italic" style:font-size-complex="12pt" style:font-style-complex="italic"/>
        </style:style>
        <style:style style:name="Index" style:family="paragraph" style:parent-style-name="Standard" style:class="index">
          <style:paragraph-properties text:number-lines="false" text:line-number="0"/>
          <style:text-properties/>
        </style:style>
        <style:style style:name="Table_20_Contents" style:display-name="Table Contents" style:family="paragraph" style:parent-style-name="Standard" style:class="extra">
          <style:paragraph-properties text:number-lines="false" text:line-number="0"/>
        </style:style>
        <style:style style:name="Graphics" style:family="graphic">
          <style:graphic-properties text:anchor-type="paragraph" svg:x="0cm" svg:y="0cm" style:wrap="dynamic" style:number-wrapped-paragraphs="no-limit" style:wrap-contour="false" style:vertical-pos="top" style:vertical-rel="paragraph" style:horizontal-pos="center" style:horizontal-rel="paragraph"/>
        </style:style>
        <text:outline-style style:name="Outline">
          <text:outline-level-style text:level="1" style:num-format="">
            <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
              <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="0.762cm" fo:text-indent="-0.762cm" fo:margin-left="0.762cm"/>
            </style:list-level-properties>
          </text:outline-level-style>
          <text:outline-level-style text:level="2" style:num-format="">
            <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
              <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="1.016cm" fo:text-indent="-1.016cm" fo:margin-left="1.016cm"/>
            </style:list-level-properties>
          </text:outline-level-style>
          <text:outline-level-style text:level="3" style:num-format="">
            <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
              <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="1.27cm" fo:text-indent="-1.27cm" fo:margin-left="1.27cm"/>
            </style:list-level-properties>
          </text:outline-level-style>
          <text:outline-level-style text:level="4" style:num-format="">
            <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
              <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="1.524cm" fo:text-indent="-1.524cm" fo:margin-left="1.524cm"/>
            </style:list-level-properties>
          </text:outline-level-style>
          <text:outline-level-style text:level="5" style:num-format="">
            <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
              <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="1.778cm" fo:text-indent="-1.778cm" fo:margin-left="1.778cm"/>
            </style:list-level-properties>
          </text:outline-level-style>
          <text:outline-level-style text:level="6" style:num-format="">
            <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
              <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="2.032cm" fo:text-indent="-2.032cm" fo:margin-left="2.032cm"/>
            </style:list-level-properties>
          </text:outline-level-style>
          <text:outline-level-style text:level="7" style:num-format="">
            <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
              <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="2.286cm" fo:text-indent="-2.286cm" fo:margin-left="2.286cm"/>
            </style:list-level-properties>
          </text:outline-level-style>
          <text:outline-level-style text:level="8" style:num-format="">
            <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
              <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="2.54cm" fo:text-indent="-2.54cm" fo:margin-left="2.54cm"/>
            </style:list-level-properties>
          </text:outline-level-style>
          <text:outline-level-style text:level="9" style:num-format="">
            <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
              <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="2.794cm" fo:text-indent="-2.794cm" fo:margin-left="2.794cm"/>
            </style:list-level-properties>
          </text:outline-level-style>
          <text:outline-level-style text:level="10" style:num-format="">
            <style:list-level-properties text:list-level-position-and-space-mode="label-alignment">
              <style:list-level-label-alignment text:label-followed-by="listtab" text:list-tab-stop-position="3.048cm" fo:text-indent="-3.048cm" fo:margin-left="3.048cm"/>
            </style:list-level-properties>
          </text:outline-level-style>
        </text:outline-style>
        <text:notes-configuration text:note-class="footnote" style:num-format="1" text:start-value="0" text:footnotes-position="page" text:start-numbering-at="document"/>
        <text:notes-configuration text:note-class="endnote" style:num-format="i" text:start-value="0"/>
        <text:linenumbering-configuration text:number-lines="false" text:offset="0.499cm" style:num-format="1" text:number-position="left" text:increment="5"/>

        <xsl:for-each select="HwpDoc/DocInfo">
          <xsl:apply-templates select="IdMappings/Style" />
        </xsl:for-each>
      </office:styles>
      <office:automatic-styles>
        <xsl:for-each select="/HwpDoc/BodyText/SectionDef/PageDef">
          <xsl:element name="style:page-layout">
            <xsl:attribute name="style:name">PageLayout-<xsl:value-of select="../@section-id + 1"/></xsl:attribute>
            <xsl:element name="style:page-layout-properties">
              <xsl:attribute name="style:print-orientation"><xsl:value-of select="@orientation"/></xsl:attribute>
              <xsl:choose>
                <xsl:when test="@orientation = 'portrait'">
                  <xsl:attribute name="fo:page-width"><xsl:value-of select="round(number(@width) div 7200 * 2.54 * 100) div 100"/>cm</xsl:attribute>
                  <xsl:attribute name="fo:page-height"><xsl:value-of select="round(number(@height) div 7200 * 2.54 * 100) div 100"/>cm</xsl:attribute>
                </xsl:when>
                <xsl:when test="@orientation = 'landscape'">
                  <xsl:attribute name="fo:page-width"><xsl:value-of select="round(number(@height) div 7200 * 2.54 * 100) div 100"/>cm</xsl:attribute>
                  <xsl:attribute name="fo:page-height"><xsl:value-of select="round(number(@width) div 7200 * 2.54 * 100) div 100"/>cm</xsl:attribute>
                </xsl:when>
              </xsl:choose>
              <xsl:attribute name="fo:margin-top"><xsl:value-of select="round(number(@top-offset) div 7200 * 2.54 * 100) div 100"/>cm</xsl:attribute>
              <xsl:attribute name="fo:margin-left"><xsl:value-of select="round(number(@left-offset) div 7200 * 2.54 * 100) div 100"/>cm</xsl:attribute>
              <xsl:attribute name="fo:margin-right"><xsl:value-of select="round(number(@right-offset) div 7200 * 2.54 * 100) div 100"/>cm</xsl:attribute>
              <xsl:attribute name="fo:margin-bottom"><xsl:value-of select="round(number(@bottom-offset) div 7200 * 2.54 * 100) div 100"/>cm</xsl:attribute>
              <style:footnote-sep style:width="0.018cm" style:distance-before-sep="0.101cm" style:distance-after-sep="0.101cm" style:adjustment="left" style:rel-width="25%" style:color="#000000"/>
            </xsl:element>
            <style:header-style/>
            <style:footer-style/>
          </xsl:element>
        </xsl:for-each>
      </office:automatic-styles>
      <office:master-styles>
        <xsl:for-each select="/HwpDoc/BodyText/SectionDef/PageDef">
          <xsl:element name="style:master-page">
            <xsl:attribute name="style:name">MasterPage-<xsl:value-of select="../@section-id + 1"/></xsl:attribute>
            <xsl:attribute name="style:page-layout-name">PageLayout-<xsl:value-of select="../@section-id + 1"/></xsl:attribute>
          </xsl:element>
        </xsl:for-each>
      </office:master-styles>
    </office:document-styles>
  </xsl:template>

  <xsl:template match="FaceName">
    <xsl:element name="style:font-face">
      <xsl:attribute name="style:name"><xsl:value-of select="@name"/></xsl:attribute>
      <xsl:attribute name="svg:font-family">'<xsl:value-of select="@name"/>'</xsl:attribute>
      <!-- Panose1/@serif-style -->
      <!-- 2..10 : serif(roman) -->
      <!-- 11~15 : sans-serif(swiss) -->
      <xsl:attribute name="style:font-family-generic">
        <xsl:choose>
          <xsl:when test="Panose1/@serif-style &lt; 11"><xsl:text>roman</xsl:text></xsl:when>
          <xsl:when test="Panose1/@serif-style &gt;= 11"><xsl:text>swiss</xsl:text></xsl:when>
        </xsl:choose>
      </xsl:attribute>
      <!-- TODO: Panose1/@proportion -->
      <xsl:attribute name="style:font-pitch">variable</xsl:attribute>
    </xsl:element>
  </xsl:template>

  <xsl:template match="Style">
    <xsl:element name="style:style">
      <xsl:attribute name="style:name"><xsl:value-of select="translate(@local-name, ' ', '_')" /></xsl:attribute>
      <!--
      <xsl:attribute name="style:parent-style-name"/>
      -->
      <xsl:variable name="styles" select="/HwpDoc/DocInfo/IdMappings/Style" />
      <xsl:variable name="next-style-id" select="@next-style-id + 1"/>
      <xsl:attribute name="style:next-style-name"><xsl:value-of select="translate($styles[$next-style-id]/@local-name, ' ', '_')" /></xsl:attribute>
      <xsl:attribute name="style:family">paragraph</xsl:attribute>
      <xsl:attribute name="style:class">text</xsl:attribute>
      <xsl:variable name="charshapeid" select="@charshape-id + 1"/>
      <xsl:variable name="parashapeid" select="@parashape-id + 1"/>
      <xsl:variable name="charshapes" select="/HwpDoc/DocInfo/IdMappings/CharShape" />
      <xsl:variable name="parashapes" select="/HwpDoc/DocInfo/IdMappings/ParaShape" />
      <xsl:variable name="charshape" select="$charshapes[number($charshapeid)]"/>
      <xsl:variable name="parashape" select="$parashapes[number($parashapeid)]"/>
      <xsl:element name="style:paragraph-properties">
      <xsl:call-template name="parashape-to-paragraph-properties">
        <xsl:with-param name="parashape" select="$parashape"/>
      </xsl:call-template>
      </xsl:element>
      <xsl:apply-templates select="$charshape" mode="style:text-properties" />
    </xsl:element>
  </xsl:template>
</xsl:stylesheet>
