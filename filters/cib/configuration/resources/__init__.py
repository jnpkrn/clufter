# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

pcs2simplepcs = '''\
    <!--
        SIMPLIFY FENCING/STONITH
     -->

    <xsl:template match="primitive[
                             @template
                             =
                             preceding-sibling::template[
                                @class = 'stonith'
                             ]/@id
                             and not(preceding-sibling::primitive[
                                @template = current()/@template
                             ])
                         ]">
        <xsl:variable name="Primitives"
                      select="(following-sibling::primitive|self::primitive)[
                                  @template = current()/@template
                              ]"/>
        <xsl:variable name="Template"
                      select="preceding-sibling::template[
                                 @id = current()/@template
                              ]"/>
        <xsl:variable name="GroupablePrimitives"
                      select="(following-sibling::primitive|self::primitive)[
                                  @template = current()/@template
                                  and not(*[name() != 'instance_attributes'])
                                  and not(instance_attributes/nvpair[
                                      @name != 'pcmk_host_list'
                                      and
                                      @name != 'pcmk_host_map'
                                  ])
                              ]"/>
        <xsl:choose>
            <!-- when we can actually do any kind of simplification/grouping,
                 i.e., when fencedev:fenceinst 1:1, or 1:N and no fenceinst
                 specify instance parameter other than port (if any) -->
            <xsl:when test="count($Primitives) = 1
                            or
                            count($Primitives) = count($GroupablePrimitives)">
                <xsl:copy>
                    <xsl:copy-of select="$Template/@*"/>
                    <xsl:for-each select="($Primitives|$Template)/*">
                        <xsl:choose>
                            <xsl:when test="generate-id(..) = generate-id($Template)
                                            and
                                            not(
                                                $Primitives/*[
                                                    name() = name(current())
                                                ]
                                            )">
                                <xsl:copy/>
                            </xsl:when>
                            <xsl:when test="generate-id(..) = generate-id($Primitives)
                                            and name() = 'instance_attributes'">
                                <xsl:copy>
                                    <xsl:copy-of select="$Template/*[
                                                             name() = name(current())
                                                         ]/*"/>
                                    <xsl:variable name="PcmkHostList"
                                                  select="$Primitives/instance_attributes/nvpair[
                                                              @name = 'pcmk_host_list'
                                                          ]"/>
                                    <xsl:variable name="PcmkHostMap"
                                                  select="$Primitives/instance_attributes/nvpair[
                                                              @name = 'pcmk_host_map'
                                                          ]"/>
                                    <xsl:if test="$PcmkHostList">
                                        <nvpair id="{concat($Template/@id, '-ATTRS-pcmk_host_list')}"
                                                name="pcmk_host_list">
                                        <xsl:attribute name="value">
                                            <xsl:for-each select="$PcmkHostList">
                                                <xsl:if test="position() != 1">
                                                    <xsl:value-of select="' '"/>
                                                </xsl:if>
                                                <xsl:value-of select="@value"/>
                                            </xsl:for-each>
                                        </xsl:attribute>
                                        </nvpair>
                                    </xsl:if>
                                    <xsl:if test="$PcmkHostMap">
                                        <nvpair id="{concat($Template/@id, '-ATTRS-pcmk_host_map')}"
                                                name="pcmk_host_map">
                                        <xsl:attribute name="value">
                                            <xsl:for-each select="$PcmkHostMap">
                                                <xsl:if test="position() != 1">
                                                    <xsl:value-of select="','"/>
                                                </xsl:if>
                                                <xsl:value-of select="@value"/>
                                            </xsl:for-each>
                                        </xsl:attribute>
                                        </nvpair>
                                    </xsl:if>
                                </xsl:copy>
                            </xsl:when>
                        </xsl:choose>
                    </xsl:for-each>
                </xsl:copy>
            </xsl:when>
            <xsl:otherwise>
                <xsl:if test="count($Primitives) != count($GroupablePrimitives)">
                    <xsl:copy-of select="preceding-sibling::template[
                                             @class = 'stonith'
                                             and
                                             @id = current()/@template
                                         ]|(following-sibling::primitive|self::primitive)[
                                             @template = current()/@template
                                         ]"/>
                </xsl:if>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <!-- remove non-first instances of fence devices, of which all are
         removed unconditionally (preserved in the above logic when needed) -->
    <xsl:template match="primitive[
                             @template
                             =
                             preceding-sibling::template[
                                @class = 'stonith'
                             ]/@id
                             and preceding-sibling::primitive[
                                @template = current()/@template
                             ]
                         ]"/>
    <xsl:template match="template[@class = 'stonith']"/>
'''
