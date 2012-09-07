<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >
  <xsl:output method="xml" encoding="utf-8" indent="yes"
      doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
      doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
      />
  <xsl:template match="/binspec">
    <xsl:element name="html">
      <xsl:element name="head">
	<xsl:element name="meta">
	  <xsl:attribute name="http-equiv">Content-Type</xsl:attribute>
	  <xsl:attribute name="content">text/xhtml; charset=utf-8</xsl:attribute>
	</xsl:element>
	<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js"></script>
	<xsl:element name="script">
	  <xsl:attribute name="type">text/javascript</xsl:attribute>
	  <xsl:text>
	    $(document).ready(function(){
	      $('a.toggle-definition').parent().parent().siblings().css('display', 'none');
	      $('a.toggle-definition').click(function(){
		$(this).parent().parent().siblings().toggle();
	      });
	    });
	  </xsl:text>
	</xsl:element>
	<xsl:element name="style">
	  <xsl:attribute name="type">text/css</xsl:attribute>
	  <xsl:text>
	    table.StructType {
	      width: 100%;
	    }
	    table.simple {
	      border: 1px solid black;
	      border-collapse: collapse;
	    }
	    table.simple th ,
	    table.simple td {
	      border: 1px solid black;
	      padding: 1em;
	    }
	    thead tr.StructType-name th {
	      background-color: #ccc;
	    }
	    tr.extension-header th {
	      background-color: #ddd;
	    }
	    tr.extension-header th .condition {
	      font-weight: normal;
	    }
	    tr.extends-header th {
	      background-color: #eee;
	      color: #777;
	      font-weight: normal;
	    }
	    table.SelectiveType,
	    table.SelectiveType th,
	    table.SelectiveType td {
	      border: 0;
	      padding: 0;
	    }
	    table.EnumType {
	      border: 0;
	      width: 100%;
	    }
	    table.EnumType tr.name th {
	      border: 0;
	    }
	    table.FlagsType {
	      border: 0;
	      width: 100%;
	    }
	    table.FlagsType tr.name th {
	      border: 0;
	    }
	    a.toggle-definition {
	      text-decoration: underline;
	      cursor: pointer;
	      color: blue;
	    }
	  </xsl:text>
	</xsl:element>
      </xsl:element>
      <xsl:element name="body">
	<xsl:element name="h1">
	  hwp5spec
	</xsl:element>
	<xsl:element name="table">
	  <xsl:element name="tr">
	    <xsl:element name="th">
	      Version:
	    </xsl:element>
	    <xsl:element name="td">
	      <xsl:value-of select="@version"/>
	    </xsl:element>
	  </xsl:element>
	</xsl:element>
	<xsl:element name="h2">Records</xsl:element>
	<xsl:call-template name="toc-Records" />
	<xsl:apply-templates select="TagModel" mode="define" />
	<xsl:element name="h2">Structs</xsl:element>
	<xsl:apply-templates select="StructType" mode="define" />
	<xsl:element name="h2">Primitives</xsl:element>
	<xsl:element name="table">
	  <xsl:attribute name="class">simple</xsl:attribute>
	  <xsl:element name="tr">
	    <xsl:element name="th">
	      name
	    </xsl:element>
	    <xsl:element name="th">
	      size
	    </xsl:element>
	    <xsl:element name="th">
	      binfmt
	    </xsl:element>
	  </xsl:element>
	  <xsl:apply-templates select="PrimitiveType" mode="define" />
	</xsl:element>
      </xsl:element>
    </xsl:element>
  </xsl:template>
  <xsl:template name="toc-Records" >
    <xsl:element name="table">
      <xsl:attribute name="class">toc simple</xsl:attribute>
      <xsl:for-each select="TagModel">
	<xsl:element name="tr">
	  <xsl:element name="td">
	    <xsl:value-of select="@tag_id" />
	  </xsl:element>
	  <xsl:element name="td">
	    <xsl:element name="a">
	      <xsl:attribute name="href">
		<xsl:text>#</xsl:text>
		<xsl:value-of select="@name" />
	      </xsl:attribute>
	      <xsl:value-of select="@name" />
	    </xsl:element>
	  </xsl:element>
	</xsl:element>
      </xsl:for-each>
    </xsl:element>
  </xsl:template>

  <xsl:template match="TagModel" mode="define">
    <xsl:element name="div">
      <xsl:element name="h3">
	<xsl:call-template name="anchor-with-name" />
      </xsl:element>
      <xsl:element name="table">
	<xsl:attribute name="class">StructType simple</xsl:attribute>
	<xsl:for-each select="base">
	  <xsl:variable name="name" select="@name" />
	  <xsl:variable name="struct" select="//StructType[@name=$name]" />
	  <xsl:for-each select="$struct[1]">
	    <xsl:apply-templates select="." mode="thead" />
	    <xsl:apply-templates select="extends" mode="tbody" />
	    <xsl:apply-templates select="." mode="tbody" />
	  </xsl:for-each>
	</xsl:for-each>
	<xsl:for-each select="extension">
	  <xsl:element name="tbody">
	    <xsl:apply-templates select="." mode="tr" />
	    <xsl:apply-templates select="extends" mode="tr" />
	    <xsl:apply-templates select="member" mode="tr" />
	  </xsl:element>
	</xsl:for-each>
      </xsl:element>
    </xsl:element>
  </xsl:template>

  <xsl:template match="StructType" mode="define">
    <xsl:element name="div">
      <xsl:element name="h3">
	<xsl:call-template name="anchor-with-name" />
      </xsl:element>
      <xsl:element name="table">
	<xsl:attribute name="class">StructType simple</xsl:attribute>
	<xsl:apply-templates select="." mode="thead" />
	<xsl:apply-templates select="extends" mode="tbody" />
	<xsl:apply-templates select="." mode="tbody" />
      </xsl:element>
    </xsl:element>
  </xsl:template>

  <xsl:template match="StructType" mode="thead">
    <xsl:element name="thead">
      <xsl:element name="tr">
	<xsl:attribute name="class">StructType-name</xsl:attribute>
	<xsl:element name="th">
	  <xsl:attribute name="colspan">4</xsl:attribute>
	  <xsl:value-of select="@name" />
	</xsl:element>
      </xsl:element>
      <xsl:element name="tr">
	<xsl:element name="th">name</xsl:element>
	<xsl:element name="th">type</xsl:element>
	<xsl:element name="th">condition</xsl:element>
	<xsl:element name="th">version</xsl:element>
      </xsl:element>
    </xsl:element>
  </xsl:template>

  <xsl:template match="StructType" mode="tbody">
    <xsl:element name="tbody">
      <xsl:apply-templates select="member" mode="tr"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="extends" mode="tbody">
    <xsl:element name="tbody">
      <xsl:apply-templates select="." mode="tr" />
      <xsl:variable name="extends-name" select="@name" />
      <xsl:variable name="struct" select="//StructType[@name=$extends-name]" />
      <xsl:apply-templates select="$struct/members" mode="tr" />
    </xsl:element>
  </xsl:template>

  <xsl:template match="extends" mode="tr">
    <xsl:element name="tr">
      <xsl:attribute name="class">extends-header</xsl:attribute>
      <xsl:element name="th">
	<xsl:attribute name="colspan">4</xsl:attribute>
	<xsl:text>(see </xsl:text>
	<xsl:call-template name="reference-type-with-name">
	  <xsl:with-param name="type-name"><xsl:value-of select="@name" /></xsl:with-param>
	</xsl:call-template>
	<xsl:text> members)</xsl:text>
      </xsl:element>
    </xsl:element>
  </xsl:template>

  <xsl:template match="extension" mode="tr" >
    <xsl:element name="tr">
      <xsl:attribute name="class">extension-header</xsl:attribute>
      <xsl:element name="th">
	<xsl:attribute name="colspan">4</xsl:attribute>
	<xsl:text>Extension: </xsl:text>
	<xsl:call-template name="toggle-definition">
	  <xsl:with-param name="text" select="@name" />
	</xsl:call-template>
	<xsl:element name="div">
	  <xsl:attribute name="class">condition</xsl:attribute>
	  (if <xsl:value-of select="condition" />)
	</xsl:element>
      </xsl:element>
    </xsl:element>
  </xsl:template>

  <xsl:template match="member" mode="tr">
    <xsl:element name="tr">
      <xsl:attribute name="class">member</xsl:attribute>
      <xsl:element name="th">
	<xsl:value-of select="@name" />
      </xsl:element>
      <xsl:element name="td">
	<xsl:apply-templates select="type-ref" />
      </xsl:element>
      <xsl:element name="td">
	<xsl:value-of select="condition" />
      </xsl:element>
      <xsl:element name="td">
	<xsl:value-of select="@version" />
      </xsl:element>
    </xsl:element>
  </xsl:template>

  <xsl:template name="anchor-with-name">
    <xsl:element name="a">
      <xsl:attribute name="name">
	<xsl:value-of select="@name" />
      </xsl:attribute>
      <xsl:attribute name="href">
	<xsl:text>#</xsl:text>
	<xsl:value-of select="@name" />
      </xsl:attribute>
      <xsl:value-of select="@name" />
    </xsl:element>
  </xsl:template>

  <xsl:template match="type-ref[@meta='EnumType']">
    <xsl:variable name="name" select="@name" />
    <xsl:variable name="scope" select="@scope" />
    <xsl:variable name="EnumType" select="//EnumType[@name=$name and @scope=$scope]" />
    <xsl:apply-templates select="$EnumType" mode="define" />
  </xsl:template>

  <xsl:template match="type-ref[@meta='FlagsType']">
    <xsl:apply-templates select="FlagsType" mode="define" />
  </xsl:template>

  <xsl:template match="type-ref[@meta='FixedArrayType']">
    <xsl:apply-templates select="FixedArrayType" mode="define" />
  </xsl:template>

  <xsl:template match="type-ref[@meta='VariableLengthArrayType']">
    <xsl:apply-templates select="VariableLengthArrayType" mode="define" />
  </xsl:template>

  <xsl:template match="type-ref[@meta='X_ARRAY']">
    <xsl:apply-templates select="XArrayType" mode="define" />
  </xsl:template>

  <xsl:template match="type-ref[@meta='SelectiveType']">
    <xsl:apply-templates select="SelectiveType" mode="define" />
  </xsl:template>

  <xsl:template match="type-ref">
    <xsl:call-template name="reference-type-with-name">
      <xsl:with-param name="type-name">
	<xsl:value-of select="@name"/>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="reference-type-with-name">
    <xsl:param name="type-name" />
    <xsl:if test="$type-name != 'int'">
      <xsl:element name="a">
	<xsl:attribute name="href">#<xsl:value-of select="$type-name" /></xsl:attribute>
	<xsl:value-of select="$type-name" />
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <xsl:template name="reference-struct-type">
    <xsl:element name="a">
      <xsl:attribute name="href">#<xsl:value-of select="." /></xsl:attribute>
      <xsl:value-of select="." />
    </xsl:element>
  </xsl:template>

  <xsl:template match="FlagsType" mode="define">
    <xsl:element name="table">
      <xsl:attribute name="class">FlagsType simple</xsl:attribute>
      <xsl:element name="tr">
	<xsl:attribute name="class">name</xsl:attribute>
	<xsl:element name="th">
	  <xsl:attribute name="colspan">3</xsl:attribute>
	  <xsl:variable name="title" select="concat('Flags(', base/type-ref/@name, ')')" />
	  <xsl:call-template name="toggle-definition">
	    <xsl:with-param name="text" select="$title" />
	  </xsl:call-template>
	</xsl:element>
      </xsl:element>
      <xsl:element name="tr">
	<xsl:element name="th">bits</xsl:element>
	<xsl:element name="th">name</xsl:element>
	<xsl:element name="th">type</xsl:element>
      </xsl:element>
      <xsl:for-each select="BitField">
	<xsl:element name="tr">
	  <xsl:element name="td">
	    <xsl:choose>
	      <xsl:when test="@lsb = @msb">
		<xsl:value-of select="@lsb" />
	      </xsl:when>
	      <xsl:otherwise>
		<xsl:value-of select="@lsb" /> ~ <xsl:value-of select="@msb" />
	      </xsl:otherwise>
	    </xsl:choose>
	  </xsl:element>
	  <xsl:element name="th">
	    <xsl:value-of select="@name" />
	  </xsl:element>
	  <xsl:element name="td">
	    <xsl:apply-templates select="type-ref[@meta='EnumType']" />
	  </xsl:element>
	</xsl:element>
      </xsl:for-each>
    </xsl:element>
  </xsl:template>

  <xsl:template match="FixedArrayType" mode="define">
    ARRAY(<xsl:apply-templates select="item-type/type-ref" />, <xsl:value-of select="@size" />)
  </xsl:template>

  <xsl:template match="XArrayType" mode="define">
    ARRAY(<xsl:apply-templates select="item-type/type-ref" />, <xsl:value-of select="@size" />)
  </xsl:template>

  <xsl:template match="VariableLengthArrayType" mode="define">
    N_ARRAY(<xsl:apply-templates select="count-type/type-ref" />,
    <xsl:apply-templates select="item-type/type-ref" />)
  </xsl:template>

  <xsl:template match="SelectiveType" mode="define">
    if
    <xsl:value-of select="@selector" />
    is:
    <xsl:element name="ul">
      <xsl:attribute name="class">SelectiveType</xsl:attribute>
      <xsl:for-each select="selection">
	<xsl:element name="li">
	    <xsl:value-of select="@when" />; then 
	    <xsl:apply-templates select="type-ref" />
	</xsl:element>
      </xsl:for-each>
    </xsl:element>
  </xsl:template>

  <xsl:template match="EnumType" mode="define">
    <xsl:element name="table">
      <xsl:attribute name="class">EnumType simple</xsl:attribute>
      <xsl:element name="tr">
	<xsl:attribute name="class">name</xsl:attribute>
	<xsl:element name="th">
	  <xsl:attribute name="colspan">2</xsl:attribute>
	  <xsl:text>Enum </xsl:text>
	  <xsl:for-each select="@scope" >
	    <xsl:call-template name="reference-struct-type" />
	  </xsl:for-each>
	  <xsl:text>.</xsl:text>
	  <xsl:call-template name="toggle-definition">
	    <xsl:with-param name="text" select="@name" />
	  </xsl:call-template>
	</xsl:element>
      </xsl:element>
      <xsl:for-each select="item">
	<xsl:element name="tr">
	  <xsl:element name="td">
	    <xsl:value-of select="@value" />
	  </xsl:element>
	  <xsl:element name="td">
	    <xsl:value-of select="@name" />
	  </xsl:element>
	</xsl:element>
      </xsl:for-each>
    </xsl:element>
  </xsl:template>

  <xsl:template match="PrimitiveType" mode="define">
    <xsl:element name="tr">
      <xsl:element name="th">
	<xsl:call-template name="anchor-with-name" />
      </xsl:element>
      <xsl:element name="td">
	<xsl:value-of select="@size" />
      </xsl:element>
      <xsl:element name="td">
	<xsl:value-of select="binfmt" />
      </xsl:element>
    </xsl:element>
  </xsl:template>

  <xsl:template name="toggle-definition">
    <xsl:param name="text" />
    <xsl:element name="a">
      <xsl:attribute name="class">toggle-definition</xsl:attribute>
      <xsl:value-of select="$text" />
    </xsl:element>
  </xsl:template>
</xsl:stylesheet>
