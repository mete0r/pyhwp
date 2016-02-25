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
  xmlns:css3t="http://www.w3.org/TR/css3-text/">
  <xsl:output method="xml" encoding="utf-8" indent="yes" />

  <xsl:template mode="office:document" match="HwpDoc">
    <office:document
      office:version="1.2"
      office:mimetype="application/vnd.oasis.opendocument.text"
      grddl:transformation="http://docs.oasis-open.org/office/1.2/xslt/odf2rdf.xsl">
      <office:scripts/>
      <xsl:apply-templates mode="office:font-face-decls" select="DocInfo" />
      <xsl:apply-templates mode="office:styles" select="DocInfo" />
      <office:automatic-styles>
        <xsl:apply-templates mode="style:page-layout" select="BodyText/SectionDef" />
        <xsl:apply-templates mode="style-style-for-paragraph-and-text" select="//Paragraph" />
        <xsl:apply-templates mode="style:style" select="//TableControl" />
        <xsl:apply-templates mode="style-style-for-table-cells" select="//TableControl" />
        <xsl:apply-templates mode="style:style" select="//ShapeComponent" />
      </office:automatic-styles>
      <xsl:apply-templates mode="office:master-styles" select="." />

      <xsl:apply-templates mode="office:body" select="BodyText" />
    </office:document>
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

  <xsl:template mode="make-style-name" match="Style">
    <xsl:call-template name="make-ncname">
      <xsl:with-param name="str" select="@local-name" />
    </xsl:call-template>
  </xsl:template>

  <xsl:template mode="style:style" match="Style">
    <xsl:element name="style:style">
      <xsl:attribute name="style:name">
        <xsl:apply-templates mode="make-style-name" select="." />
      </xsl:attribute>
      <!--
      <xsl:attribute name="style:parent-style-name"/>
      -->
      <xsl:variable name="styles" select="/HwpDoc/DocInfo/IdMappings/Style" />
      <xsl:variable name="next-style-id" select="@next-style-id + 1"/>
      <xsl:attribute name="style:next-style-name">
        <xsl:apply-templates mode="make-style-name" select="$styles[$next-style-id]" />
      </xsl:attribute>
      <xsl:attribute name="style:family">paragraph</xsl:attribute>
      <xsl:attribute name="style:class">text</xsl:attribute>
      <xsl:variable name="charshapeid" select="@charshape-id + 1"/>
      <xsl:variable name="charshapes" select="/HwpDoc/DocInfo/IdMappings/CharShape" />
      <xsl:variable name="charshape" select="$charshapes[number($charshapeid)]"/>
      <xsl:apply-templates mode="style:paragraph-properties" select="." />
      <xsl:apply-templates select="$charshape" mode="style:text-properties" />
    </xsl:element>
  </xsl:template>

  <xsl:template name="make-ncname">
    <!-- see #140 -->
    <!-- see http://www.w3.org/TR/REC-xml-names/#NT-NCName -->
    <!-- see http://www.w3.org/TR/REC-xml/#NT-Name -->
    <!-- see http://stackoverflow.com/questions/1631396/what-is-an-xsncname-type-and-when-should-it-be-used -->
    <xsl:param name="str" />
    <xsl:variable name="prohibited"> !&quot;#$%&amp;&apos;()*+,/:;&lt;=&gt;?@[\]^`{|}~</xsl:variable>
    <xsl:variable name="replace">______________________________</xsl:variable>
    <xsl:value-of select="translate($str, $prohibited, $replace)" />
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

  <xsl:template mode="style:text-xxxline-style-value" match="CharShape">
    <xsl:choose>
      <xsl:when test="@underline-style = 'solid'">solid</xsl:when>
      <xsl:when test="@underline-style = 'dashed'">dash</xsl:when>
      <xsl:when test="@underline-style = 'dotted'">dotted</xsl:when>
      <xsl:when test="@underline-style = 'dash_dot'">dot-dash</xsl:when>
      <xsl:when test="@underline-style = 'dash_dot_dot'">dot-dot-dash</xsl:when>
      <xsl:when test="@underline-style = 'long_dashed'">long-dash</xsl:when>
      <xsl:when test="@underline-style = 'large_dotted'">dotted</xsl:when>
      <xsl:when test="@underline-style = 'double'">solid</xsl:when>
      <xsl:when test="@underline-style = 'lower_weighted'">solid</xsl:when>
      <xsl:when test="@underline-style = 'upper_weighted'">solid</xsl:when>
      <xsl:when test="@underline-style = 'middle_weighted'">solid</xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template mode="style:text-xxxline-type-value" match="CharShape">
    <xsl:choose>
      <xsl:when test="@underline-style = 'solid'">single</xsl:when>
      <xsl:when test="@underline-style = 'dashed'">single</xsl:when>
      <xsl:when test="@underline-style = 'dotted'">single</xsl:when>
      <xsl:when test="@underline-style = 'dash_dot'">single</xsl:when>
      <xsl:when test="@underline-style = 'dash_dot_dot'">single</xsl:when>
      <xsl:when test="@underline-style = 'long_dashed'">single</xsl:when>
      <xsl:when test="@underline-style = 'large_dotted'">single</xsl:when>
      <xsl:when test="@underline-style = 'double'">double</xsl:when>
      <xsl:when test="@underline-style = 'lower_weighted'">double</xsl:when>
      <xsl:when test="@underline-style = 'upper_weighted'">double</xsl:when>
      <xsl:when test="@underline-style = 'middle_weighted'">double</xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template mode="style:text-underline" match="CharShape">
    <xsl:choose>
      <xsl:when test="@underline = 'underline'">
        <xsl:attribute name="style:text-underline-type"><xsl:apply-templates mode="style:text-xxxline-type-value" select="." /></xsl:attribute>
        <xsl:attribute name="style:text-underline-style"><xsl:apply-templates mode="style:text-xxxline-style-value" select="." /></xsl:attribute>
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
      <xsl:when test="@underline = 'overline'">
        <xsl:attribute name="style:text-overline-type"><xsl:apply-templates mode="style:text-xxxline-type-value" select="." /></xsl:attribute>
        <xsl:attribute name="style:text-overline-style"><xsl:apply-templates mode="style:text-xxxline-style-value" select="." /></xsl:attribute>
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
      <xsl:when test="@underline = 'line_through'">
        <xsl:attribute name="style:text-line-through-type"><xsl:apply-templates mode="style:text-xxxline-type-value" select="." /></xsl:attribute>
        <xsl:attribute name="style:text-line-through-style"><xsl:apply-templates mode="style:text-xxxline-style-value" select="." /></xsl:attribute>
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

  <xsl:template mode="office:body" match="BodyText">
    <office:body>
      <office:text>
	<text:sequence-decls>
	  <text:sequence-decl text:display-outline-level="0" text:name="Illustration"/>
	  <text:sequence-decl text:display-outline-level="0" text:name="Table"/>
	  <text:sequence-decl text:display-outline-level="0" text:name="Text"/>
	  <text:sequence-decl text:display-outline-level="0" text:name="Drawing"/>
	</text:sequence-decls>
	<xsl:apply-templates select="SectionDef" />
      </office:text>
    </office:body>
  </xsl:template>

  <xsl:template mode="style-style-for-paragraph-and-text" match="Paragraph">
    <xsl:variable name="style-id" select="@style-id + 1" />
    <xsl:variable name="style" select="//Style[$style-id]"/>

    <xsl:apply-templates mode="style:style" select="." />

    <xsl:variable name="paragraph-id" select="@paragraph-id + 1"/>
    <xsl:for-each select="LineSeg">
      <xsl:variable name="lineseg-pos" select="position()" />
      <xsl:for-each select="Text">
        <xsl:variable name="text-pos" select="position()" />
        <xsl:variable name="style-name">
          <xsl:text>p</xsl:text>
          <xsl:value-of select="$paragraph-id" />
          <xsl:text>-</xsl:text>
          <xsl:value-of select="$lineseg-pos"/>
          <xsl:text>-</xsl:text>
          <xsl:value-of select="$text-pos"/>
        </xsl:variable>
        <xsl:apply-templates mode="style:style" select=".">
          <xsl:with-param name="style-name" select="$style-name" />
          <xsl:with-param name="style-charshape-id" select="$style/@charshape-id + 1" />
        </xsl:apply-templates>
      </xsl:for-each>
    </xsl:for-each>
  </xsl:template>

  <xsl:template mode="style:style" match="Text">
    <xsl:param name="style-name" />
    <xsl:param name="style-charshape-id" />

    <xsl:variable name="charshape-id" select="@charshape-id + 1" />
    <xsl:if test="$style-charshape-id != $charshape-id">
      <xsl:element name="style:style">
        <xsl:attribute name="style:family">text</xsl:attribute>
        <xsl:attribute name="style:name">
          <xsl:value-of select="$style-name" />
        </xsl:attribute>
        <xsl:apply-templates select="//CharShape[$charshape-id]" mode="style:text-properties" />
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <xsl:template mode="style:style" match="Paragraph">
    <xsl:variable name="paragraph-id" select="@paragraph-id + 1"/>
    <xsl:variable name="style-id" select="@style-id + 1" />
    <xsl:variable name="style" select="//Style[$style-id]"/>
    <xsl:variable name="style-parashape-id" select="$style/@parashape-id + 1"/>
    <xsl:variable name="parashape-id" select="@parashape-id + 1"/>
    <xsl:variable name="parashape" select="//ParaShape[$parashape-id]"/>
    <xsl:if test="$style-parashape-id != $parashape-id or @new-page = '1'">
      <xsl:element name="style:style">
        <xsl:attribute name="style:family">paragraph</xsl:attribute>
        <xsl:attribute name="style:class">text</xsl:attribute>
        <xsl:attribute name="style:name">
          <xsl:text>Paragraph-</xsl:text>
          <xsl:value-of select="@paragraph-id + 1" />
        </xsl:attribute>
        <xsl:apply-templates mode="style:parent-style-name" select="$style" />
        <xsl:if test="@new-section = '1'">
          <xsl:apply-templates mode="style:master-page-name" select="../.." />
        </xsl:if>
	<xsl:apply-templates mode="style:paragraph-properties" select="." />
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <xsl:template mode="style:paragraph-properties" match="Paragraph">
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
    <xsl:variable name="parashape-id" select="@parashape-id + 1"/>
    <xsl:variable name="parashape" select="//ParaShape[$parashape-id]"/>
    <xsl:element name="style:paragraph-properties">
      <xsl:apply-templates mode="style-paragraph-properties-common" select="$parashape" />
      <xsl:if test="@new-page = '1'">
	<xsl:attribute name="fo:break-before">page</xsl:attribute>
      </xsl:if>
    </xsl:element>
  </xsl:template>

  <xsl:template mode="style:parent-style-name" match="Style">
    <xsl:attribute name="style:parent-style-name">
      <xsl:apply-templates mode="make-style-name" select="." />
    </xsl:attribute>
  </xsl:template>

  <xsl:template mode="style:master-page-name" match="SectionDef">
    <xsl:attribute name="style:master-page-name">
      <xsl:text>MasterPage-</xsl:text>
      <xsl:value-of select="@section-id + 1"/>
    </xsl:attribute>
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
            <xsl:attribute name="text:style-name">
              <xsl:apply-templates mode="make-style-name" select="$style" />
            </xsl:attribute>
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
    <xsl:apply-templates select="Text|GShapeObjectControl|FootNote|EndNote|ControlChar">
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
    <xsl:variable name="table-id" select="@table-id + 1" />
    <xsl:element name="table:table">
      <xsl:attribute name="table:style-name">Table-<xsl:value-of select="$table-id"/></xsl:attribute>
      <table:table-column>
        <xsl:attribute name="table:number-columns-repeated"><xsl:value-of select="TableBody/@cols"/></xsl:attribute>
      </table:table-column>
      <xsl:for-each select="TableBody/TableRow">
	<xsl:variable name="rownum" select="position()" />
        <table:table-row>
          <xsl:for-each select="TableCell">
	    <xsl:variable name="colnum" select="position()" />
            <table:table-cell>
	      <xsl:attribute name="table:style-name">Table-<xsl:value-of select="$table-id"/>-<xsl:value-of select="$rownum" />-<xsl:value-of select="$colnum" /></xsl:attribute>
              <xsl:attribute name="table:number-columns-spanned"><xsl:value-of select="@colspan"/></xsl:attribute>
              <xsl:attribute name="table:number-rows-spanned"><xsl:value-of select="@rowspan"/></xsl:attribute>
              <xsl:apply-templates />
            </table:table-cell>
          </xsl:for-each>
        </table:table-row>
      </xsl:for-each>
    </xsl:element>
  </xsl:template>

  <xsl:template mode="style-style-for-table-cells" match="TableControl">
    <xsl:variable name="table-id" select="@table-id + 1" />
    <xsl:for-each select="TableBody/TableRow">
      <xsl:variable name="rowidx" select="position()" />
      <xsl:for-each select="TableCell">
	<xsl:variable name="colidx" select="position()" />
	<xsl:apply-templates mode="style:style" select=".">
	  <xsl:with-param name="table-id" select="$table-id" />
	  <xsl:with-param name="rowidx" select="$rowidx" />
	  <xsl:with-param name="colidx" select="$colidx" />
	</xsl:apply-templates>
      </xsl:for-each>
    </xsl:for-each>
  </xsl:template>

  <xsl:template mode="style:style" match="TableCell">
    <xsl:param name="table-id" />
    <xsl:param name="rowidx" />
    <xsl:param name="colidx" />
    <xsl:element name="style:style">
      <xsl:attribute name="style:name">Table-<xsl:value-of select="$table-id"/>-<xsl:value-of select="$rowidx" />-<xsl:value-of select="$colidx" /></xsl:attribute>
      <xsl:attribute name="style:family">table-cell</xsl:attribute>
      <xsl:apply-templates mode="style:table-cell-properties" select="." />
    </xsl:element>
  </xsl:template>

  <!--
  17.18 style:table-cell-properties
  http://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html#element-style_table-cell-properties
  -->
  <xsl:template mode="style:table-cell-properties" match="TableCell">
    <xsl:element name="style:table-cell-properties">
      <!--
      Attributes:
	fo:background-color 20.175
	fo:border 20.176.2
	fo:border-bottom 20.176.3
	fo:border-left 20.176.4
	fo:border-right 20.176.5
	fo:border-top 20.176.6
	fo:padding 20.210
	fo:padding-bottom 20.211
	fo:padding-left 20.212
	fo:padding-right 20.213
	fo:padding-top 20.214
	fo:wrap-option 20.223
	style:border-line-width 20.241
	style:border-line-width-bottom 20.242
	style:border-line-width-left 20.243
	style:border-line-width-right 20.244
	style:border-line-width-top 20.245
	style:cell-protect 20.246
	style:decimal-places 20.250
	style:diagonal-bl-tr 20.251
	style:diagonal-bl-tr-widths 20.252
	style:diagonal-tl-br 20.253
	style:diagonal-tl-br-widths 20.254
	style:direction 20.255
	style:glyph-orientation-vertical 20.289
	style:print-content 20.323.3
	style:repeat-content 20.334
	style:rotation-align 20.338
	style:rotation-angle 20.339
	style:shadow 20.349
	style:shrink-to-fit 20.350
	style:text-align-source 20.354
	style:vertical-align 20.386.2
	style:writing-mode 20.394.6.
      Elements:
	style:background-image 17.3.
      -->
      <xsl:attribute name="fo:padding-left"><xsl:value-of select="round(@padding-left div 7200 * 2.54 * 10 * 100) div 100" />mm</xsl:attribute>
      <xsl:attribute name="fo:padding-right"><xsl:value-of select="round(@padding-right div 7200 * 2.54 * 10 * 100) div 100" />mm</xsl:attribute>
      <xsl:attribute name="fo:padding-top"><xsl:value-of select="round(@padding-top div 7200 * 2.54 * 10 * 100) div 100" />mm</xsl:attribute>
      <xsl:attribute name="fo:padding-bottom"><xsl:value-of select="round(@padding-bottom div 7200 * 2.54 * 10 * 100) div 100" />mm</xsl:attribute>
      <xsl:variable name="bfid" select="@borderfill-id" />
      <xsl:for-each select="/HwpDoc/DocInfo/IdMappings/BorderFill[number($bfid)]">
	<xsl:apply-templates mode="fo-border" select="." />
	<xsl:apply-templates mode="fo:background-color" select="." />
	<xsl:apply-templates mode="style:background-image" select="." />
      </xsl:for-each>
    </xsl:element>
  </xsl:template>

  <!--
  20.175 fo:background-color
  http://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html#property-fo_background-color
  -->
  <xsl:template mode="fo:background-color" match="BorderFill">
    <!--
    The values of the fo:background-color attribute are transparent or a value of type color 18.3.9.
    -->

    <xsl:for-each select="FillColorPattern">
      <xsl:attribute name="fo:background-color"><xsl:value-of select="@background-color"/></xsl:attribute>
    </xsl:for-each>
  </xsl:template>

  <!--
  17.3 style:background-image
  http://docs.oasis-open.org/office/v1.2/os/OpenDocument-v1.2-os-part1.html#element-style_background-image
  -->
  <xsl:template mode="style:background-image" match="BorderFill">
    <!--
    Attributes:
      draw:opacity 19.202
      style:filter-name 19.477
      style:position 19.508.2
      style:repeat 19.511
      xlink:actuate 19.909
      xlink:href 19.910.28
      xlink:show 19.911
      xlink:type 19.913.
    Elements:
      <office:binary-data> 10.4.5.
    -->
    <xsl:for-each select="FillColorPattern">
	<!-- generate image with @pattern-type and @pattern-color
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
    </xsl:for-each>
    <xsl:for-each select="FillImage">
      <!-- TODO -->
    </xsl:for-each>
  </xsl:template>

  <xsl:template mode="fo-border" match="BorderFill">
    <xsl:for-each select="Border[@attribute-name='left']">
      <xsl:attribute name="fo:border-left">
	<xsl:value-of select="@width" />
	<xsl:text> </xsl:text>
	<xsl:apply-templates mode="fo-border-style-value" select="." />
	<xsl:text> </xsl:text>
	<xsl:value-of select="@color" />
      </xsl:attribute>
    </xsl:for-each>
    <xsl:for-each select="Border[@attribute-name='right']">
      <xsl:attribute name="fo:border-right">
	<xsl:value-of select="@width" />
	<xsl:text> </xsl:text>
	<xsl:apply-templates mode="fo-border-style-value" select="." />
	<xsl:text> </xsl:text>
	<xsl:value-of select="@color" />
      </xsl:attribute>
    </xsl:for-each>
    <xsl:for-each select="Border[@attribute-name='top']">
      <xsl:attribute name="fo:border-top">
	<xsl:value-of select="@width" />
	<xsl:text> </xsl:text>
	<xsl:apply-templates mode="fo-border-style-value" select="." />
	<xsl:text> </xsl:text>
	<xsl:value-of select="@color" />
      </xsl:attribute>
    </xsl:for-each>
    <xsl:for-each select="Border[@attribute-name='bottom']">
      <xsl:attribute name="fo:border-bottom">
	<xsl:value-of select="@width" />
	<xsl:text> </xsl:text>
	<xsl:apply-templates mode="fo-border-style-value" select="." />
	<xsl:text> </xsl:text>
	<xsl:value-of select="@color" />
      </xsl:attribute>
    </xsl:for-each>
  </xsl:template>

  <xsl:template mode="fo-border-style-value" match="Border">
    <xsl:value-of select="@stroke-type" />
  </xsl:template>

  <xsl:template mode="style:style" match="TableControl">
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
  </xsl:template>

  <xsl:template match="GShapeObjectControl" mode="style-graphic-properties">
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

	    <xsl:when test="@halign = 'inside'">
	      <xsl:text>from-inside</xsl:text>
	    </xsl:when>

	    <xsl:when test="@halign = 'center' and @x = 0">
	      <xsl:text>center</xsl:text>
	    </xsl:when>
	    <xsl:when test="@halign = 'center'">
	      <!-- TODO -->
	      <xsl:text>from-left</xsl:text>
	    </xsl:when>

	    <xsl:when test="@halign = 'outside' and @x = 0">
	      <xsl:text>outside</xsl:text>
	    </xsl:when>
	    <xsl:when test="@halign = 'outside'">
	      <!-- TODO -->
	      <xsl:text>outside</xsl:text>
	    </xsl:when>

	    <xsl:when test="@halign = 'right' and @x = 0">
	      <xsl:text>right</xsl:text>
	    </xsl:when>
	    <xsl:when test="@halign = 'right'">
	      <!-- TODO -->
	      <xsl:text>right</xsl:text>
	    </xsl:when>

	  </xsl:choose>
	</xsl:attribute>

	<xsl:attribute name="style:vertical-pos">
	  <xsl:choose>
	    <xsl:when test="@valign = 'top'">
	      <xsl:text>from-top</xsl:text>
	    </xsl:when>

	    <xsl:when test="@valign = 'middle' and @y = 0">
	      <xsl:text>middle</xsl:text>
	    </xsl:when>
	    <xsl:when test="@valign = 'middle'">
	      <!-- TODO -->
	      <xsl:text>middle</xsl:text>
	    </xsl:when>

	    <xsl:when test="@valign = 'bottom' and @y = 0">
	      <xsl:text>bottom</xsl:text>
	    </xsl:when>
	    <xsl:when test="@valign = 'bottom'">
	      <!-- TODO -->
	      <xsl:text>bottom</xsl:text>
	    </xsl:when>

	    <!-- TODO -->
	    <xsl:otherwise>
	      <xsl:text>top</xsl:text>
	    </xsl:otherwise>
	  </xsl:choose>
	</xsl:attribute>
      </xsl:when>
      <xsl:otherwise> <!-- when @inline = 1 -->
	<xsl:attribute name="style:vertical-rel">baseline</xsl:attribute>
	<xsl:attribute name="style:vertical-pos">top</xsl:attribute>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template mode="style-graphic-properties" match="ShapeComponent[@chid='$con']">
  </xsl:template>

  <xsl:template mode="draw-fill" match="ShapeComponent">
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
  </xsl:template>

  <xsl:template mode="draw-stroke" match="ShapeComponent">
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
  </xsl:template>

  <xsl:template match="ShapeComponent" mode="style:style">
    <xsl:element name="style:style">
      <xsl:attribute name="style:name">Shape-<xsl:value-of select="@shape-id + 1"/></xsl:attribute>
      <xsl:attribute name="style:family">graphic</xsl:attribute>
      <!-- 15.27 Frame Formatting Properties -->
      <xsl:element name="style:graphic-properties">
	<xsl:apply-templates mode="style-graphic-properties" select=".." />
	<xsl:apply-templates mode="draw-fill" select="." />
	<xsl:apply-templates mode="draw-stroke" select="." />
      </xsl:element>
    </xsl:element>
  </xsl:template>

  <!-- ShapeComponent의 transform matrix들로 draw:transform 속성 생성 -->
  <xsl:template mode="draw-transform" match="ShapeComponent">
    <xsl:param name="x" />
    <xsl:param name="y" />

    <!-- TODO: 여러 개의 ScaleRotationMatrix가 존재할 때 -->
    <xsl:attribute name="draw:transform">

      <!-- 타겟 좌표계에서 ShapeComponent-local 좌표계로 변환 -->
      <xsl:text> translate (</xsl:text>
      <xsl:value-of select="-round($x div 7200 * 25.4 * 100) div 100"/><xsl:text>mm </xsl:text>
      <xsl:value-of select="-round($y div 7200 * 25.4 * 100) div 100"/><xsl:text>mm)</xsl:text>

      <xsl:for-each select="Array/ScaleRotationMatrix">
	<!-- ShapeComponent-local 좌표계 변환: Scaler -->
	<xsl:apply-templates mode="draw-transform-matrix" select="Matrix[@attribute-name='scaler']" />

	<!-- ShapeComponent-local 좌표계 변환: Rotator -->
	<xsl:apply-templates mode="draw-transform-matrix" select="Matrix[@attribute-name='rotator']" />
      </xsl:for-each>

      <!-- ShapeComponent-local 좌표계 변환: Translator -->
      <xsl:apply-templates mode="draw-transform-matrix" select="Matrix[@attribute-name='translation']" />

      <!-- ShapeComponent-local 좌표계에서 다시 타겟 좌표계로 변환 -->
      <xsl:text> translate (</xsl:text>
      <xsl:value-of select="round($x div 7200 * 25.4 * 100) div 100"/><xsl:text>mm </xsl:text>
      <xsl:value-of select="round($y div 7200 * 25.4 * 100) div 100"/><xsl:text>mm)</xsl:text>

    </xsl:attribute>

  </xsl:template>

  <xsl:template match="Matrix" mode="draw-transform-matrix">
    <xsl:text> matrix (</xsl:text>
    <xsl:value-of select="@a"/><xsl:text> </xsl:text>
    <xsl:value-of select="@b"/><xsl:text> </xsl:text>
    <xsl:value-of select="@c"/><xsl:text> </xsl:text>
    <xsl:value-of select="@d"/><xsl:text> </xsl:text>
    <xsl:value-of select="round(@e div 7200 * 25.4 * 100) div 100"/><xsl:text>mm </xsl:text>
    <xsl:value-of select="round(@f div 7200 * 25.4 * 100) div 100"/><xsl:text>mm)</xsl:text>
  </xsl:template>

  <xsl:template match="GShapeObjectControl">
    <xsl:apply-templates select="ShapeComponent">
      <xsl:with-param name="x" select="@x" />
      <xsl:with-param name="y" select="@y" />
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="ShapeComponent[@chid='$con']">
    <xsl:param name="x" />
    <xsl:param name="y" />
    <xsl:element name="draw:g">
      <xsl:attribute name="draw:style-name">Shape-<xsl:value-of select="@shape-id + 1"/></xsl:attribute>
      <xsl:apply-templates mode="text-anchor-type" select=".." />
      <xsl:apply-templates select="ShapeComponent">
	<xsl:with-param name="x" select="$x" />
	<xsl:with-param name="y" select="$y" />
      </xsl:apply-templates>
    </xsl:element>
  </xsl:template>

  <xsl:template match="ShapeComponent[@chid='$pic']">
    <xsl:param name="x" />
    <xsl:param name="y" />

    <!-- 9.3 Frames -->
    <xsl:element name="draw:frame">
      <!-- common-draw-style-name-attlist -->
      <xsl:attribute name="draw:style-name">Shape-<xsl:value-of select="@shape-id + 1"/></xsl:attribute>
      <xsl:apply-templates mode="draw-image-frame-attributes" select="..">
	<xsl:with-param name="shapecomponent-pict" select="." />
      </xsl:apply-templates>

      <xsl:apply-templates mode="draw-transform" select=".">
	<xsl:with-param name="x" select="$x" />
	<xsl:with-param name="y" select="$y" />
      </xsl:apply-templates>

      <xsl:for-each select="ShapePicture">
	<xsl:variable name="binpath" select="'bindata/'"/>
	<xsl:variable name="bindataid" select="PictureInfo/@bindata-id"/>
	<xsl:variable name="bindata" select="/HwpDoc/DocInfo/IdMappings/BinData[number($bindataid)]"/>
	<xsl:element name="draw:image">
	  <xsl:choose>
	    <xsl:when test="$bindata/@storage = 'embedding'">
	      <xsl:for-each select="$bindata/BinDataEmbedding">
		<xsl:choose>
		  <xsl:when test="@inline = 'true'">
		    <xsl:element name="office:binary-data">
		      <xsl:if test="@inline = 'true'">
			<xsl:value-of select="text()" />
		      </xsl:if>
		    </xsl:element>
		  </xsl:when>
		  <xsl:otherwise>
		    <xsl:attribute name="xlink:actuate">onLoad</xsl:attribute>
		    <xsl:attribute name="xlink:show">embed</xsl:attribute>
		    <xsl:attribute name="xlink:type">simple</xsl:attribute>
		    <xsl:attribute name="xlink:href"><xsl:value-of select="$binpath"/><xsl:value-of select="@storage-id"/>.<xsl:value-of select="@ext"/></xsl:attribute>
		  </xsl:otherwise>
		</xsl:choose>
	      </xsl:for-each>
	    </xsl:when>
	  </xsl:choose>
	</xsl:element>
      </xsl:for-each>
    </xsl:element>
  </xsl:template>

  <xsl:template mode="draw-image-frame-attributes" match="ShapeComponent[@chid='$con']">
    <xsl:param name="shapecomponent-pict" />
    <xsl:attribute name="svg:width"><xsl:value-of select="round($shapecomponent-pict/@initial-width div 7200 * 2.54 * 10 * 100) div 100"/>mm</xsl:attribute>
    <xsl:attribute name="svg:height"><xsl:value-of select="round($shapecomponent-pict/@initial-height div 7200 * 2.54 * 10 * 100) div 100"/>mm</xsl:attribute>
  </xsl:template>

  <xsl:template mode="text-anchor-type" match="GShapeObjectControl">
    <!-- common-text-anchor-attlist -->
    <xsl:choose>
      <xsl:when test="@inline = 1">
	<xsl:attribute name="text:anchor-type">as-char</xsl:attribute>
      </xsl:when>
      <xsl:otherwise>
	<xsl:attribute name="text:anchor-type">paragraph</xsl:attribute>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template mode="text-anchor-type" match="ShapeComponent[@chid='$con']">
  </xsl:template>

  <xsl:template mode="draw-image-frame-attributes" match="GShapeObjectControl">
    <xsl:param name="shapecomponent-pict" />
    <!-- common-draw-position-attlist -->
    <xsl:if test="@inline = 0">
      <xsl:attribute name="svg:x"><xsl:value-of select="@x div 100"/>pt</xsl:attribute>
      <xsl:attribute name="svg:y"><xsl:value-of select="@y div 100"/>pt</xsl:attribute>
    </xsl:if>
    <!-- common-draw-z-index-attlist -->
    <xsl:attribute name="draw:z-index"><xsl:value-of select="@z-order"/></xsl:attribute>
    <!-- 15.27.1 Frame Widths -->
    <xsl:choose>
      <xsl:when test="@width-relto = 'absolute'">
	<xsl:attribute name="svg:width"><xsl:value-of select="round(ShapeComponent/@initial-width div 7200 * 2.54 * 10 * 100) div 100"/>mm</xsl:attribute>
      </xsl:when>
    </xsl:choose>
    <!-- 15.27.2 Frame Heights -->
    <xsl:choose>
      <xsl:when test="@height-relto = 'absolute'">
	<xsl:attribute name="svg:height"><xsl:value-of select="round(ShapeComponent/@initial-height div 7200 * 2.54 * 10 * 100) div 100"/>mm</xsl:attribute>
      </xsl:when>
    </xsl:choose>
    <xsl:apply-templates mode="text-anchor-type" select="." />
  </xsl:template>

  <xsl:template match="ShapeComponent[@chid='$rec']">
    <xsl:param name="x" />
    <xsl:param name="y" />

    <xsl:element name="draw:rect">
      <xsl:attribute name="draw:style-name">Shape-<xsl:value-of select="@shape-id + 1"/></xsl:attribute>
      <xsl:attribute name="svg:x"><xsl:value-of select="round($x div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:attribute name="svg:y"><xsl:value-of select="round($y div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:variable name="width" select="ShapeRectangle/Coord[2]/@x - ShapeRectangle/Coord[1]/@x"/>
      <xsl:variable name="height" select="ShapeRectangle/Coord[3]/@y - ShapeRectangle/Coord[2]/@y"/>
      <xsl:attribute name="svg:width"><xsl:value-of select="round($width div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:attribute name="svg:height"><xsl:value-of select="round($height div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:apply-templates mode="text-anchor-type" select=".." />

      <xsl:apply-templates mode="draw-transform" select=".">
	<xsl:with-param name="x" select="$x" />
	<xsl:with-param name="y" select="$y" />
      </xsl:apply-templates>

      <xsl:for-each select="TextboxParagraphList">
        <xsl:apply-templates />
      </xsl:for-each>
    </xsl:element>
  </xsl:template>

  <xsl:template match="ShapeComponent[@chid='$lin']">
    <xsl:param name="x" />
    <xsl:param name="y" />
    <xsl:variable name="x1" select="$x"/>
    <xsl:variable name="y1" select="$y"/>
    <xsl:variable name="cx" select="Coord[@attribute-name='rotation_center']/@x"/>
    <xsl:variable name="cy" select="Coord[@attribute-name='rotation_center']/@y"/>
    <xsl:variable name="x2" select="$x1 + 2 * $cx"/>
    <xsl:variable name="y2" select="$y1 + 2 * $cy"/>
    <xsl:element name="draw:line">
      <xsl:attribute name="svg:x1"><xsl:value-of select="round($x1 div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:attribute name="svg:y1"><xsl:value-of select="round($y1 div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:attribute name="svg:x2"><xsl:value-of select="round($x2 div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:attribute name="svg:y2"><xsl:value-of select="round($y2 div 7200 * 25.4 * 100) div 100"/>mm</xsl:attribute>
      <xsl:attribute name="draw:style-name">Shape-<xsl:value-of select="@shape-id + 1"/></xsl:attribute>
      <xsl:apply-templates mode="text-anchor-type" select=".." />
    </xsl:element>
  </xsl:template>

  <!-- 각주 -->
  <xsl:template match="FootNote">
    <xsl:apply-templates mode="text:note" select="." />
  </xsl:template>

  <!-- 미주 -->
  <xsl:template match="EndNote">
    <xsl:apply-templates mode="text:note" select="." />
  </xsl:template>

  <!-- 각주/미주 공통 -->
  <xsl:template mode="text:note" match="FootNote|EndNote">
    <xsl:element name="text:note">
      <xsl:attribute name="text:id"><xsl:value-of select="local-name()" />-<xsl:value-of select="@number" /></xsl:attribute>
      <xsl:apply-templates mode="text:note-class" select="." />
      <xsl:apply-templates mode="text:note-citation" select="." />
      <xsl:apply-templates mode="text:note-body" select="." />
    </xsl:element>
  </xsl:template>

  <xsl:template mode="text:note-class" match="FootNote">
    <xsl:attribute name="text:note-class">footnote</xsl:attribute>
  </xsl:template>

  <xsl:template mode="text:note-class" match="EndNote">
    <xsl:attribute name="text:note-class">endnote</xsl:attribute>
  </xsl:template>

  <xsl:template mode="text:note-citation" match="FootNote|EndNote">
    <xsl:element name="text:note-citation">
      <xsl:value-of select="@number"/>
    </xsl:element>
  </xsl:template>

  <xsl:template mode="text:note-body" match="FootNote|EndNote">
    <xsl:element name="text:note-body">
      <xsl:apply-templates select="ListHeader/Paragraph" />
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>
