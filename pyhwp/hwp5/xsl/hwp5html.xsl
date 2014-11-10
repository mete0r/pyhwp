<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.w3.org/1999/xhtml">
  <xsl:import href="hwp5css-common.xsl" />
  <xsl:output method="xml" encoding="utf-8" indent="no"
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
        <xsl:element name="style">
          <xsl:attribute name="type">text/css</xsl:attribute>
          <xsl:text>&#10;</xsl:text>
          <xsl:apply-templates select="BodyText/SectionDef" mode="css-rule" />
          <xsl:apply-templates select="//Header" mode="css-rule" />
          <xsl:apply-templates select="//Footer" mode="css-rule" />
        </xsl:element>
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
      <xsl:apply-templates select="." mode="css-rule" />
    </xsl:element>
  </xsl:template>

  <xsl:template match="BodyText" mode="body">
    <xsl:element name="body">
      <xsl:apply-templates select="SectionDef" mode="div" />
    </xsl:element>
  </xsl:template>

  <xsl:template match="SectionDef" mode="div">
    <xsl:element name="div">
      <xsl:attribute name="class">
        <xsl:text>Section</xsl:text>
        <xsl:text> </xsl:text>
        <xsl:text>Section-</xsl:text>
        <xsl:value-of select="@section-id" />
        <xsl:text> </xsl:text>
        <xsl:text>Paper</xsl:text>
      </xsl:attribute>
      <xsl:element name="div">
        <xsl:attribute name="class">HeaderPageFooter</xsl:attribute>
        <xsl:apply-templates select="//Header" mode="div" />
        <xsl:element name="div">
          <xsl:attribute name="class">Page</xsl:attribute>
          <xsl:apply-templates />
        </xsl:element>
        <xsl:apply-templates select="//Footer" mode="div" />
      </xsl:element>
    </xsl:element>
  </xsl:template>

  <xsl:template match="Header" mode="div">
    <xsl:element name="div">
      <xsl:attribute name="class">HeaderArea</xsl:attribute>
      <xsl:apply-templates select="HeaderParagraphList/Paragraph" />
    </xsl:element>
  </xsl:template>

  <xsl:template match="Footer" mode="div">
    <xsl:element name="div">
      <xsl:attribute name="class">FooterArea</xsl:attribute>
      <xsl:apply-templates select="FooterParagraphList/Paragraph" />
    </xsl:element>
  </xsl:template>

  <xsl:template match="Paragraph">
    <xsl:element name="p">
      <xsl:variable name="styleid" select="@style-id"/>
      <xsl:variable name="style" select="//Style[number($styleid)+1]" />
      <xsl:variable name="stylename" select="$style/@name" />
      <xsl:variable name="stylencname" select="translate($stylename, ' ', '-')" />
      <xsl:variable name="parashape_pos" select="number(@parashape-id) + 1" />
      <xsl:variable name="parashape" select="//ParaShape[$parashape_pos]" />
      <xsl:attribute name="class">
        <xsl:value-of select="$stylencname" />
        <xsl:choose>
          <xsl:when test="$style/@parashape-id = @parashape-id">
            <xsl:apply-templates select="$style" mode="add-class-bullet" />
          </xsl:when>
          <xsl:otherwise>
            <xsl:text> </xsl:text>
            <xsl:text>parashape-</xsl:text>
            <xsl:value-of select="@parashape-id"/>
            <xsl:apply-templates select="." mode="add-class-bullet" />
          </xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:for-each select="LineSeg">
        <xsl:apply-templates select="Text|ControlChar|AutoNumbering|TableControl[@inline='1']|GShapeObjectControl[@inline='1']" />
      </xsl:for-each>
    </xsl:element>
    <xsl:apply-templates select="LineSeg/TableControl[@inline='0']" />
    <xsl:apply-templates select="LineSeg/GShapeObjectControl[@inline='0']" />
  </xsl:template>

  <xsl:template match="ControlChar"><xsl:value-of select="@char"/></xsl:template>

  <xsl:template match="Paragraph/LineSeg/Text">
    <xsl:element name="span">
      <xsl:variable name="styleid" select="../../@style-id"/>
      <xsl:variable name="style" select="//Style[number($styleid)+1]" />
      <xsl:variable name="stylename" select="$style/@name" />
      <xsl:variable name="stylencname" select="translate($stylename, ' ', '-')" />
      <xsl:attribute name="class">
        <xsl:text>lang-</xsl:text>
        <xsl:value-of select="@lang" />
        <xsl:choose>
          <xsl:when test="$style/@charshape-id = @charshape-id"></xsl:when>
          <xsl:otherwise>
              <xsl:text> </xsl:text>
              <xsl:text>charshape-</xsl:text>
              <xsl:value-of select="@charshape-id" />
          </xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:value-of select="text()"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="AutoNumbering">
    <xsl:element name="span">
      <xsl:attribute name="class">
        <xsl:text>autonumbering</xsl:text>
        <xsl:text> </xsl:text>
        <xsl:text>autonumbering-</xsl:text>
        <xsl:value-of select="@kind" />
      </xsl:attribute>
      <xsl:value-of select="@prefix" />
      <xsl:value-of select="@number" />
      <xsl:value-of select="@suffix" />
    </xsl:element>
  </xsl:template>

  <xsl:template match="TableControl[@inline='1']">
    <xsl:element name="span">
      <xsl:attribute name="class">
        <xsl:text>TableControl</xsl:text>
      </xsl:attribute>
      <xsl:attribute name="style">
        <xsl:apply-templates select="." mode="css-display" />
      </xsl:attribute>
      <xsl:element name="table">
        <xsl:attribute name="class">borderfill-<xsl:value-of select="TableBody/@borderfill-id"/></xsl:attribute>
        <xsl:attribute name="cellspacing"><xsl:value-of select="TableBody/@cellspacing"/></xsl:attribute>
        <xsl:attribute name="style">
          <xsl:apply-templates select="." mode="css-width" />
          <xsl:apply-templates select="." mode="table-border" />
        </xsl:attribute>
        <xsl:apply-templates />
      </xsl:element>
    </xsl:element>
  </xsl:template>

  <xsl:template match="TableControl[@inline='0']">
    <xsl:element name="table">
      <xsl:attribute name="class">
        <xsl:text>TableControl</xsl:text>
        <xsl:text> </xsl:text>
        <xsl:text>borderfill-</xsl:text>
        <xsl:value-of select="TableBody/@borderfill-id"/>
      </xsl:attribute>
      <xsl:attribute name="cellspacing"><xsl:value-of select="TableBody/@cellspacing"/></xsl:attribute>
      <xsl:attribute name="style">
        <xsl:apply-templates select="." mode="css-width" />
        <xsl:apply-templates select="." mode="extendedcontrol-hpos" />
        <xsl:apply-templates select="." mode="table-border" />
      </xsl:attribute>
      <xsl:apply-templates />
    </xsl:element>
  </xsl:template>

  <xsl:template match="TableControl" mode="table-border">
    <xsl:call-template name="css-declaration">
      <xsl:with-param name="property">border-collapse</xsl:with-param>
      <xsl:with-param name="value">collapse</xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="TableCaption">
    <xsl:element name="caption">
      <xsl:attribute name="class">TableCaption</xsl:attribute>
      <xsl:attribute name="style">
        <xsl:choose>
          <xsl:when test="@position = 'top'">
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">caption-side</xsl:with-param>
              <xsl:with-param name="value" select="@position" />
            </xsl:call-template>
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">margin-bottom</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <xsl:with-param name="hwpunit" select="@separation" />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">width</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <xsl:with-param name="hwpunit" select="@width" />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
          </xsl:when>
          <xsl:when test="@position = 'bottom'">
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">caption-side</xsl:with-param>
              <xsl:with-param name="value" select="@position" />
            </xsl:call-template>
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">margin-top</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <xsl:with-param name="hwpunit" select="@separation" />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">width</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <xsl:with-param name="hwpunit" select="@width" />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
          </xsl:when>
          <xsl:otherwise>
            <xsl:text>/* </xsl:text>
            <xsl:text>not supported @position: </xsl:text>
            <xsl:value-of select="@position" />
            <xsl:text> */&#10;</xsl:text>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
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
      <xsl:attribute name="style">
        <xsl:call-template name="css-declaration">
          <xsl:with-param name="property">width</xsl:with-param>
          <xsl:with-param name="value">
            <xsl:call-template name="hwpunit-to-mm">
              <xsl:with-param name="hwpunit" select="@width" />
            </xsl:call-template>
          </xsl:with-param>
        </xsl:call-template>
        <xsl:call-template name="css-declaration">
          <xsl:with-param name="property">height</xsl:with-param>
          <xsl:with-param name="value">
            <xsl:call-template name="hwpunit-to-mm">
              <xsl:with-param name="hwpunit" select="@height" />
            </xsl:call-template>
          </xsl:with-param>
        </xsl:call-template>
        <xsl:call-template name="css-declaration">
          <xsl:with-param name="property">padding</xsl:with-param>
          <xsl:with-param name="value">
            <xsl:call-template name="hwpunit-to-mm">
              <xsl:with-param name="hwpunit" select="@padding-top" />
            </xsl:call-template>
            <xsl:text> </xsl:text>
            <xsl:call-template name="hwpunit-to-mm">
              <xsl:with-param name="hwpunit" select="@padding-right" />
            </xsl:call-template>
            <xsl:text> </xsl:text>
            <xsl:call-template name="hwpunit-to-mm">
              <xsl:with-param name="hwpunit" select="@padding-bottom" />
            </xsl:call-template>
            <xsl:text> </xsl:text>
            <xsl:call-template name="hwpunit-to-mm">
              <xsl:with-param name="hwpunit" select="@padding-left" />
            </xsl:call-template>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:attribute>
      <xsl:attribute name="rowspan"><xsl:value-of select="@rowspan"/></xsl:attribute>
      <xsl:attribute name="colspan"><xsl:value-of select="@colspan"/></xsl:attribute>
      <xsl:apply-templates />
    </xsl:element>
  </xsl:template>

  <xsl:template match="GShapeObjectControl[@inline='1']">
    <xsl:element name="span">
      <xsl:attribute name="class">GShapeObjectControl</xsl:attribute>
      <xsl:attribute name="style">
        <xsl:apply-templates select="." mode="css-width" />
        <xsl:apply-templates select="." mode="css-display" />
      </xsl:attribute>
      <xsl:apply-templates />
    </xsl:element>
  </xsl:template>

  <xsl:template match="GShapeObjectControl[@inline='0']">
    <xsl:element name="div">
      <xsl:attribute name="class">GShapeObjectControl</xsl:attribute>
      <xsl:attribute name="style">
        <xsl:apply-templates select="." mode="css-width" />
        <xsl:apply-templates select="." mode="extendedcontrol-hpos" />
      </xsl:attribute>
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
    <xsl:call-template name="css-declaration">
      <xsl:with-param name="property">width</xsl:with-param>
      <xsl:with-param name="value">
        <xsl:call-template name="hwpunit-to-mm">
          <xsl:with-param name="hwpunit" select="@width" />
        </xsl:call-template>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="ShapeComponent" mode="css-height">
    <xsl:call-template name="css-declaration">
      <xsl:with-param name="property">height</xsl:with-param>
      <xsl:with-param name="value">
        <xsl:call-template name="hwpunit-to-mm">
          <xsl:with-param name="hwpunit" select="@height" />
        </xsl:call-template>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="TableControl[@inline='1']|GShapeObjectControl[@inline='1']" mode="css-display">
    <xsl:call-template name="css-declaration">
      <xsl:with-param name="property">display</xsl:with-param>
      <xsl:with-param name="value">inline-block</xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="TableControl|GShapeObjectControl" mode="css-width">
    <xsl:call-template name="css-declaration">
      <xsl:with-param name="property">width</xsl:with-param>
      <xsl:with-param name="value">
        <xsl:call-template name="hwpunit-to-mm">
          <xsl:with-param name="hwpunit" select="@width" />
        </xsl:call-template>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="TableControl|GShapeObjectControl" mode="extendedcontrol-hpos">
    <xsl:variable name="paragraph" select="../.." />
    <xsl:variable name="parashape_pos" select="number($paragraph/@parashape-id) + 1" />
    <xsl:variable name="parashape" select="//ParaShape[$parashape_pos]" />
    <xsl:variable name="columnset" select="$paragraph/.." />
    <xsl:variable name="section" select="$columnset/.." />
    <xsl:variable name="pagedef" select="$section/PageDef" />
    <xsl:text>/*</xsl:text>
    <xsl:text> hrelto: </xsl:text>
    <xsl:value-of select="@hrelto" />
    <xsl:text> halign: </xsl:text>
    <xsl:value-of select="@halign" />
    <xsl:text>*/</xsl:text>
    <xsl:choose>
      <!-- 문단 -->
      <xsl:when test="@hrelto = 'paragraph'">
        <xsl:choose>
          <!-- 왼쪽으로부터 -->
          <xsl:when test="@halign = 'left'">
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">margin-left</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <xsl:with-param name="hwpunit" select="$parashape/@doubled-margin-left div 2 + @margin-left + @x" />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
          </xsl:when>
          <!-- 오른쪽으로부터 -->
          <xsl:when test="@halign = 'right'">
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">margin-left</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <!--
                  (종이 넓이)                             : 종이 x축에서
                  - (쪽 오른쪽 여백) - (문단 오른쪽 여백) : 문단 맨 오른쪽
                  - (@x)                                  : x만큼 왼쪽으로
                  - (개체 오른쪽 여백) - (개체 넓이)      : 개체 맨 왼쪽
                  - (쪽 왼쪽 여백)                        : 쪽 x축으로
                  -->
                  <xsl:with-param name="hwpunit" select="
                    $pagedef/@width
                    - $pagedef/@right-offset - $parashape/@doubled-margin-right div 2
                    - @x
                    - @margin-right - @width
                    - $pagedef/@left-offset
                    " />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
          </xsl:when>
          <!-- 가운데로부터 -->
          <xsl:when test="@halign = 'center'">
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">margin-left</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <!--
                  (종이 넓이 - 쪽 양쪽 여백 - 문단 양쪽 여백) / 2 : 문단 중간
                  - (개체 넓이 / 2)                               : 개체 너비 절반만큼 왼쪽
                  + (@x)                                          : x만큼 오른쪽
                  + (문단 왼쪽 여백)                              : 문단 x 축에서 쪽 x축으로
                  -->
                  <xsl:with-param name="hwpunit" select="
                    ($pagedef/@width - $pagedef/@left-offset - $pagedef/@right-offset) div 2
                    - @width div 2
                    + @x
                    + $parashape/@doubled-margin-left div 2
                    " />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
          </xsl:when>
        </xsl:choose>
      </xsl:when>
      <!-- 단 -->
      <xsl:when test="@hrelto = 'column'">
        <xsl:choose>
          <!-- 왼쪽으로부터 -->
          <xsl:when test="@halign = 'left'">
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">margin-left</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <xsl:with-param name="hwpunit" select="@margin-left + @x" />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
          </xsl:when>
          <!-- 오른쪽으로부터 -->
          <xsl:when test="@halign = 'right'">
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">margin-left</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <!--
                  (종이 넓이)                             : 종이 x축에서
                  - (쪽 오른쪽 여백)                      : 단 맨 오른쪽
                  - (@x)                                  : x만큼 왼쪽으로
                  - (개체 오른쪽 여백) - (개체 넓이)      : 개체 맨 왼쪽
                  - (쪽 왼쪽 여백)                        : 쪽 x축으로
                  -->
                  <xsl:with-param name="hwpunit" select="
                    $pagedef/@width
                    - $pagedef/@right-offset
                    - @x
                    - @margin-right - @width
                    - $pagedef/@left-offset
                    " />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
          </xsl:when>
          <!-- 가운데로부터 -->
          <xsl:when test="@halign = 'center'">
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">margin-left</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <!--
                  (종이 넓이 - 쪽 양쪽 여백) / 2     : 쪽 중간
                  - (개체 넓이 / 2)                  : 개체 너비 절반만큼 왼쪽
                  + (@x)                             : x만큼 오른쪽
                  -->
                  <xsl:with-param name="hwpunit" select="
                    ($pagedef/@width - $pagedef/@left-offset - $pagedef/@right-offset) div 2
                    - @width div 2
                    + @x
                    " />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
          </xsl:when>
        </xsl:choose>
      </xsl:when>
      <!-- 쪽 -->
      <xsl:when test="@hrelto = 'page'">
        <xsl:choose>
          <!-- 왼쪽으로부터 -->
          <xsl:when test="@halign = 'left'">
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">margin-left</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <xsl:with-param name="hwpunit" select="@margin-left + @x" />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
          </xsl:when>
          <!-- 오른쪽으로부터 -->
          <xsl:when test="@halign = 'right'">
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">margin-left</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <!--
                  (종이 넓이)                             : 종이 x축에서
                  - (쪽 오른쪽 여백)                      : 쪽 맨 오른쪽
                  - (@x)                                  : x만큼 왼쪽으로
                  - (개체 오른쪽 여백) - (개체 넓이)      : 개체 맨 왼쪽
                  - (쪽 왼쪽 여백)                        : 쪽 x축으로
                  -->
                  <xsl:with-param name="hwpunit" select="
                    $pagedef/@width
                    - $pagedef/@right-offset
                    - @x
                    - @margin-right - @width
                    - $pagedef/@left-offset
                    " />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
          </xsl:when>
          <!-- 가운데로부터 -->
          <xsl:when test="@halign = 'center'">
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">margin-left</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <!--
                  (종이 넓이 - 쪽 양쪽 여백) / 2     : 쪽 중간
                  - (개체 넓이 / 2)                  : 개체 너비 절반만큼 왼쪽
                  + (@x)                             : x만큼 오른쪽
                  -->
                  <xsl:with-param name="hwpunit" select="
                    ($pagedef/@width - $pagedef/@left-offset - $pagedef/@right-offset) div 2
                    - @width div 2
                    + @x
                    " />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
          </xsl:when>
        </xsl:choose>
      </xsl:when>
      <!-- 종이 -->
      <xsl:when test="@hrelto = 'paper'">
        <xsl:choose>
          <!-- 왼쪽으로부터 -->
          <xsl:when test="@halign = 'left'">
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">margin-left</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <xsl:with-param name="hwpunit" select="@margin-left + @x - $pagedef/@left-offset" />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
          </xsl:when>
          <!-- 오른쪽으로부터 -->
          <xsl:when test="@halign = 'right'">
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">margin-left</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <!--
                  (종이 넓이)                        : 종이 x축에서, 종이 맨 오른쪽
                  - (@x)                             : x만큼 왼쪽
                  - (개체 오른쪽 여백) - (개체 넓이) : 개체 맨 왼쪽
                  - (쪽 왼쪽 여백)                   : 쪽 x축으로
                  -->
                  <xsl:with-param name="hwpunit" select="
                    $pagedef/@width
                    - @x
                    - @margin-right - @width
                    - $pagedef/@left-offset
                    " />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
          </xsl:when>
          <!-- 가운데로부터 -->
          <xsl:when test="@halign = 'center'">
            <xsl:call-template name="css-declaration">
              <xsl:with-param name="property">margin-left</xsl:with-param>
              <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                  <!--
                  (종이 넓이 / 2)                    : 종이 x축에서, 종이 가운데
                  - (개체 넓이 / 2)                  : 개체 너비 절반만큼 왼쪽
                  + (@x)                             : x만큼 오른쪽
                  - (쪽 왼쪽 여백)                   : 쪽 x축으로
                  -->
                  <xsl:with-param name="hwpunit" select="
                    $pagedef/@width div 2
                    - @width div 2
                    + @x
                    - $pagedef/@left-offset
                    " />
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
          </xsl:when>
        </xsl:choose>
      </xsl:when>
    </xsl:choose>
  </xsl:template>
</xsl:stylesheet>
