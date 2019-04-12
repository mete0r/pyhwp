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
  <xsl:template match="/">
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
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
      <!--
      <office:meta>
        <meta:initial-creator>mete0r </meta:initial-creator>
        <meta:creation-date>2011-06-17T18:20:45</meta:creation-date>
        <dc:date>2011-06-18T13:16:44</dc:date>
        <dc:creator>mete0r </dc:creator>
        <meta:editing-duration>PT12M22S</meta:editing-duration>
        <meta:editing-cycles>6</meta:editing-cycles>
        <meta:generator>LibreOffice/3.3$Linux LibreOffice_project/330m19$Build-202</meta:generator>
        <meta:document-statistic meta:table-count="1" meta:image-count="1" meta:object-count="0" meta:page-count="1" meta:paragraph-count="6" meta:word-count="6" meta:character-count="15"/>
      </office:meta>
      <office:scripts>
        <office:script script:language="ooo:Basic">
          <ooo:libraries/>
        </office:script>
      </office:scripts>
      <office:font-face-decls>
        <style:font-face style:name="Lohit Hindi1" svg:font-family="'Lohit Hindi'"/>
        <style:font-face style:name="은 돋움" svg:font-family="'은 돋움'" style:font-family-generic="roman" style:font-pitch="variable"/>
        <style:font-face style:name="은 돋움1" svg:font-family="'은 돋움'" style:font-family-generic="swiss" style:font-pitch="variable"/>
        <style:font-face style:name="Lohit Hindi" svg:font-family="'Lohit Hindi'" style:font-family-generic="system" style:font-pitch="variable"/>
        <style:font-face style:name="은 돋움2" svg:font-family="'은 돋움'" style:font-family-generic="system" style:font-pitch="variable"/>
      </office:font-face-decls>
      <office:styles>
        <style:default-style style:family="graphic">
          <style:graphic-properties draw:shadow-offset-x="0.3cm" draw:shadow-offset-y="0.3cm" draw:start-line-spacing-horizontal="0.283cm" draw:start-line-spacing-vertical="0.283cm" draw:end-line-spacing-horizontal="0.283cm" draw:end-line-spacing-vertical="0.283cm" style:flow-with-text="false"/>
          <style:paragraph-properties style:text-autospace="ideograph-alpha" style:line-break="strict" style:writing-mode="lr-tb" style:font-independent-line-spacing="false">
            <style:tab-stops/>
          </style:paragraph-properties>
          <style:text-properties style:use-window-font-color="true" fo:font-size="12pt" fo:language="en" fo:country="US" style:letter-kerning="true" style:font-size-asian="10.5pt" style:language-asian="ko" style:country-asian="KR" style:font-size-complex="12pt" style:language-complex="hi" style:country-complex="IN"/>
        </style:default-style>
        <style:default-style style:family="paragraph">
          <style:paragraph-properties fo:hyphenation-ladder-count="no-limit" style:text-autospace="ideograph-alpha" style:punctuation-wrap="hanging" style:line-break="strict" style:tab-stop-distance="1.251cm" style:writing-mode="page"/>
          <style:text-properties style:use-window-font-color="true" style:font-name="은 돋움" fo:font-size="12pt" fo:language="en" fo:country="US" style:letter-kerning="true" style:font-name-asian="은 돋움2" style:font-size-asian="10.5pt" style:language-asian="ko" style:country-asian="KR" style:font-name-complex="Lohit Hindi" style:font-size-complex="12pt" style:language-complex="hi" style:country-complex="IN" fo:hyphenate="false" fo:hyphenation-remain-char-count="2" fo:hyphenation-push-char-count="2"/>
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
          <style:text-properties style:font-name="은 돋움1" fo:font-size="14pt" style:font-name-asian="은 돋움2" style:font-size-asian="14pt" style:font-name-complex="Lohit Hindi" style:font-size-complex="14pt"/>
        </style:style>
        <style:style style:name="Text_20_body" style:display-name="Text body" style:family="paragraph" style:parent-style-name="Standard" style:class="text">
          <style:paragraph-properties fo:margin-top="0cm" fo:margin-bottom="0.212cm"/>
        </style:style>
        <style:style style:name="List" style:family="paragraph" style:parent-style-name="Text_20_body" style:class="list">
          <style:text-properties style:font-size-asian="12pt" style:font-name-complex="Lohit Hindi1"/>
        </style:style>
        <style:style style:name="Caption" style:family="paragraph" style:parent-style-name="Standard" style:class="extra">
          <style:paragraph-properties fo:margin-top="0.212cm" fo:margin-bottom="0.212cm" text:number-lines="false" text:line-number="0"/>
          <style:text-properties fo:font-size="12pt" fo:font-style="italic" style:font-size-asian="12pt" style:font-style-asian="italic" style:font-name-complex="Lohit Hindi1" style:font-size-complex="12pt" style:font-style-complex="italic"/>
        </style:style>
        <style:style style:name="Index" style:family="paragraph" style:parent-style-name="Standard" style:class="index">
          <style:paragraph-properties text:number-lines="false" text:line-number="0"/>
          <style:text-properties style:font-size-asian="12pt" style:font-name-complex="Lohit Hindi1"/>
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
      </office:styles>
      <office:automatic-styles>
        <style:style style:name="표1" style:family="table">
          <style:table-properties style:width="17cm" table:align="margins"/>
        </style:style>
        <style:style style:name="표1.A" style:family="table-column">
          <style:table-column-properties style:column-width="5.667cm" style:rel-column-width="21845*"/>
        </style:style>
        <style:style style:name="표1.A1" style:family="table-cell">
          <style:table-cell-properties fo:padding="0.097cm" fo:border-left="0.002cm solid #000000" fo:border-right="none" fo:border-top="0.002cm solid #000000" fo:border-bottom="0.002cm solid #000000"/>
        </style:style>
        <style:style style:name="표1.C1" style:family="table-cell">
          <style:table-cell-properties fo:padding="0.097cm" fo:border="0.002cm solid #000000"/>
        </style:style>
        <style:style style:name="표1.A2" style:family="table-cell">
          <style:table-cell-properties fo:padding="0.097cm" fo:border-left="0.002cm solid #000000" fo:border-right="none" fo:border-top="none" fo:border-bottom="0.002cm solid #000000"/>
        </style:style>
        <style:style style:name="표1.B2" style:family="table-cell">
          <style:table-cell-properties fo:padding="0.097cm" fo:border-left="0.002cm solid #000000" fo:border-right="0.002cm solid #000000" fo:border-top="none" fo:border-bottom="0.002cm solid #000000"/>
        </style:style>
        <style:style style:name="T1" style:family="text">
          <style:text-properties fo:font-style="italic" style:font-style-asian="italic" style:font-style-complex="italic"/>
        </style:style>
        <style:style style:name="T2" style:family="text">
          <style:text-properties fo:font-weight="bold" style:font-weight-asian="bold" style:font-weight-complex="bold"/>
        </style:style>
        <style:style style:name="T3" style:family="text">
          <style:text-properties style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"/>
        </style:style>
        <style:style style:name="fr1" style:family="graphic" style:parent-style-name="Graphics">
          <style:graphic-properties style:vertical-pos="from-top" style:vertical-rel="paragraph" style:horizontal-pos="from-left" style:horizontal-rel="paragraph" style:mirror="none" fo:clip="rect(0cm, 0cm, 0cm, 0cm)" draw:luminance="0%" draw:contrast="0%" draw:red="0%" draw:green="0%" draw:blue="0%" draw:gamma="100%" draw:color-inversion="false" draw:image-opacity="100%" draw:color-mode="standard"/>
        </style:style>
        <style:page-layout style:name="pm1">
          <style:page-layout-properties fo:page-width="21.001cm" fo:page-height="29.7cm" style:num-format="1" style:print-orientation="portrait" fo:margin-top="2cm" fo:margin-bottom="2cm" fo:margin-left="2cm" fo:margin-right="2cm" style:writing-mode="lr-tb" style:footnote-max-height="0cm">
            <style:footnote-sep style:width="0.018cm" style:distance-before-sep="0.101cm" style:distance-after-sep="0.101cm" style:adjustment="left" style:rel-width="25%" style:color="#000000"/>
          </style:page-layout-properties>
          <style:header-style/>
          <style:footer-style/>
        </style:page-layout>
      </office:automatic-styles>
      <office:master-styles>
        <style:master-page style:name="Standard" style:page-layout-name="pm1"/>
      </office:master-styles>
      -->
      <office:body>
        <office:text>
          <!--
          <text:sequence-decls>
            <text:sequence-decl text:display-outline-level="0" text:name="Illustration"/>
            <text:sequence-decl text:display-outline-level="0" text:name="Table"/>
            <text:sequence-decl text:display-outline-level="0" text:name="Text"/>
            <text:sequence-decl text:display-outline-level="0" text:name="Drawing"/>
          </text:sequence-decls>
          -->
          <xsl:for-each select="HwpDoc/BodyText">
              <xsl:apply-templates />
          </xsl:for-each>
        </office:text>
      </office:body>
    </office:document>
  </xsl:template>

  <xsl:template match="Paragraph">
      <xsl:element name="text:p">
        <xsl:apply-templates select="LineSeg/Text"/>
      </xsl:element>
      <xsl:apply-templates select="LineSeg/TableControl"/>
  </xsl:template>

  <xsl:template match="Text">
    <xsl:element name="text:span"><xsl:value-of select="text()"/></xsl:element>
  </xsl:template>

  <xsl:template match="ControlChar"></xsl:template>

  <xsl:template match="GShapeObjectControl">
    <!--
    <xsl:element name="draw:frame">
        <xsl:apply-templates />
    </xsl:element>
    -->
    <!--
    <draw:frame draw:style-name="fr1" draw:name="그림1" text:anchor-type="paragraph" svg:x="2.718cm" svg:y="0.291cm" svg:width="0.452cm" svg:height="0.452cm" draw:z-index="0">
      <draw:image>
        <office:binary-data>iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QAAAAAAAD5Q7t/AAAACXBIWXMAAA3WAAAN1gGQb3mcAAAACXZwQWcAAAAQAAAAEABcxq3DAAACV0lEQVQ4y32TMU9UQRDHf7tvOY47uAgel4tBhUKIJoZE0YbSSiBoQW2hFQnfwEjHF7CHjg6auwIaGm20wwYS6AUSNCdwB++93RmLd4AK+E+2mp2Z339n1szPzyMiuZmZmTelUmlIVZV/1Gg04u97e6tTk5Nb09PT1Ov1i5grFos453qq1epcX1/fqIj8lWyMoVwu09vb+2pjY2OuVqt9mZh4ydraelYgu6ZGVW0cxxwfHXEFAegqFJ4Oj4ws1ur1tysrq1/Hx8fZ3NzEqiqqioggISDBo8Ejf5zgPa1mE+fco8H7gx+Xl5eHFxYWMgJVRUWREGgGy4GWMBiczTp3O6En8qTHx+zu7HJycvK8Uql8WFpafDc7O5s4VUHUggR2G8r6foHIGMoFcEa519Hkcf4EVaVcvk2l0o/3fnRs7FkpSZJDJ6JYq/gg2NY+xZ+HEPWgSYGunhLdnZDr6ECBrnyefD5Po9HAGINzUduCCiLCj4M9vn3+hNoctrNIrrsf/3CIgQe3EBGstVhrCSG0cxSnKqha0jTlbnWA1y+msJHD2ggbWaqlDpwD0YjIWkQE7z3njV02ASX1nr5iJ08GctkYVQBB8bRagDFYazHGEEJAJJueU1HUKiEEkjTlLEnh6jISRREG8N7jQ5tAFCcqWL3EclHETVLNGgXffoNzCypZIE1T4ji+NtkYk1EYkxFcWGhvYkYgOOduKMCF/4ygXSCOY3zkpdVqnlprUiDwf0WtVvP07OxMfAi4nZ1dUP3Vlc+/z+Vyd5Rr/9IlCZg4Sfa2trePQPkN6rGAJMLKdHsAAAAldEVYdGRhdGU6Y3JlYXRlADIwMTAtMDUtMjRUMDc6NDI6MTctMDY6MDB3nikDAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDEwLTA1LTI0VDA3OjQyOjE3LTA2OjAwBsORvwAAADV0RVh0TGljZW5zZQBodHRwOi8vY3JlYXRpdmVjb21tb25zLm9yZy9saWNlbnNlcy9MR1BMLzIuMS87wbQYAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAA90RVh0U291cmNlAG51b3ZlWFQy6iA23AAAACJ0RVh0U291cmNlX1VSTABodHRwOi8vbnVvdmV4dC5wd3NwLm5ldJGJxy0AAAAASUVORK5CYII=</office:binary-data>
      </draw:image>
    </draw:frame>
    -->
  </xsl:template>

  <xsl:template match="TableControl">
    <table:table>
      <table:table-column>
      <xsl:attribute name="table:number-columns-repeated"><xsl:value-of select="TableBody/@cols"/></xsl:attribute>
      </table:table-column>
      <xsl:for-each select="TableBody/TableRow">
        <table:table-row>
          <xsl:for-each select="TableCell">
            <table:table-cell>
              <xsl:apply-templates />
            </table:table-cell>
          </xsl:for-each>
        </table:table-row>
      </xsl:for-each>
    </table:table>
    <!--
    <table:table table:name="표1" table:style-name="표1">
      <table:table-column table:style-name="표1.A" table:number-columns-repeated="3"/>
      <table:table-row>
        <table:table-cell table:style-name="표1.A1" office:value-type="string">
          <text:p text:style-name="Table_20_Contents">A0</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="표1.A1" office:value-type="string">
          <text:p text:style-name="Table_20_Contents">B0</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="표1.C1" office:value-type="string">
          <text:p text:style-name="Table_20_Contents">C0</text:p>
        </table:table-cell>
      </table:table-row>
      <table:table-row>
        <table:table-cell table:style-name="표1.A2" office:value-type="string">
          <text:p text:style-name="Table_20_Contents">A1</text:p>
        </table:table-cell>
        <table:table-cell table:style-name="표1.B2" table:number-columns-spanned="2" office:value-type="string">
          <text:p text:style-name="Table_20_Contents">B1</text:p>
        </table:table-cell>
        <table:covered-table-cell/>
      </table:table-row>
    </table:table>
    -->
  </xsl:template>
</xsl:stylesheet>
