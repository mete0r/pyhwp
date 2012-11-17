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
      <xsl:attribute name="fo:text-align">
        <xsl:choose>
          <xsl:when test="$parashape/@align = 'both'">justify</xsl:when>
          <xsl:when test="$parashape/@align = 'left'">left</xsl:when>
          <xsl:when test="$parashape/@align = 'right'">right</xsl:when>
          <xsl:when test="$parashape/@align = 'center'">center</xsl:when>
          <xsl:when test="$parashape/@align = 'distribute'">justify</xsl:when>
          <xsl:when test="$parashape/@align = 'distribute_space'">justify</xsl:when>
          <xsl:otherwise>justify</xsl:otherwise>
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
        <xsl:when test="$parashape/@linespacing-type = 'ratio'">
          <xsl:attribute name="fo:line-height"><xsl:value-of select="number($parashape/@linespacing)"/>%</xsl:attribute>
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
        <xsl:when test="$parashape/@linespacing-type = 'fixed'">
          <xsl:attribute name="fo:line-height"><xsl:value-of select="number($parashape/@linespacing) div 200"/>pt</xsl:attribute>
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
        <xsl:when test="$parashape/@linespacing-type = 'spaceonly'">
          <xsl:attribute name="style:line-spacing"><xsl:value-of select="number($parashape/@linespacing) div 200 div 2"/>pt</xsl:attribute>
        </xsl:when>
      </xsl:choose>
  </xsl:template>

  <xsl:template mode="style:text-properties" match="CharShape">
    <xsl:element name="style:text-properties">

      <xsl:apply-templates mode="style:font-name" select="FontFace" />
      <xsl:apply-templates mode="style:font-name-asian" select="FontFace" />

      <xsl:apply-templates mode="fo:font-size" select="." />
      <xsl:apply-templates mode="style:font-size-asian" select="." />

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
      <xsl:value-of select="@basesize div 100"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>
  </xsl:template>

  <xsl:template mode="style:font-size-asian" match="CharShape">
    <xsl:attribute name="style:font-size-asian">
      <xsl:value-of select="@basesize div 100"/>
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
