# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

from .... import package_name

cibprelude2cibcompact = ('''\
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
        <xsl:variable name="Resources" select="../primitive[
                                                  meta_attributes/nvpair[
                                                      @name = 'rgmanager-service'
                                                      and
                                                      @value = $ResourceGroup
                                                  ]
                                               ]"/>
        <xsl:if test="$Resources">
            <group id="{$ResourceGroup}-GROUP">
                <xsl:for-each select="$Resources">
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
                <!--
                    stickiness=INFINITY for each N in dedicated nodes ~ @nofailback
                -->
                <xsl:variable name="FailoverDomain"
                            select="../template[
                                    @provider = '%(package_name)s'
                                    and
                                    @type = 'temporary-failoverdomain'
                                    and
                                    @id = current()/meta_attributes/nvpair[
                                        @name = 'domain'
                                    ]/@value
                                ]"/>
                <xsl:if test="$FailoverDomain/meta_attributes/nvpair[
                                @name = 'nofailback'
                            ]/@value ='1'
                            and
                            count(
                                $FailoverDomain/meta_attributes/nvpair[
                                    starts-with(@name, 'failoverdomainnode-')
                                ]
                            ) != 0">
                    <xsl:comment
                    ><xsl:value-of select="concat(' mimic NOFAILBACK failoverdomain (',
                                                $FailoverDomain/@id, ')')"
                    /></xsl:comment>
                    <meta_attributes id="{$ResourceGroup}-META-ATTRS-nofailback">
                        <rule id="{$ResourceGroup}-META-RULE-stickiness"
                            score="0"
                            boolean-op="or">
                            <xsl:for-each select="$FailoverDomain/meta_attributes/nvpair[
                                                    starts-with(@name, 'failoverdomainnode-')
                                                ]">
                                <expression id="STICKINESS-{$ResourceGroup}-{@value}"
                                            attribute="#uname"
                                            operation="eq"
                                            value="{@value}">
                                </expression>
                            </xsl:for-each>
                        </rule>
                        <nvpair id="{$ResourceGroup}-META-ATTRS-nofailback-pair"
                                name="resource-stickiness"
                                value="INFINITY"/>
                    </meta_attributes>
                </xsl:if>
                <!--
                    is-managed=false ~ @autostart in (no, 0)
                -->
                <xsl:variable name="Autostart"
                            select="meta_attributes/nvpair[
                                        @name = 'autostart'
                                    ]/@value"/>
                <xsl:if test="$Autostart = 'no'
                              or
                              $Autostart = 0">
                    <xsl:comment
                    ><xsl:value-of select="concat(' mimic no-autostart resource group (',
                                                $ResourceGroup, ')')"
                    /></xsl:comment>
                    <meta_attributes id="{$ResourceGroup}-META-ATTRS-autostart">
                        <nvpair id="{$ResourceGroup}-META-is-managed"
                                name="is-managed"
                                value="false"/>
                    </meta_attributes>
                </xsl:if>
            </group>
        </xsl:if>

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

###

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....filters.cib2pcscmd import attrset_xsl
from ....utils_xslt import NL, xslt_is_member

cib2pcscmd = ('''\
    <!-- STONITH -->
    <xsl:for-each select=".//primitive[@class = 'stonith']">
''' + (
        verbose_inform('"new stonith: ", @id')
) + '''
        <xsl:value-of select="concat($pcscmd_pcs, 'stonith create',
                                     ' ', @id,
                                     ' ', @type)"/>
''' + (
        attrset_xsl("instance_attributes")
) + '''
        <!-- operations -->
        <xsl:if test="operations/op">
            <xsl:value-of select="' op'"/>
            <xsl:for-each select="operations/op">
                <xsl:value-of select="concat(' ', @name)"/>
                <xsl:for-each select="@*">
                    <xsl:value-of select='concat(" &apos;",
                                                 name(), "=", .,
                                                 "&apos;")'/>
                </xsl:for-each>
            </xsl:for-each>
        </xsl:if>
        <!-- meta attrs -->
        <xsl:if test="meta_attributes/nvpair">
            <xsl:value-of select="' meta'"/>
''' + (
            attrset_xsl("meta_attributes")
) + '''
        </xsl:if>
        <xsl:value-of select="'%(NL)s'"/>
''' + (
        verbose_ec_test
) + '''
    </xsl:for-each>

    <!--
        ORDINARY/CLONE/MASTER CLUSTER RESOURCES
     -->

    <!-- primitives -->
    <xsl:for-each select=".//primitive[@class != 'stonith']">
        <xsl:variable name="ResourceSpec">
            <xsl:choose>
                <xsl:when test="@class = 'ocf'">
                    <xsl:value-of select="concat(@class, ':', @provider, ':', @type)"/>
                </xsl:when>
                <xsl:when test="@class">
                    <xsl:value-of select="concat(@class, ':', @type)"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="@type"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:choose>
            <xsl:when test="name(..) = 'clone'">
''' + (
                verbose_inform('"new clone resource: ", @id')
) + '''
            </xsl:when>
            <xsl:when test="name(..) = 'master'">
''' + (
                verbose_inform('"new master resource: ", @id')
) + '''
            </xsl:when>
            <xsl:otherwise>
''' + (
                verbose_inform('"new resource: ", @id')
) + '''
            </xsl:otherwise>
        </xsl:choose>
        <xsl:value-of select="concat($pcscmd_pcs, 'resource create',
                                     ' ', @id,
                                     ' ', $ResourceSpec)"/>
''' + (
        attrset_xsl("instance_attributes")
) + '''
        <!-- operations -->
        <xsl:if test="operations/op">
            <xsl:value-of select="' op'"/>
            <xsl:for-each select="operations/op">
                <xsl:value-of select="concat(' ', @name)"/>
                <xsl:for-each select="@*">
                    <xsl:value-of select='concat(" &apos;",
                                                 name(), "=", .,
                                                 "&apos;")'/>
                </xsl:for-each>
            </xsl:for-each>
        </xsl:if>
        <!-- meta attrs -->
        <xsl:if test="meta_attributes/nvpair">
            <xsl:value-of select="' meta'"/>
''' + (
            attrset_xsl("meta_attributes")
) + '''
        </xsl:if>
        <!-- clone/master resource specifics
         XXX alternatively, we could use: pcs resource clone to be
             more explicit
         -->
        <xsl:if test="
''' + (
            xslt_is_member('name(..)', ('clone', 'master'))
) + '''">
            <xsl:value-of select="concat(' --', name(..))"/>
''' + (
            attrset_xsl("../meta_attributes")
) + '''
        </xsl:if>
        <xsl:value-of select="'%(NL)s'"/>
''' + (
        verbose_ec_test
) + '''
    </xsl:for-each>

    <!-- groups -->
    <clufter:descent-mix at="group"/>

    <!-- templates -->
    <xsl:if test="template">
        <xsl:message terminate="true"
        >Cannot convert templates to pcs commands yet [https://bugzilla.redhat.com/1281359]</xsl:message>
    </xsl:if>

''') % dict(
    NL=NL,
)

###

from ....utils_xslt import xslt_is_member

cib_meld_templates_op_roles = ('Started', 'Slave')

# see lib/pengine/complex.c: unpack_template
cib_meld_templates = ('''\
    <!-- drop any occurrence as we meld them into proper primitives -->
    <xsl:template match="template[1]">
        <xsl:message
        >NOTE: this step may not be necessary once pcs handles templates [https://bugzilla.redhat.com/1281359]</xsl:message>
    </xsl:template>
    <xsl:template match="template"/>

    <xsl:template name="rewrite-id">
        <xsl:param name="Elem"/>
        <xsl:param name="InstanceId"/>
        <xsl:copy>
            <xsl:for-each select="@*">
                <xsl:choose>
                    <xsl:when test="name() = 'id'">
                        <xsl:attribute name="{name()}">
                            <xsl:value-of select="concat(., '-', $InstanceId)"/>
                        </xsl:attribute>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:copy/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:for-each>
            <xsl:for-each select="*">
                <xsl:call-template name="rewrite-id">
                    <xsl:with-param name="Elem" select="."/>
                    <xsl:with-param name="InstanceId" select="$InstanceId"/>
                </xsl:call-template>
            </xsl:for-each>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="primitive[@template]">
        <xsl:variable name="Template"
                      select="//template[@id = current()/@template]"/>
        <xsl:variable name="InstanceId" select="generate-id()"/>
        <xsl:copy>
            <xsl:copy-of select="@id|$Template/@*[name() != 'id']"/>
            <xsl:for-each select="$Template/*[name() != 'operations']">
                <xsl:call-template name="rewrite-id">
                    <xsl:with-param name="Elem" select="."/>
                    <xsl:with-param name="InstanceId" select="$InstanceId"/>
                </xsl:call-template>
            </xsl:for-each>
            <xsl:for-each select="*">
                <xsl:copy>
                    <xsl:copy-of select="@*"/>
                    <xsl:if test="name() = 'operations'">
                        <xsl:variable name="Operations" select="."/>
                        <xsl:for-each select="$Template/op[
                                                  not(
                                                      $Operations/op[
                                                          @name = current()/@name
                                                          and
                                                          (
                                                              @role = current()/@role
                                                              or
                                                              ((
                                                                  not(@role)
                                                                  or
''' + (
                                                                  xslt_is_member('@role',
                                                                                 cib_meld_templates_op_roles)
) + '''
                                                              ) and (
                                                                  not(current()/@role)
                                                                  or
''' + (
                                                                  xslt_is_member('current()/@role',
                                                                                 cib_meld_templates_op_roles)
) + '''

                                                              ))
                                                          )
                                                      ]
                                                  )
                                              ]">
                            <xsl:call-template name="rewrite-id">
                                <xsl:with-param name="Elem" select="."/>
                                <xsl:with-param name="InstanceId" select="$InstanceId"/>
                            </xsl:call-template>
                        </xsl:for-each>
                    </xsl:if>
                    <xsl:if test="name() != 'operations'">
                        <xsl:apply-templates/>
                    </xsl:if>
                </xsl:copy>
            </xsl:for-each>
        </xsl:copy>
    </xsl:template>
''')
