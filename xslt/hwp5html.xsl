<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" encoding="utf-8" indent="yes"/>
    <xsl:template match="/">
        <xsl:text disable-output-escaping="yes">&lt;!DOCTYPE html&gt;</xsl:text>
        <html>
            <head>
                <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
                <xsl:element name="style">
                    <xsl:attribute name="type">text/css</xsl:attribute>
                    <xsl:for-each select="HwpDoc/DocInfo/IdMappings/Style">
                        .style-<xsl:value-of select="@next-style-id"/> {
                        }
                    </xsl:for-each>
                    <xsl:for-each select="HwpDoc/DocInfo/IdMappings/ParaShape">
                        .parashape-<xsl:number value="position()-1" /> {
                        <xsl:choose>
                            <xsl:when test="@linespacing-type = 'ratio'">
                                line-height: <xsl:value-of select="@linespacing-before-2007"/>%;
                            </xsl:when>
                        </xsl:choose>
                            margin:
                                <xsl:value-of select="@doubled-margin-top div 100 div 2"/>pt
                                <xsl:value-of select="@doubled-margin-right div 100 div 2"/>pt
                                <xsl:value-of select="@doubled-margin-bottom div 100 div 2"/>pt
                                <xsl:value-of select="@doubled-margin-left div 100 div 2"/>pt;
                        }
                    </xsl:for-each>
                    <xsl:for-each select="HwpDoc/DocInfo/IdMappings/CharShape">
                        .charshape-<xsl:number value="position()-1" /> {
                            /* fontface-ko <xsl:value-of select="FaceNameRef/@ko"/> */
                            color: <xsl:value-of select="@text-color"/>;
                            font-size: <xsl:value-of select="@basesize div 100"/>pt;
                            <xsl:if test="@italic = 1">
                                font-style: italic;
                            </xsl:if>
                            <xsl:if test="@bold = 1">
                                font-weight: bold;
                            </xsl:if>
                        }
                    </xsl:for-each>
                    <xsl:for-each select="HwpDoc/DocInfo/IdMappings/BorderFill">
                        .borderfill-<xsl:number value="position()" /> {
                            border-left-color: <xsl:value-of select="Border[@attribute-name='left']/@color" />;
                            border-left-style: solid; /* Border.style: <xsl:value-of select="Border[@attribute-name='left']/@style" />; */
                            border-left-width: 1px; /* Border.width: <xsl:value-of select="Border[@attribute-name='left']/@width" />; */

                            border-right-color: <xsl:value-of select="Border[@attribute-name='right']/@color" />;
                            border-right-style: solid; /* Border.style: <xsl:value-of select="Border[@attribute-name='right']/@style" />; */
                            border-right-width: 1px; /* Border.width: <xsl:value-of select="Border[@attribute-name='right']/@width" />; */

                            border-top-color: <xsl:value-of select="Border[@attribute-name='top']/@color" />;
                            border-top-style: solid; /* Border.style: <xsl:value-of select="Border[@attribute-name='top']/@style" />; */
                            border-top-width: 1px; /* Border.width: <xsl:value-of select="Border[@attribute-name='top']/@width" />; */

                            border-bottom-color: <xsl:value-of select="Border[@attribute-name='bottom']/@color" />;
                            border-bottom-style: solid; /* Border.style: <xsl:value-of select="Border[@attribute-name='bottom']/@style" />; */
                            border-bottom-width: 1px; /* Border.width: <xsl:value-of select="Border[@attribute-name='bottom']/@width" />; */
                        }
                    </xsl:for-each>

                </xsl:element>
            </head>
            <xsl:element name="body">
                <xsl:for-each select="HwpDoc/BodyText">
                    <xsl:apply-templates />
                </xsl:for-each>
            </xsl:element>
        </html>
    </xsl:template>

    <xsl:template match="Paragraph">
        <xsl:element name="p">
            <xsl:attribute name="class"><xsl:value-of select="concat('style-',@style-id)"/> parashape-<xsl:value-of select="@parashape-id"/></xsl:attribute>
            <xsl:apply-templates />
        </xsl:element>
    </xsl:template>

    <xsl:template match="ControlChar"><xsl:value-of select="@char"/></xsl:template>

    <xsl:template match="Text">
        <xsl:element name="span"><xsl:attribute name="class">charshape-<xsl:value-of select="@charshape-id"/></xsl:attribute><xsl:value-of select="text()"/></xsl:element>
    </xsl:template>

    <xsl:template match="TableCaption">
        <xsl:element name="caption">
            <xsl:attribute name="class">TableCaption</xsl:attribute>
            <xsl:apply-templates />
        </xsl:element>
    </xsl:template>

    <xsl:template match="TableControl">
        <xsl:element name="table">
            <xsl:attribute name="class">borderfill-<xsl:value-of select="TableBody/@borderfill-id"/></xsl:attribute>
            <xsl:attribute name="cellspacing"><xsl:value-of select="TableBody/@cellspacing"/></xsl:attribute>
            <xsl:attribute name="style">border-collapse:collapse;</xsl:attribute>
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
            <xsl:attribute name="style">width:<xsl:value-of select="@width div 100"/>pt; height:<xsl:value-of select="@height div 100"/>pt;</xsl:attribute>
            <xsl:attribute name="rowspan"><xsl:value-of select="@rowspan"/></xsl:attribute>
            <xsl:attribute name="colspan"><xsl:value-of select="@colspan"/></xsl:attribute>
            <xsl:apply-templates />
        </xsl:element>
    </xsl:template>

    <xsl:template match="GShapeObjectControl">
        <xsl:element name="div">
            <xsl:attribute name="class">GShapeObject</xsl:attribute>
            <xsl:apply-templates />
        </xsl:element>
    </xsl:template>

    <xsl:template match="ShapePicture">
        <xsl:variable name="binpath" select="'bindata/'"/>
        <xsl:variable name="bindataid" select="PictureInfo/@bindata-id"/>
        <xsl:variable name="bindata" select="/HwpDoc/DocInfo/IdMappings/BinData[number($bindataid)]"/>
        <xsl:element name="img">
            <xsl:choose>
                <xsl:when test="$bindata/BinEmbedded">
                    <xsl:attribute name="src"><xsl:value-of select="$binpath"/><xsl:value-of select="$bindata/BinEmbedded/@storage-id"/>.<xsl:value-of select="$bindata/BinEmbedded/@ext"/></xsl:attribute>
                </xsl:when>
            </xsl:choose>
            <xsl:attribute name="style">width:<xsl:value-of select="../@width div 100"/>pt; height:<xsl:value-of select="../@height div 100"/>pt;</xsl:attribute>
        </xsl:element>
    </xsl:template>
</xsl:stylesheet>
