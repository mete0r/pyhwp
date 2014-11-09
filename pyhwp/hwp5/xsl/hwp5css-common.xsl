<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" media-type="text/css" encoding="utf-8" indent="no" />
    <xsl:template match="IdMappings" mode="content">
        /* Styles */
        <xsl:for-each select="Style">
            p.<xsl:value-of select="translate(@name, ' ', '-')"/> {
            }
        </xsl:for-each>

        /* Paragraph attributes */
        <xsl:for-each select="ParaShape">
            .parashape-<xsl:number value="position()-1" /> {
                margin:
                    <xsl:value-of select="@doubled-margin-top div 100 div 2"/>pt
                    <xsl:value-of select="@doubled-margin-right div 100 div 2"/>pt
                    <xsl:value-of select="@doubled-margin-bottom div 100 div 2"/>pt
                    <xsl:value-of select="@doubled-margin-left div 100 div 2"/>pt;
                <xsl:apply-templates select="." mode="css-text-align" />
                <xsl:apply-templates select="." mode="css-text-indent" />
            }
            .parashape-<xsl:number value="position()-1" /> &gt; span {
            <xsl:choose>
                <xsl:when test="@linespacing-type = 'ratio'">
                line-height: <xsl:value-of select="@linespacing"/>%;
                </xsl:when>
            </xsl:choose>
            }
        </xsl:for-each>

        /* Text attributes */
        <xsl:for-each select="CharShape">
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
                <xsl:apply-templates select="." mode="css-text-decoration" />
            }
        </xsl:for-each>
        <xsl:for-each select="BorderFill">
            .borderfill-<xsl:number value="position()" /> {
                border-top: <xsl:apply-templates select="Border[@attribute-name='top']" mode="cssborder"/>;
                border-right: <xsl:apply-templates select="Border[@attribute-name='right']" mode="cssborder"/>;
                border-bottom: <xsl:apply-templates select="Border[@attribute-name='bottom']" mode="cssborder"/>;
                border-left: <xsl:apply-templates select="Border[@attribute-name='left']" mode="cssborder"/>;
            }
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="Border" mode="cssborder"> 1px solid <xsl:value-of select="@color" />/* width:<xsl:value-of select="@width" /> style:<xsl:value-of select="@style" /> */ </xsl:template>

    <xsl:template match="SectionDef" mode="style-content">
        .Section-<xsl:value-of select="position()-1" /> {
          width: <xsl:value-of select="PageDef/@width div 100" />pt;
          margin-left: <xsl:value-of select="PageDef/@left-offset div 100" />pt;
          margin-right <xsl:value-of select="PageDef/@right-offset div 100" />pt;
        }
    </xsl:template>

    <xsl:template match="ParaShape" mode="css-text-align">
        text-align: <xsl:apply-templates select="." mode="css-text-align-value" />;
    </xsl:template>

    <xsl:template match="ParaShape" mode="css-text-align-value">
        <xsl:choose>
            <xsl:when test="@align = 'center'">center</xsl:when>
            <xsl:when test="@align = 'left'">left</xsl:when>
            <xsl:when test="@align = 'right'">right</xsl:when>
            <xsl:when test="@align = 'both'">justify</xsl:when>
            <xsl:otherwise>justify</xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="ParaShape" mode="css-text-indent">
        text-indent: <xsl:apply-templates select="." mode="css-text-indent-value" />;
        <xsl:if test="@indent &lt; 0">
        padding-left: <xsl:value-of select="@indent div 100 div 2 * -1" />pt;
        </xsl:if>
    </xsl:template>

    <xsl:template match="ParaShape" mode="css-text-indent-value">
        <!-- @indent seems to be doubled -->
        <xsl:value-of select="@indent div 100 div 2" />pt
    </xsl:template>

    <xsl:template match="CharShape" mode="css-text-decoration">
        <xsl:choose>
            <xsl:when test="@underline = 'underline'">
                text-decoration: underline;
                text-decoration-style: <xsl:apply-templates select="." mode="css-text-decoration-style-value" />;
                text-decoration-color: <xsl:value-of select="@underline-color" />;
                -moz-text-decoration-style: <xsl:apply-templates select="." mode="css-text-decoration-style-value" />;
                -moz-text-decoration-color: <xsl:value-of select="@underline-color" />;
                -webkit-text-decoration-style: <xsl:apply-templates select="." mode="css-text-decoration-style-value" />;
                -webkit-text-decoration-color: <xsl:value-of select="@underline-color" />;
            </xsl:when>
            <xsl:when test="@underline = 'overline'">
                text-decoration: overline;
                text-decoration-style: <xsl:apply-templates select="." mode="css-text-decoration-style-value" />;
                text-decoration-color: <xsl:value-of select="@underline-color" />;
                -moz-text-decoration-style: <xsl:apply-templates select="." mode="css-text-decoration-style-value" />;
                -moz-text-decoration-color: <xsl:value-of select="@underline-color" />;
                -webkit-text-decoration-style: <xsl:apply-templates select="." mode="css-text-decoration-style-value" />;
                -webkit-text-decoration-color: <xsl:value-of select="@underline-color" />;
            </xsl:when>
            <xsl:when test="@underline = 'line_through'">
                text-decoration: line-through;
                text-decoration-style: <xsl:apply-templates select="." mode="css-text-decoration-style-value" />;
                text-decoration-color: <xsl:value-of select="@underline-color" />;
                -moz-text-decoration-style: <xsl:apply-templates select="." mode="css-text-decoration-style-value" />;
                -moz-text-decoration-color: <xsl:value-of select="@underline-color" />;
                -webkit-text-decoration-style: <xsl:apply-templates select="." mode="css-text-decoration-style-value" />;
                -webkit-text-decoration-color: <xsl:value-of select="@underline-color" />;
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="CharShape" mode="css-text-decoration-style-value">
        <xsl:choose>
            <xsl:when test="@underline-style = 'solid'">solid</xsl:when>
            <xsl:when test="@underline-style = 'dashed'">dashed</xsl:when>
            <xsl:when test="@underline-style = 'dotted'">dotted</xsl:when>
            <xsl:when test="@underline-style = 'dash_dot'">dashed</xsl:when>
            <xsl:when test="@underline-style = 'dash_dot_dot'">dashed</xsl:when>
            <xsl:when test="@underline-style = 'long_dashed'">dashed</xsl:when>
            <xsl:when test="@underline-style = 'large_dotted'">dotted</xsl:when>
            <xsl:when test="@underline-style = 'double'">double</xsl:when>
            <xsl:when test="@underline-style = 'lower_weighted'">double</xsl:when>
            <xsl:when test="@underline-style = 'upper_weighted'">double</xsl:when>
            <xsl:when test="@underline-style = 'middle_weighted'">double</xsl:when>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>
