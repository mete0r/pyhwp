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
    <xsl:apply-templates mode="office:document-styles" select="/HwpDoc" />
  </xsl:template>

  <xsl:template mode="office:document-styles" match="HwpDoc">
    <office:document-styles office:version="1.2" grddl:transformation="http://docs.oasis-open.org/office/1.2/xslt/odf2rdf.xsl">
      <xsl:apply-templates mode="office:font-face-decls" select="DocInfo" />
      <xsl:apply-templates mode="office:styles" select="DocInfo" />
      <office:automatic-styles>
        <xsl:apply-templates mode="style:page-layout" select="BodyText/SectionDef" />
      </office:automatic-styles>
      <xsl:apply-templates mode="office:master-styles" select="." />
    </office:document-styles>
  </xsl:template>

  <xsl:template mode="office:font-face-decls" match="DocInfo">
    <office:font-face-decls>
      <style:font-face style:name="serif" svg:font-family="'Times New Roman'" style:font-family-generic="roman" style:font-pitch="variable"/>
      <style:font-face style:name="sans-serif" svg:font-family="'Arial'" style:font-family-generic="swiss" style:font-pitch="variable"/>
      <style:font-face style:name="명조" svg:font-family="'은 바탕'" style:font-family-generic="roman" style:font-pitch="variable"/>
      <style:font-face style:name="고딕" svg:font-family="'은 돋움'" style:font-family-generic="swiss" style:font-pitch="variable"/>
      <style:font-face style:name="Lohit Hindi" svg:font-family="'Lohit Hindi'" style:font-family-generic="system" style:font-pitch="variable"/>
      <xsl:apply-templates mode="style:font-face" select="IdMappings/FaceName" />
    </office:font-face-decls>
  </xsl:template>

  <xsl:template mode="office:styles" match="DocInfo">
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

      <xsl:apply-templates mode="style:style" select="IdMappings/Style" />
    </office:styles>
  </xsl:template>

  <xsl:template mode="office:master-styles" match="HwpDoc">
    <!--
    3.15.4 http://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html#element-office_master-styles

    Elements:
      <draw:layer-set> 10.2.2
      <style:handout-master> 10.2.1
      <style:master-page> 16.9.
    -->
    <office:master-styles>
      <xsl:for-each select="BodyText/SectionDef">
        <xsl:element name="style:master-page">
          <xsl:attribute name="style:name">MasterPage-<xsl:value-of select="@section-id + 1"/></xsl:attribute>
          <xsl:attribute name="style:page-layout-name">PageLayout-<xsl:value-of select="@section-id + 1"/></xsl:attribute>
        </xsl:element>
      </xsl:for-each>
    </office:master-styles>
  </xsl:template>

  <xsl:template mode="style:font-face" match="FaceName">
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

  <xsl:template mode="style:style" match="Style">
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
      <xsl:variable name="charshapes" select="/HwpDoc/DocInfo/IdMappings/CharShape" />
      <xsl:variable name="charshape" select="$charshapes[number($charshapeid)]"/>
      <xsl:apply-templates mode="style:paragraph-properties" select="." />
      <xsl:apply-templates select="$charshape" mode="style:text-properties" />
    </xsl:element>
  </xsl:template>

  <xsl:template mode="style:page-layout" match="SectionDef">
    <xsl:element name="style:page-layout">
      <!--
      16.5 http://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html#element-style_page-layout

      Attributes:
        style:name 19.498.2
        style:page-usage 19.505.
      Elements:
        <style:footer-style> 16.7
        <style:header-style> 16.6
        <style:page-layout-properties> 17.2
      -->
      <xsl:attribute name="style:name">PageLayout-<xsl:value-of select="@section-id + 1"/></xsl:attribute>
      <xsl:apply-templates mode="style:page-layout-properties" select="PageDef" />
      <style:header-style/>
      <style:footer-style/>
    </xsl:element>
  </xsl:template>

  <xsl:template mode="style:page-layout-properties" match="PageDef">
    <xsl:element name="style:page-layout-properties">
      <!--
      17.2 http://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html#element-style_page-layout-properties

      Attributes:
        fo:background-color 20.175
        fo:border 20.176.2
        fo:border-bottom 20.176.3
        fo:border-left 20.176.4
        fo:border-right 20.176.5
        fo:border-top 20.176.6
        fo:margin 20.198
        fo:margin-bottom 20.199
        fo:margin-left 20.200
        fo:margin-right 20.201
        fo:margin-top 20.202
        fo:padding 20.210
        fo:padding-bottom 20.211
        fo:padding-left 20.212
        fo:padding-right 20.213
        fo:padding-top 20.214
        fo:page-height 20.208
        fo:page-width 20.209
        style:border-line-width 20.241
        style:border-line-width-bottom 20.242
        style:border-line-width-left 20.243
        style:border-line-width-right 20.244
        style:border-line-width-top 20.245
        style:first-page-number 20.258
        style:footnote-max-height 20.288
        style:layout-grid-base-height 20.296
        style:layout-grid-base-width 20.297
        style:layout-grid-color 20.298
        style:layout-grid-display 20.299
        style:layout-grid-lines 20.300
        style:layout-grid-mode 20.301
        style:layout-grid-print 20.302
        style:layout-grid-ruby-below 20.303
        style:layout-grid-ruby-height 20.304
        style:layout-grid-snap-to 20.305
        style:layout-grid-standard-mode 20.306
        style:num-format 20.314
        style:num-letter-sync 20.315
        style:num-prefix 20.316
        style:num-suffix 20.317
        style:paper-tray-name 20.321
        style:print 20.322
        style:print-orientation 20.325
        style:print-page-order 20.324
        style:register-truth-ref-style-name 20.329
        style:scale-to 20.344
        style:scale-to-pages 20.345
        style:shadow 20.349
        style:table-centering 20.353
        style:writing-mode 20.394.3
      Elements:
        <style:background-image> 17.3
        <style:columns> 17.12
        <style:footnote-sep> 17.4.
      -->
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
  </xsl:template>

  <xsl:template mode="style:paragraph-properties" match="Style">
    <xsl:variable name="parashapeid" select="@parashape-id + 1"/>
    <xsl:variable name="parashapes" select="/HwpDoc/DocInfo/IdMappings/ParaShape" />
    <xsl:variable name="parashape" select="$parashapes[number($parashapeid)]"/>
    <xsl:element name="style:paragraph-properties">
      <xsl:apply-templates mode="style-paragraph-properties-common" select="$parashape" />
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>
