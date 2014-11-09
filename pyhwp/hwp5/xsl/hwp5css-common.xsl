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
        <xsl:variable name="paragraph-selector">
            <xsl:text>.</xsl:text>
            <xsl:value-of select="translate(@name, ' ', '-')"/>
        </xsl:variable>
        <xsl:variable name="spans-selector">
            <xsl:value-of select="$paragraph-selector" />
            <xsl:text> &gt; </xsl:text>
            <xsl:text>span</xsl:text>
        </xsl:variable>
        <xsl:if test="@kind = 'paragraph'">
            <xsl:variable name="parashape_pos" select="@parashape-id + 1" />
            <xsl:variable name="parashape" select="//ParaShape[$parashape_pos]" />
            <xsl:call-template name="css-rule">
                <xsl:with-param name="selector" select="$paragraph-selector" />
                <xsl:with-param name="declarations">
                    <xsl:text>/* </xsl:text>
                    <xsl:text>@parashape-id = </xsl:text>
                    <xsl:value-of select="@parashape-id" />
                    <xsl:text>*/&#10;</xsl:text>
                    <xsl:apply-templates select="$parashape" mode="css-declaration" />
                </xsl:with-param>
            </xsl:call-template>
            <xsl:call-template name="css-rule">
                <xsl:with-param name="selector" select="$spans-selector" />
                <xsl:with-param name="declarations">
                    <xsl:apply-templates select="$parashape" mode="css-declaration-for-span" />
                </xsl:with-param>
            </xsl:call-template>
        </xsl:if>
        <xsl:variable name="charshape_pos" select="number(@charshape-id) + 1" />
        <xsl:variable name="charshape" select="//CharShape[$charshape_pos]" />
        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector" select="$spans-selector" />
            <xsl:with-param name="declarations">
                <xsl:text>/* </xsl:text>
                <xsl:text>@charshape-id = </xsl:text>
                <xsl:value-of select="@charshape-id" />
                <xsl:text>*/&#10;</xsl:text>
                <xsl:apply-templates select="$charshape" mode="css-declaration" />
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="ParaShape" mode="css-rule">
        <xsl:variable name="paragraph-selector">
            <xsl:text>p.parashape-</xsl:text>
            <xsl:number value="position()-1" />
        </xsl:variable>
        <xsl:variable name="spans-selector">
            <xsl:value-of select="$paragraph-selector" />
            <xsl:text> &gt; </xsl:text>
            <xsl:text>span</xsl:text>
        </xsl:variable>
        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector" select="$paragraph-selector" />
            <xsl:with-param name="declarations">
                <xsl:apply-templates select="." mode="css-declaration" />
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector" select="$spans-selector" />
            <xsl:with-param name="declarations">
                <xsl:apply-templates select="." mode="css-declaration-for-span" />
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="ParaShape" mode="css-declaration">
        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">margin</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:value-of select="@doubled-margin-top div 100 div 2"/>
                <xsl:text>pt</xsl:text>
                <xsl:text> </xsl:text>
                <xsl:value-of select="@doubled-margin-right div 100 div 2"/>
                <xsl:text>pt</xsl:text>
                <xsl:text> </xsl:text>
                <xsl:value-of select="@doubled-margin-bottom div 100 div 2"/>
                <xsl:text>pt</xsl:text>
                <xsl:text> </xsl:text>
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
    </xsl:template>

    <xsl:template match="ParaShape" mode="css-declaration-for-span">
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
    </xsl:template>

    <xsl:template match="CharShape" mode="css-rule">
        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector">
                <xsl:text>span.charshape-</xsl:text>
                <xsl:number value="position()-1" />
            </xsl:with-param>
            <xsl:with-param name="declarations">
                <xsl:apply-templates select="." mode="css-declaration" />
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="CharShape" mode="css-declaration">
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
                        <xsl:apply-templates select="Border[@attribute-name='top']" mode="border-value"/>
                    </xsl:with-param>
                </xsl:call-template>

                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">border-right</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:apply-templates select="Border[@attribute-name='right']" mode="border-value"/>
                    </xsl:with-param>
                </xsl:call-template>

                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">border-bottom</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:apply-templates select="Border[@attribute-name='bottom']" mode="border-value"/>
                    </xsl:with-param>
                </xsl:call-template>

                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">border-left</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:apply-templates select="Border[@attribute-name='left']" mode="border-value"/>
                    </xsl:with-param>
                </xsl:call-template>

                <xsl:apply-templates select="FillColorPattern" mode="css-declaration" />
                <xsl:apply-templates select="FillGradation" mode="css-declaration" />
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="Border" mode="border-value">
        <xsl:apply-templates select="." mode="border-width-value" />
        <xsl:text> </xsl:text>
        <xsl:apply-templates select="." mode="border-style-value" />
        <xsl:text> </xsl:text>
        <xsl:value-of select="@color" />
    </xsl:template>

    <xsl:template match="Border" mode="border-width-value">
        <xsl:choose>
            <xsl:when test="@width = '0.1mm'">1px</xsl:when>
            <xsl:when test="@width = '0.12mm'">1px</xsl:when>
            <xsl:when test="@width = '0.15mm'">1px</xsl:when>
            <xsl:when test="@width = '0.2mm'">1px</xsl:when>
            <xsl:when test="@width = '0.25mm'">1px</xsl:when>
            <xsl:when test="@width = '0.4mm'">2px</xsl:when>
            <xsl:when test="@width = '0.5mm'">2px</xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="@width" />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="Border" mode="border-style-value">
        <xsl:choose>
            <xsl:when test="@stroke-type = 'none'">none</xsl:when>
            <xsl:when test="@stroke-type = 'solid'">solid</xsl:when>
            <xsl:when test="@stroke-type = 'dashed'">dashed</xsl:when>
            <xsl:when test="@stroke-type = 'dotted'">dotted</xsl:when>
            <xsl:when test="@stroke-type = 'dash-dot'">dashed</xsl:when>
            <xsl:when test="@stroke-type = 'dash-dot-dot'">dashed</xsl:when>
            <xsl:when test="@stroke-type = 'long-dash'">dahsed</xsl:when>
            <xsl:when test="@stroke-type = 'large-dot'">dotted</xsl:when>
            <xsl:when test="@stroke-type = 'double'">double</xsl:when>
            <xsl:when test="@stroke-type = 'double-2'">double</xsl:when>
            <xsl:when test="@stroke-type = 'double-3'">double</xsl:when>
            <xsl:when test="@stroke-type = 'triple'">double</xsl:when>
            <xsl:when test="@stroke-type = 'wave'">solid</xsl:when>
            <xsl:when test="@stroke-type = 'double-wave'">double</xsl:when>
            <xsl:when test="@stroke-type = 'inset'">inset</xsl:when>
            <xsl:when test="@stroke-type = 'outset'">outset</xsl:when>
            <xsl:when test="@stroke-type = 'groove'">groove</xsl:when>
            <xsl:when test="@stroke-type = 'ridge'">ridge</xsl:when>
            <xsl:otherwise>solid</xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="FillColorPattern" mode="css-declaration">
        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">background-color</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:value-of select="@background-color" />
            </xsl:with-param>
        </xsl:call-template>
        <xsl:apply-templates select="." mode="background-image" />
    </xsl:template>

    <xsl:template match="FillColorPattern" mode="background-image">
        <xsl:choose>
            <xsl:when test="@pattern-type = 'none'"></xsl:when>
            <xsl:when test="@pattern-type = 'horizontal'">
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">background-image</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:text>url(</xsl:text>
                        <xsl:text>data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAQAAABuBnYAAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAAAEgAAABIAEbJaz4AAAATSURBVAjXY2AgGTAy/CddEyEAAFOKAQGTpJ5ZAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDE0LTExLTA1VDE1OjM3OjA3KzA5OjAwrbX03gAAACV0RVh0ZGF0ZTptb2RpZnkAMjAxNC0xMS0wNVQxNTozNzowNyswOTowMNzoTGIAAAAASUVORK5CYII=</xsl:text>
                        <xsl:text>)</xsl:text>
                        <xsl:text>/* </xsl:text>
                        <xsl:value-of select="@pattern-type" />
                        <xsl:text> */</xsl:text>
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:when>
            <xsl:when test="@pattern-type = 'vertical'">
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">background-image</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:text>url(</xsl:text>
                        <xsl:text>data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAQAAABuBnYAAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAAAEgAAABIAEbJaz4AAAAVSURBVAjXY2CAgP9QmoGJAQ3QRwAAg8ABDm14IFwAAAAldEVYdGRhdGU6Y3JlYXRlADIwMTQtMTEtMDVUMTU6Mzc6MzcrMDk6MDAjOvM9AAAAJXRFWHRkYXRlOm1vZGlmeQAyMDE0LTExLTA1VDE1OjM3OjM3KzA5OjAwUmdLgQAAAABJRU5ErkJggg==</xsl:text>
                        <xsl:text>)</xsl:text>
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:when>
            <xsl:when test="@pattern-type = 'backslash'">
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">background-image</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:text>url(</xsl:text>
                        <xsl:text>data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAQAAABuBnYAAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAAAEgAAABIAEbJaz4AAAAQSURBVAjXY2D4z4ABBkAIABqKB/lrzYhNAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDE0LTExLTA1VDE1OjM4OjE0KzA5OjAwofy1UAAAACV0RVh0ZGF0ZTptb2RpZnkAMjAxNC0xMS0wNVQxNTozODoxNCswOTowMNChDewAAAAASUVORK5CYII=</xsl:text>
                        <xsl:text>)</xsl:text>
                        <xsl:text>/* </xsl:text>
                        <xsl:value-of select="@pattern-type" />
                        <xsl:text> */</xsl:text>
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:when>
            <xsl:when test="@pattern-type = 'slash'">
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">background-image</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:text>url(</xsl:text>
                        <xsl:text>data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAQAAABuBnYAAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAAAEgAAABIAEbJaz4AAAAPSURBVAjXY2BABf8HiAsAGooH+VFK23UAAAAldEVYdGRhdGU6Y3JlYXRlADIwMTQtMTEtMDVUMTU6Mzg6MzUrMDk6MDBFrrmZAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDE0LTExLTA1VDE1OjM4OjM1KzA5OjAwNPMBJQAAAABJRU5ErkJggg==</xsl:text>
                        <xsl:text>)</xsl:text>
                        <xsl:text>/* </xsl:text>
                        <xsl:value-of select="@pattern-type" />
                        <xsl:text> */</xsl:text>
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:when>
            <xsl:when test="@pattern-type = 'grid'">
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">background-image</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:text>url(</xsl:text>
                        <xsl:text>data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAQAAABuBnYAAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAAAEgAAABIAEbJaz4AAAAVSURBVAjXY2T4z4AG0ASY0OVpIgAA/d8CDKGA4lwAAAAldEVYdGRhdGU6Y3JlYXRlADIwMTQtMTEtMDVUMTU6MzQ6MzUrMDk6MDBfklkXAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDE0LTExLTA1VDE1OjM0OjM1KzA5OjAwLs/hqwAAAABJRU5ErkJggg==</xsl:text>
                        <xsl:text>)</xsl:text>
                        <xsl:text>/* </xsl:text>
                        <xsl:value-of select="@pattern-type" />
                        <xsl:text> */</xsl:text>
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:when>
            <xsl:when test="@pattern-type = 'cross'">
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">background-image</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:text>url(</xsl:text>
                        <xsl:text>data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAQAAABuBnYAAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAAAEgAAABIAEbJaz4AAAAeSURBVAjXY2CAgP9QmoGJAQ1gCDAiFKMCEszAEAAAEWMDCQJfExIAAAAldEVYdGRhdGU6Y3JlYXRlADIwMTQtMTEtMDVUMTU6Mzk6NDErMDk6MDBU5v+tAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDE0LTExLTA1VDE1OjM5OjQxKzA5OjAwJbtHEQAAAABJRU5ErkJggg==</xsl:text>
                        <xsl:text>)</xsl:text>
                        <xsl:text>/* </xsl:text>
                        <xsl:value-of select="@pattern-type" />
                        <xsl:text> */</xsl:text>
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>/* </xsl:text>
                <xsl:text>unrecognized @pattern-type: </xsl:text>
                <xsl:value-of select="@pattern-type" />
                <xsl:text> */</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="FillGradation" mode="css-declaration">
        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">background-image</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:text>linear-gradient</xsl:text>
                <xsl:text>(</xsl:text>
                <xsl:value-of select="@shear" />
                <xsl:text>deg</xsl:text>
                <xsl:for-each select="colors">
                    <xsl:text>,</xsl:text>
                    <xsl:value-of select="@hex" />
                </xsl:for-each>
                <xsl:text>)</xsl:text>
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">background-image</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:text>-webkit-linear-gradient</xsl:text>
                <xsl:text>(</xsl:text>
                <xsl:value-of select="@shear" />
                <xsl:text>deg</xsl:text>
                <xsl:for-each select="colors">
                    <xsl:text>,</xsl:text>
                    <xsl:value-of select="@hex" />
                </xsl:for-each>
                <xsl:text>)</xsl:text>
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">background-image</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:text>-moz-linear-gradient</xsl:text>
                <xsl:text>(</xsl:text>
                <xsl:value-of select="@shear" />
                <xsl:text>deg</xsl:text>
                <xsl:for-each select="colors">
                    <xsl:text>,</xsl:text>
                    <xsl:value-of select="@hex" />
                </xsl:for-each>
                <xsl:text>)</xsl:text>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="SectionDef" mode="css-rule">
        <xsl:variable name="section-selector">
            <xsl:text>.Section-</xsl:text>
            <xsl:value-of select="@section-id" />
        </xsl:variable>
        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector" select="$section-selector" />
            <xsl:with-param name="declarations">
                <xsl:apply-templates select="PageDef" mode="paper-dimension" />
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector">
                <xsl:value-of select="$section-selector" />
                <xsl:text> </xsl:text>
                <xsl:text>.HeaderPageFooter</xsl:text>
            </xsl:with-param>
            <xsl:with-param name="declarations">
                <xsl:apply-templates select="PageDef" mode="headerpagefooter-css" />
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector">
                <xsl:value-of select="$section-selector" />
                <xsl:text> </xsl:text>
                <xsl:text>.Page</xsl:text>
            </xsl:with-param>
            <xsl:with-param name="declarations">
                <xsl:apply-templates select="PageDef" mode="page-css" />
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="PageDef" mode="headerpagefooter-css">
        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">position</xsl:with-param>
            <xsl:with-param name="value">relative</xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">margin-top</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                    <xsl:with-param name="hwpunit" select="@top-offset" />
                </xsl:call-template>
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">margin-right</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                    <xsl:with-param name="hwpunit" select="@right-offset" />
                </xsl:call-template>
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">margin-bottom</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                    <xsl:with-param name="hwpunit" select="@bottom-offset" />
                </xsl:call-template>
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">margin-left</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                    <xsl:with-param name="hwpunit" select="@left-offset" />
                </xsl:call-template>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="PageDef" mode="page-css">
        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">padding-top</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                    <xsl:with-param name="hwpunit" select="@header-offset" />
                </xsl:call-template>
            </xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">padding-bottom</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                    <xsl:with-param name="hwpunit" select="@footer-offset" />
                </xsl:call-template>
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
                <xsl:call-template name="hwpunit-to-mm">
                    <xsl:with-param name="hwpunit" select="@width" />
                </xsl:call-template>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="PageDef" mode="paper-dimension-landscape">
        <xsl:call-template name="css-declaration">
            <xsl:with-param name="property">width</xsl:with-param>
            <xsl:with-param name="value">
                <xsl:call-template name="hwpunit-to-mm">
                    <xsl:with-param name="hwpunit" select="@height" />
                </xsl:call-template>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="Header" mode="css-rule">
        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector">.HeaderArea</xsl:with-param>
            <xsl:with-param name="declarations">
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">position</xsl:with-param>
                    <xsl:with-param name="value">absolute</xsl:with-param>
                </xsl:call-template>
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">left</xsl:with-param>
                    <xsl:with-param name="value">0</xsl:with-param>
                </xsl:call-template>
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">top</xsl:with-param>
                    <xsl:with-param name="value">0</xsl:with-param>
                </xsl:call-template>
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">width</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:call-template name="hwpunit-to-mm">
                            <xsl:with-param name="hwpunit" select="HeaderParagraphList/@width" />
                        </xsl:call-template>
                    </xsl:with-param>
                </xsl:call-template>
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">height</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:call-template name="hwpunit-to-mm">
                            <xsl:with-param name="hwpunit" select="HeaderParagraphList/@height" />
                        </xsl:call-template>
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="Footer" mode="css-rule">
        <xsl:call-template name="css-rule">
            <xsl:with-param name="selector">.FooterArea</xsl:with-param>
            <xsl:with-param name="declarations">
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">position</xsl:with-param>
                    <xsl:with-param name="value">absolute</xsl:with-param>
                </xsl:call-template>
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">left</xsl:with-param>
                    <xsl:with-param name="value">0</xsl:with-param>
                </xsl:call-template>
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">bottom</xsl:with-param>
                    <xsl:with-param name="value">0</xsl:with-param>
                </xsl:call-template>
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">width</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:call-template name="hwpunit-to-mm">
                            <xsl:with-param name="hwpunit" select="FooterParagraphList/@width" />
                        </xsl:call-template>
                    </xsl:with-param>
                </xsl:call-template>
                <xsl:call-template name="css-declaration">
                    <xsl:with-param name="property">height</xsl:with-param>
                    <xsl:with-param name="value">
                        <xsl:call-template name="hwpunit-to-mm">
                            <xsl:with-param name="hwpunit" select="FooterParagraphList/@height" />
                        </xsl:call-template>
                    </xsl:with-param>
                </xsl:call-template>
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

    <xsl:template name="hwpunit-to-mm">
        <xsl:param name="hwpunit" />
        <xsl:value-of select="floor($hwpunit div 100 * 0.352777778 * 100 + 0.5) div 100" />
        <xsl:text>mm</xsl:text>
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
