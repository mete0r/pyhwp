<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" media-type="text/css" encoding="utf-8" indent="no" />
    <xsl:template match="IdMappings" mode="css-rule">
        <xsl:text>/* Styles */&#10;</xsl:text>
        <xsl:apply-templates select="Style" mode="css-rule" />
        <xsl:text>/* Paragraph attributes */&#10;</xsl:text>
        <xsl:apply-templates select="ParaShape" mode="css-rule" />
        <xsl:text>/* Text attributes */&#10;</xsl:text>
        <xsl:apply-templates select="CharShape" mode="css-rule" />
        <xsl:apply-templates select="BorderFill" mode="css-rule" />
    </xsl:template>

    <xsl:template match="Style" mode="css-rule">
        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector">
                <xsl:text>p.</xsl:text>
                <xsl:value-of select="translate(@name, ' ', '-')"/>
            </xsl:with-param>
            <xsl:with-param name="declarations"></xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="ParaShape" mode="css-rule">
        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector">
                <xsl:text>.parashape-</xsl:text>
                <xsl:number value="position()-1" />
            </xsl:with-param>
            <xsl:with-param name="declarations">
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">margin</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:value-of select="@doubled-margin-top div 100 div 2"/>
                        <xsl:text>pt </xsl:text>
                        <xsl:value-of select="@doubled-margin-right div 100 div 2"/>
                        <xsl:text>pt </xsl:text>
                        <xsl:value-of select="@doubled-margin-bottom div 100 div 2"/>
                        <xsl:text>pt </xsl:text>
                        <xsl:value-of select="@doubled-margin-left div 100 div 2"/>
                        <xsl:text>pt</xsl:text>
                    </xsl:with-param>
                </xsl:call-template>
                <xsl:apply-templates select="." mode="text-align" />
                <xsl:apply-templates select="." mode="text-indent" />
                <xsl:choose>
                    <xsl:when test="@linespacing-type = 'ratio'">
                        <xsl:call-template name="css-declaration">
                            <xsl:with-param name="property">min-height</xsl:with-param>
                            <xsl:with-param name="value">
                                <xsl:value-of select="@linespacing div 100" />
                                <xsl:text>em</xsl:text>
                            </xsl:with-param>
                        </xsl:call-template>
                    </xsl:when>
                </xsl:choose>
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector">
                <xsl:text>.parashape-</xsl:text>
                <xsl:number value="position()-1" />
                <xsl:text> &gt; span</xsl:text>
            </xsl:with-param>
            <xsl:with-param name="declarations">
                <xsl:choose>
                    <xsl:when test="@linespacing-type = 'ratio'">
                        <xsl:call-template name="css-declaration">
                            <xsl:with-param name="property">line-height</xsl:with-param>
                            <xsl:with-param name="value">
                                <xsl:value-of select="@linespacing div 100"/>
                            </xsl:with-param>
                        </xsl:call-template>
                    </xsl:when>
                </xsl:choose>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="CharShape" mode="css-rule">
        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector">
                <xsl:text>.charshape-</xsl:text>
                <xsl:number value="position()-1" />
            </xsl:with-param>
            <xsl:with-param name="declarations">

                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">color</xsl:with-param>
                    <xsl:with-param name="value"><xsl:value-of select="@text-color" /></xsl:with-param>
                </xsl:call-template>

                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">font-family</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:apply-templates select="FontFace" mode="css-declaration-font-family-value" />
                    </xsl:with-param>
                </xsl:call-template>

                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">font-size</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:value-of select="@basesize div 100"/>
                        <xsl:text>pt</xsl:text>
                    </xsl:with-param>
                </xsl:call-template>

                <xsl:if test="@italic = 1">
                    <xsl:call-template name="css-declaration">
                        <xsl:with-param name="property">font-style</xsl:with-param>
                        <xsl:with-param name="value">italic</xsl:with-param>
                    </xsl:call-template>
                </xsl:if>

                <xsl:if test="@bold = 1">
                    <xsl:call-template name="css-declaration">
                        <xsl:with-param name="property">font-weight</xsl:with-param>
                        <xsl:with-param name="value">bold</xsl:with-param>
                    </xsl:call-template>
                </xsl:if>

                <xsl:apply-templates select="." mode="text-decoration" />

            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="FontFace" mode="css-declaration-font-family-value">
        <xsl:variable name="facenamebaseko" select="1" />
        <xsl:variable name="facenamebaseen" select="$facenamebaseko + //IdMappings/@ko-fonts" />
        <xsl:variable name="facenamebasecn" select="$facenamebaseen + //IdMappings/@en-fonts" />
        <xsl:variable name="facenamebasejp" select="$facenamebasecn + //IdMappings/@cn-fonts" />
        <xsl:variable name="facenamebaseot" select="$facenamebasejp + //IdMappings/@other-fonts" />
        <xsl:variable name="facenamebasesy" select="$facenamebaseot + //IdMappings/@symbol-fonts" />
        <xsl:variable name="facenamebaseus" select="$facenamebasesy + //IdMappings/@user-fonts" />
        <xsl:text>/*</xsl:text>
        <xsl:text> </xsl:text>
        <xsl:text>base: </xsl:text>
        <xsl:value-of select="$facenamebaseko" />
        <xsl:text> </xsl:text>
        <xsl:value-of select="$facenamebaseen" />
        <xsl:text> </xsl:text>
        <xsl:value-of select="$facenamebasecn" />
        <xsl:text> </xsl:text>
        <xsl:value-of select="$facenamebasejp" />
        <xsl:text> </xsl:text>
        <xsl:value-of select="$facenamebaseot" />
        <xsl:text> </xsl:text>
        <xsl:value-of select="$facenamebasesy" />
        <xsl:text> </xsl:text>
        <xsl:value-of select="$facenamebaseus" />
        <xsl:text> </xsl:text>
        <xsl:text>*/</xsl:text>
        <xsl:text>&#10;</xsl:text>

        <xsl:variable name="facenameidko" select="$facenamebaseko + @ko" />
        <xsl:variable name="facenameiden" select="$facenamebaseen + @en" />
        <xsl:variable name="facenameidcn" select="$facenamebasecn + @cn" />
        <xsl:variable name="facenameidjp" select="$facenamebasejp + @jp" />
        <xsl:variable name="facenameidot" select="$facenamebaseot + @other" />
        <xsl:variable name="facenameidsy" select="$facenamebasesy + @symbol" />
        <xsl:variable name="facenameidus" select="$facenamebaseus + @user" />
        <xsl:text>/*</xsl:text>
        <xsl:text> </xsl:text>
        <xsl:text>base + offset: </xsl:text>
        <xsl:value-of select="$facenameidko" />
        <xsl:text> </xsl:text>
        <xsl:value-of select="$facenameiden" />
        <xsl:text> </xsl:text>
        <xsl:value-of select="$facenameidcn" />
        <xsl:text> </xsl:text>
        <xsl:value-of select="$facenameidjp" />
        <xsl:text> </xsl:text>
        <xsl:value-of select="$facenameidot" />
        <xsl:text> </xsl:text>
        <xsl:value-of select="$facenameidsy" />
        <xsl:text> </xsl:text>
        <xsl:value-of select="$facenameidus" />
        <xsl:text> </xsl:text>
        <xsl:text>*/</xsl:text>
        <xsl:text>&#10;</xsl:text>

        <xsl:text>/*</xsl:text>
        <xsl:text> </xsl:text>
        <xsl:text>ko en cn jp other symbol user</xsl:text>
        <xsl:text> </xsl:text>
        <xsl:text>*/</xsl:text>
        <xsl:text>&#10;</xsl:text>

        <xsl:text>"</xsl:text>
        <xsl:value-of select="//FaceName[$facenameidko]/@name" />
        <xsl:text>", "</xsl:text>
        <xsl:value-of select="//FaceName[$facenameiden]/@name" />
        <xsl:text>", "</xsl:text>
        <xsl:value-of select="//FaceName[$facenameidcn]/@name" />
        <xsl:text>", "</xsl:text>
        <xsl:value-of select="//FaceName[$facenameidjp]/@name" />
        <xsl:text>", "</xsl:text>
        <xsl:value-of select="//FaceName[$facenameidot]/@name" />
        <xsl:text>", "</xsl:text>
        <xsl:value-of select="//FaceName[$facenameidsy]/@name" />
        <xsl:text>", "</xsl:text>
        <xsl:value-of select="//FaceName[$facenameidus]/@name" />
        <xsl:text>"</xsl:text>
    </xsl:template>

    <xsl:template match="BorderFill" mode="css-rule">
        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector">
                <xsl:text>.borderfill-</xsl:text>
                <xsl:number value="position()" />
            </xsl:with-param>
            <xsl:with-param name="declarations">
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">border-top</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:apply-templates select="Border[@attribute-name='top']" mode="cssborder"/>
                    </xsl:with-param>
                </xsl:call-template>

                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">border-right</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:apply-templates select="Border[@attribute-name='right']" mode="cssborder"/>
                    </xsl:with-param>
                </xsl:call-template>

                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">border-bottom</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:apply-templates select="Border[@attribute-name='bottom']" mode="cssborder"/>
                    </xsl:with-param>
                </xsl:call-template>

                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">border-left</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:apply-templates select="Border[@attribute-name='left']" mode="cssborder"/>
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="Border" mode="cssborder">
        <xsl:text>1px solid </xsl:text>
        <xsl:value-of select="@color" />
        <xsl:text>/*</xsl:text>
        <xsl:value-of select="@width" />
        <xsl:text> </xsl:text>
        <xsl:value-of select="@stroke-type" />
        <xsl:text>*/</xsl:text>
    </xsl:template>

    <xsl:template match="SectionDef" mode="css-rule">
        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector">
                <xsl:text>.Section-</xsl:text>
                <xsl:value-of select="position()-1" />
            </xsl:with-param>
            <xsl:with-param name="declarations">
                <xsl:apply-templates select="PageDef" mode="paper-dimension" />
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector">
                <xsl:text>.Section-</xsl:text>
                <xsl:value-of select="position()-1" />
                <xsl:text> .Page</xsl:text>
            </xsl:with-param>
            <xsl:with-param name="declarations">
                <xsl:apply-templates select="PageDef" mode="page-css" />
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="PageDef" mode="page-css">
        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">margin-top</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:value-of select="@top-offset div 100" />
                <xsl:text>pt</xsl:text>
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">margin-right</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:value-of select="@right-offset div 100" />
                <xsl:text>pt</xsl:text>
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">margin-bottom</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:value-of select="@bottom-offset div 100" />
                <xsl:text>pt</xsl:text>
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">margin-left</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:value-of select="@left-offset div 100" />
                <xsl:text>pt</xsl:text>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="PageDef" mode="paper-dimension">
        <xsl:choose>
            <xsl:when test="@orientation = 'portrait'">
                <xsl:apply-templates select="." mode="paper-dimension-portrait" />
            </xsl:when>
            <xsl:when test="@orientation = 'landscape'">
                <xsl:apply-templates select="." mode="paper-dimension-landscape" />
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="PageDef" mode="paper-dimension-portrait">
        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">width</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:value-of select="@width div 100" />
                <xsl:text>pt</xsl:text>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="PageDef" mode="paper-dimension-landscape">
        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">width</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:value-of select="@height div 100" />
                <xsl:text>pt</xsl:text>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="ParaShape" mode="text-align">
        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">text-align</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:choose>
                    <xsl:when test="@align = 'center'">center</xsl:when>
                    <xsl:when test="@align = 'left'">left</xsl:when>
                    <xsl:when test="@align = 'right'">right</xsl:when>
                    <xsl:when test="@align = 'both'">justify</xsl:when>
                    <xsl:otherwise>justify</xsl:otherwise>
                </xsl:choose>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="ParaShape" mode="text-indent">
        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">text-indent</xsl:with-param>
            <xsl:with-param name="value">
                <!-- @indent seems to be doubled -->
                <xsl:value-of select="@indent div 100 div 2" />
                <xsl:text>pt</xsl:text>
            </xsl:with-param>
        </xsl:call-template>

        <xsl:if test="@indent &lt; 0">
            <xsl:call-template name="css-declaration">
                <xsl:with-param name="property">padding-left</xsl:with-param>
                <xsl:with-param name="value">
                    <xsl:value-of select="@indent div 100 div 2 * -1" />
                    <xsl:text>pt</xsl:text>
                </xsl:with-param>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>

    <xsl:template match="CharShape" mode="text-decoration">
        <xsl:choose>
            <xsl:when test="@underline = 'underline'">
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">text-decoration</xsl:with-param>
                    <xsl:with-param name="value">underline</xsl:with-param>
                </xsl:call-template>
                <xsl:apply-templates select="." mode="text-decoration-color" />
                <xsl:apply-templates select="." mode="text-decoration-style" />
            </xsl:when>
            <xsl:when test="@underline = 'overline'">
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">text-decoration</xsl:with-param>
                    <xsl:with-param name="value">overline</xsl:with-param>
                </xsl:call-template>
                <xsl:apply-templates select="." mode="text-decoration-color" />
                <xsl:apply-templates select="." mode="text-decoration-style" />
            </xsl:when>
            <xsl:when test="@underline = 'line_through'">
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">text-decoration</xsl:with-param>
                    <xsl:with-param name="value">line-through</xsl:with-param>
                </xsl:call-template>
                <xsl:apply-templates select="." mode="text-decoration-color" />
                <xsl:apply-templates select="." mode="text-decoration-style" />
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="CharShape" mode="text-decoration-color">
        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">text-decoration-color</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:value-of select="@underline-color" />
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">-moz-text-decoration-color</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:value-of select="@underline-color" />
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">-webkit-text-decoration-color</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:value-of select="@underline-color" />
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="CharShape" mode="text-decoration-style">
        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">text-decoration-style</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:apply-templates select="." mode="text-decoration-style-value" />
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">-moz-text-decoration-style</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:apply-templates select="." mode="text-decoration-style-value" />
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">-webkit-text-decoration-style</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:apply-templates select="." mode="text-decoration-style-value" />
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="CharShape" mode="text-decoration-style-value">
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

    <xsl:template name="css-rule">
        <xsl:param name="selector" />
        <xsl:param name="declarations" />
        <xsl:value-of select="$selector" />
        <xsl:text> {&#10;</xsl:text>
        <xsl:value-of select="$declarations" />
        <xsl:text>}&#10;</xsl:text>
    </xsl:template>

    <xsl:template name="css-declaration">
        <xsl:param name="property" />
        <xsl:param name="value" />

        <xsl:text>  </xsl:text>
        <xsl:value-of select="$property" />
        <xsl:text>: </xsl:text>
        <xsl:value-of select="$value" />
        <xsl:text>;&#10;</xsl:text>
    </xsl:template>
</xsl:stylesheet>
