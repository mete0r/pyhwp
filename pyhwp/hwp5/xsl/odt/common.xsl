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

  <xsl:template mode="style-paragraph-properties-common" match="ParaShape">
    <!--
    17.6
    http://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html#element-style_paragraph-properties

    Attributes:
      fo:background-color 20.175
      fo:border 20.176.2
      fo:border-bottom 20.176.3
      fo:border-left 20.176.4
      fo:border-right 20.176.5
      fo:border-top 20.176.6
      fo:break-after 20.177
      fo:break-before 20.178
      fo:hyphenation-keep 20.189
      fo:hyphenation-ladder-count 20.190
      fo:keep-together 20.193
      fo:keep-with-next 20.194
      fo:line-height 20.197
      fo:margin 20.198
      fo:margin-bottom 20.199
      fo:margin-left 20.200
      fo:margin-right 20.201
      fo:margin-top 20.202
      fo:orphans 20.207
      fo:padding 20.210
      fo:padding-bottom 20.211
      fo:padding-left 20.212
      fo:padding-right 20.213
      fo:padding-top 20.214
      fo:text-align 20.216.1
      fo:text-align-last 20.217
      fo:text-indent 20.218
      fo:widows 20.221
      style:auto-text-indent 20.239
      style:background-transparency 20.240
      style:border-line-width 20.241
      style:border-line-width-bottom 20.242
      style:border-line-width-left 20.243
      style:border-line-width-right 20.244
      style:border-line-width-top 20.245
      style:font-independent-line-spacing 20.268
      style:join-border 20.292
      style:justify-single-word 20.293
      style:line-break 20.307
      style:line-height-at-least 20.309
      style:line-spacing 20.310
      style:page-number 20.320
      style:punctuation-wrap 20.327
      style:register-true 20.328
      style:shadow 20.349
      style:snap-to-layout-grid 20.351
      style:tab-stop-distance 20.352
      style:text-autospace 20.355
      style:vertical-align 20.386.1
      style:writing-mode 20.394.4
      style:writing-mode-automatic 20.395
      text:line-number 20.420
      text:number-lines 20.424.
    Elements:
      <style:background-image> 17.3
      <style:drop-cap> 17.9
      <style:tab-stops> 17.7
    -->
    <xsl:attribute name="fo:text-align">
      <xsl:choose>
        <xsl:when test="@align = 'both'">justify</xsl:when>
        <xsl:when test="@align = 'left'">left</xsl:when>
        <xsl:when test="@align = 'right'">right</xsl:when>
        <xsl:when test="@align = 'center'">center</xsl:when>
        <xsl:when test="@align = 'distribute'">justify</xsl:when>
        <xsl:when test="@align = 'distribute_space'">justify</xsl:when>
        <xsl:otherwise>justify</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
    <xsl:variable name="margin-left" select="number(@doubled-margin-left)"/>
    <xsl:variable name="indent" select="number(@indent)"/>
    <xsl:attribute name="fo:text-indent"><xsl:value-of select="$indent div 200"/>pt</xsl:attribute>
    <xsl:attribute name="fo:margin-left">
      <xsl:choose>
        <xsl:when test="$indent &lt; 0"><xsl:value-of select="($margin-left - $indent) div 200"/>pt</xsl:when>
        <xsl:otherwise><xsl:value-of select="$margin-left div 200"/>pt</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
    <xsl:attribute name="fo:margin-right"><xsl:value-of select="number(@doubled-margin-right) div 200"/>pt</xsl:attribute>
    <xsl:attribute name="fo:margin-top"><xsl:value-of select="number(@doubled-margin-top) div 200"/>pt</xsl:attribute>
    <xsl:attribute name="fo:margin-bottom"><xsl:value-of select="number(@doubled-margin-bottom) div 200"/>pt</xsl:attribute>
    <!--
      줄 간격

      전반적으로 글자를 줄 내에서 수직 배치하는 방식에서 차이가 있는 것 같다.
      hwp5의 줄 간격 관련 속성을 odt에 있는 비슷한 속성으로 단순 변환하는
      것만으로는 꽤 차이가 나며, 아래와 같이 좀 더 부가적인 조정을 하더라도
      여전히 미묘한 차이가 생긴다.

      이러한 상황을 개선하기 위해선 폰트의 metric에 대한 이해가 선행되어야 할
      것으로 보인다. (아마도 폰트의 leading 값과 관련있는 것으로 추측된다.)

      samples/linespacing.hwp로 비교해볼 수 있다.
    -->
    <xsl:choose>
      <!--
        줄 간격: 글자에 따라

        폰트 크기에 지정된 비율을 적용한 값을 줄의 높이로 설정하기 위해,
        fo:line-height을 사용한다.

        NOTE: 같은 폰트 크기/비율을 지정해도 libreoffice에서는 줄 간격이 좀
        더 넓게 나타난다. (samples/linespacing.hwp의 "글자에 따라 100%"를 ODT
        변환 후와 비교) 이는 아마도 비율을 적용할 때 폰트의 leading에 대한
        처리방식이 다르기 때문이 아닐까 한다. (hwp5는 폰트의 em-box 크기만을
        고려하는 듯 하며, libreoffice는 여기에 아마도 폰트의 leading을
        포함시키는 듯 하다.
      -->
      <xsl:when test="@linespacing-type = 'ratio'">
        <xsl:attribute name="fo:line-height"><xsl:value-of select="number(@linespacing)"/>%</xsl:attribute>
      </xsl:when>
      <!--
        줄 간격: 고정 값

        지정된 값을 fo:line-height로 적용한다.

        NOTE: hwp5에서는 글자를 줄 공간의 위 (또는 위에 가깝게) 배치하는
        반면, libreoffice에서는 기본적으로 줄 공간의 아래에 가깝게
        배치한다(baseline 정렬). 따라서 추가적으로 style:vertical-align을
        top으로 지정하였다.

        그래도 여전히 미묘한 차이가 발생하는데, samples/linespacing.hwp의 맨
        위 'HHHH..' 블럭과 '고정 값 100%'를 각각 ODT 변환 후와 비교해보면,
        libreoffice의 경우 'HHHH..' 블럭은 거의 비슷하게 나타나는 반면 '고정
        값 100%'는 줄의 아래 부분이 잘린 채 나타난다. 이는 한글 문자의 윗
        부분에 약간의 공백을 좀 더 들어가면서 전체적으로 줄 공간 내에서
        글자들이 약간 아래로 밀려나기 때문으로 보인다.
      -->
      <xsl:when test="@linespacing-type = 'fixed'">
        <xsl:attribute name="fo:line-height"><xsl:value-of select="number(@linespacing) div 200"/>pt</xsl:attribute>
        <xsl:attribute name="style:vertical-align">top</xsl:attribute>
      </xsl:when>
      <!--
        줄 간격: 여백만 지정

        지정된 값을 style:line-spacing에 적용한다.

        NOTE: style:line-spacing은 글자의 위/아래에 지정된 공간을 배치한다.
        따라서 hwp5에서 지정된 값을 반으로 나누어 적용하였다.  그래도 미묘한
        차이가 나는 데, samples/linespacing.hwp의 "여백만 지정 20pt"를
        선택/반전하여 보면, hwp5는 글자(와 윗줄)이 줄 공간의 맨 위에 거의 딱
        붙어 배치되는데 반해, libreoffice에서는 약간의 공간이 더 들어간다.
      -->
      <xsl:when test="@linespacing-type = 'spaceonly'">
        <xsl:attribute name="style:line-spacing"><xsl:value-of select="number(@linespacing) div 200 div 2"/>pt</xsl:attribute>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template mode="style:text-properties" match="CharShape">
    <xsl:element name="style:text-properties">

      <xsl:apply-templates mode="style:font-name" select="FontFace" />
      <xsl:apply-templates mode="style:font-name-asian" select="FontFace" />

      <xsl:apply-templates mode="fo:font-size" select="." />
      <xsl:apply-templates mode="style:font-size-asian" select="." />
      <xsl:apply-templates mode="style:font-size-complex" select="." />

      <!-- 15.4.25 Font Style -->
      <xsl:apply-templates mode="fo:font-style" select="." />
      <xsl:apply-templates mode="style:font-style-asian" select="." />
      <xsl:apply-templates mode="style:font-style-complex" select="." />

      <!-- 15.4.28 Underlining Type -->
      <!-- 15.4.31 Underline Color -->
      <xsl:apply-templates mode="style:text-underline" select="." />
      <xsl:apply-templates mode="style:text-overline" select="." />
      <xsl:apply-templates mode="style:text-line-through" select="." />
      <!-- 15.4.32 Font Weight -->
      <xsl:apply-templates mode="fo:font-weight" select="." />
      <xsl:apply-templates mode="style:font-weight-asian" select="." />
      <xsl:apply-templates mode="style:font-weight-complex" select="." />
    </xsl:element>
  </xsl:template>

  <xsl:template mode="style:font-name" match="FontFace">
    <xsl:variable name="facename-en-id" select="@en + 1"/>
    <xsl:apply-templates mode="style:font-name" select="//FaceName[$facename-en-id]" />
  </xsl:template>

  <xsl:template mode="style:font-name" match="FaceName">
    <xsl:attribute name="style:font-name"><xsl:value-of select="@name"/></xsl:attribute>
  </xsl:template>

  <xsl:template mode="style:font-name-asian" match="FontFace">
    <xsl:variable name="facename-ko-id" select="@ko + 1"/>
    <xsl:apply-templates mode="style:font-name-asian" select="//FaceName[$facename-ko-id]" />
  </xsl:template>

  <xsl:template mode="style:font-name-asian" match="FaceName">
    <xsl:attribute name="style:font-name-asian"><xsl:value-of select="@name"/></xsl:attribute>
  </xsl:template>

  <xsl:template mode="fo:font-size" match="CharShape">
    <xsl:attribute name="fo:font-size">
      <!-- @en 값이 western language를 대표 -->
      <xsl:value-of select="@basesize * RelativeSize/@en div 100 div 100"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:template>

  <xsl:template mode="style:font-size-asian" match="CharShape">
    <xsl:attribute name="style:font-size-asian">
      <!-- @ko 값이 asian language를 대표 -->
      <xsl:value-of select="@basesize * RelativeSize/@ko div 100 div 100"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:template>

  <xsl:template mode="style:font-size-complex" match="CharShape">
    <xsl:attribute name="style:font-size-complex">
      <!-- @otheer 값이 complex language를 대표 -->
      <xsl:value-of select="@basesize * RelativeSize/@other div 100 div 100"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:template>

  <xsl:template mode="fo:font-style" match="CharShape">
    <xsl:if test="@italic = 1">
      <xsl:attribute name="fo:font-style">italic</xsl:attribute>
    </xsl:if>
  </xsl:template>

  <xsl:template mode="style:font-style-asian" match="CharShape">
    <xsl:if test="@italic = 1">
      <xsl:attribute name="style:font-style-asian">italic</xsl:attribute>
    </xsl:if>
  </xsl:template>

  <xsl:template mode="style:font-style-complex" match="CharShape">
    <xsl:if test="@italic = 1">
      <xsl:attribute name="style:font-style-complex">italic</xsl:attribute>
    </xsl:if>
  </xsl:template>

  <xsl:template mode="fo:font-weight" match="CharShape">
    <xsl:if test="@bold = 1">
      <xsl:attribute name="fo:font-weight">bold</xsl:attribute>
    </xsl:if>
  </xsl:template>

  <xsl:template mode="style:font-weight-asian" match="CharShape">
    <xsl:if test="@bold = 1">
      <xsl:attribute name="style:font-weight-asian">bold</xsl:attribute>
    </xsl:if>
  </xsl:template>

  <xsl:template mode="style:font-weight-complex" match="CharShape">
    <xsl:if test="@bold = 1">
      <xsl:attribute name="style:font-weight-complex">bold</xsl:attribute>
    </xsl:if>
  </xsl:template>

  <xsl:template mode="style:text-underline" match="CharShape">
    <xsl:choose>
      <xsl:when test="@underline = 'underline'">
        <xsl:attribute name="style:text-underline-type">single</xsl:attribute>
        <xsl:attribute name="style:text-underline-style">solid</xsl:attribute>
        <xsl:attribute name="style:text-underline-width">auto</xsl:attribute>
        <xsl:attribute name="style:text-underline-color">
          <xsl:value-of select="@underline-color"/>
        </xsl:attribute>
      </xsl:when>
      <xsl:otherwise>
        <xsl:attribute name="style:text-underline-type">none</xsl:attribute>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template mode="style:text-overline" match="CharShape">
    <xsl:choose>
      <xsl:when test="@underline = 'upperline'">
        <xsl:attribute name="style:text-overline-type">single</xsl:attribute>
        <xsl:attribute name="style:text-overline-style">solid</xsl:attribute>
        <xsl:attribute name="style:text-overline-width">auto</xsl:attribute>
        <xsl:attribute name="style:text-overline-color">
          <xsl:value-of select="@underline-color"/>
        </xsl:attribute>
      </xsl:when>
      <xsl:otherwise>
        <xsl:attribute name="style:text-overline-type">none</xsl:attribute>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template mode="style:text-line-through" match="CharShape">
    <xsl:choose>
      <xsl:when test="@underline = 'unknown'">
        <xsl:attribute name="style:text-line-through-type">single</xsl:attribute>
        <xsl:attribute name="style:text-line-through-style">solid</xsl:attribute>
        <xsl:attribute name="style:text-line-through-width">auto</xsl:attribute>
        <xsl:attribute name="style:text-line-through-color">
          <xsl:value-of select="@underline-color"/>
        </xsl:attribute>
      </xsl:when>
      <xsl:otherwise>
        <xsl:attribute name="style:text-line-through-type">none</xsl:attribute>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
