# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

from .... import package_name

pcsprelude2pcscompact = ('''\
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
                 specify instance parameter other than port (if any)
                 or no instance attributes specified per fencedev -->
            <xsl:when test="count($Primitives) = 1
                            or
                            count($Primitives) = count($GroupablePrimitives)
                            or
                            count($Template/instance_attributes/*) = 0">
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
                                    <xsl:attribute name="id">
                                        <xsl:value-of select="concat($Template/@id, '-ATTRS')"/>
                                    </xsl:attribute>
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


    <!--
        trivial conversion of resource groups into groups (original groups
        are preserved as-were) if they are not exclusive
     -->

    <xsl:template match="template[
                             @provider = '%(package_name)s'
                             and
                             @type = 'temporary-service'
                             and
                             not(
                                 meta_attributes/nvpair[
                                     @name = 'exclusive'
                                     and
                                     (
                                        @value = 'yes'
                                        or
                                        @value &gt; 0
                                    )
                                 ]
                             )
                          ]">
        <xsl:variable name="ResourceGroup" select="@id"/>
        <group id="{$ResourceGroup}-GROUP">
            <xsl:for-each select="../primitive[
                                     meta_attributes/nvpair[
                                         @name = 'rgmanager-service'
                                         and
                                         @value = $ResourceGroup
                                     ]
                                  ]">
                <xsl:copy>
                    <xsl:copy-of select="@*"/>
                    <xsl:for-each select="node()[not(
                                              name() = 'meta_attributes'
                                              and
                                              (
                                                  count(*) = 0
                                                  or
                                                  (
                                                      count(*) = 1
                                                      and
                                                      nvpair[
                                                          @name = 'rgmanager-service'
                                                      ]
                                                  )
                                              )
                                          )]">
                        <xsl:choose>
                            <xsl:when test="meta_attributes">
                                <xsl:copy>
                                    <xsl:copy-of select="@*|node()[
                                                            name() != 'nvpair'
                                                            or
                                                            (
                                                                name() = 'nvpair'
                                                                and
                                                                @name != 'rgmanager-service'
                                                            )]"/>
                                </xsl:copy>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:copy>
                                    <xsl:copy-of select="@*|node()"/>
                                </xsl:copy>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:for-each>
                </xsl:copy>
            </xsl:for-each>
            <xsl:variable name="Autostart"
                          select="meta_attributes/nvpair[
                                      @name = 'autostart'
                                  ]/@value"/>
            <xsl:if test="$Autostart = 'no'
                          or
                          $Autostart = 0">
                <meta_attributes id="{$ResourceGroup}-META">
                    <nvpair id="{$ResourceGroup}-META-is-managed"
                            name="is-managed"
                            value="false"/>
                </meta_attributes>
            </xsl:if>
        </group>

        <xsl:if test="meta_attributes/nvpair[
                          @name = 'domain'
                      ]">
            <xsl:copy>
                <xsl:copy-of select="@*|node()"/>
            </xsl:copy>
        </xsl:if>
    </xsl:template>

    <!-- also remove the primitive(s) now moved to the group(s) -->
    <xsl:template match="primitive[
                            meta_attributes/nvpair[
                                @name = 'rgmanager-service'
                                and
                                @value = current()/../template[
                                    @provider = '%(package_name)s'
                                    and
                                    @type = 'temporary-service'
                                    and
                                    not(
                                        meta_attributes/nvpair[
                                            @name = 'exclusive'
                                            and
                                            (
                                               @value = 'yes'
                                               or
                                               @value &gt; 0
                                           )
                                        ]
                                    )
                                ]/@id
                            ]
                         ]"/>

''') % dict(package_name=package_name())
