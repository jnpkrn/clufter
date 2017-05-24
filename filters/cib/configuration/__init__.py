# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"


cibprelude2cibcompact = '''\
    <clufter:descent-mix preserve-rest="true"/>
    <!-- strip empty optional elements -->
    <xsl:template match="fencing-topology[count(*) = 0]"/>
'''

###

from .... import package_name

cibcompact2cib = ('''\
    <xsl:template match="crm_config[
                             not(
                                 following-sibling::resources/primitive[
                                     @class = 'stonith'
                                 ]|following-sibling::resources/primitive[
                                     preceding-sibling::template[
                                         @class = 'stonith'
                                         and
                                         @id = current()/@template
                                     ]
                                 ]
                             )
                         ]">
        <xsl:copy>
            <xsl:comment> %(note_stonith)s </xsl:comment>
            <xsl:message>%(note_stonith)s</xsl:message>
            <cluster_property_set id="CRMCONFIG-bootstrap">
                <nvpair id="CRMCONFIG-bootstrap-STONITH-ENABLED"
                        name="stonith-enabled"
                        value="false"/>
            </cluster_property_set>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="constraints">
        <xsl:copy>
            <xsl:for-each select="../resources/template[
                                      @provider = '%(package_name)s'
                                      and
                                      @type = 'temporary-failoverdomain'
                                  ]">
                <xsl:variable name="FailoverDomain" select="."/>
                <xsl:for-each select="../template[
                                        @provider = '%(package_name)s'
                                        and
                                        @type = 'temporary-service'
                                        and
                                        meta_attributes/nvpair[
                                            @name = 'domain'
                                        ]/@value = $FailoverDomain/@id
                                    ]">
                    <xsl:variable name="Service" select="."/>
                    <xsl:variable name="Resources"
                                  select="../primitive[
                                              meta_attributes/nvpair[
                                                  @name = 'rgmanager-service'
                                                  and
                                                  @value = $Service/@id
                                              ]
                                          ]
                                          |
                                          ../group[
                                            @id = concat($Service/@id, '-GROUP')
                                          ]"/>
                    <xsl:for-each select="$Resources">
                        <xsl:variable name="Resource" select="."/>

                        <!-- rsc_location ~ failoverdomain/failoverdomainnodes -->

                        <xsl:if test="count(
                                          $FailoverDomain/meta_attributes/nvpair[
                                              starts-with(@name, 'failoverdomainnode-')
                                          ]
                                      ) != 0">
                            <rsc_location id="CONSTRAINT-LOCATION-{$Resource/@id}"
                                          rsc="{$Resource/@id}">
                                <xsl:comment
                                ><xsl:value-of select="concat(' mimic failoverdomain (',
                                                              substring-after($FailoverDomain/@id, 'FAILOVERDOMAIN-'),
                                                              ') for ', $Service/@id, ' ')"
                                /></xsl:comment>
                                <xsl:for-each select="$FailoverDomain/meta_attributes/nvpair[
                                                          starts-with(@name, 'failoverdomainnode-')
                                                      ]">
                                    <rule id="CONSTRAINT-LOCATION-{$Resource/@id}-{@value}">
                                        <xsl:attribute name="score">
                                            <xsl:choose>
                                                <xsl:when test="$FailoverDomain/meta_attributes/nvpair[
                                                                    @name = 'ordered'
                                                                ]/@value = 1
                                                                and
                                                                number(
                                                                    substring-after(@name,
                                                                                    'failoverdomainnode-')
                                                                ) &gt; 0">
                                                    <xsl:variable name="Result"
                                                                  select="(101 - number(
                                                                              substring-after(@name,
                                                                                              'failoverdomainnode-')
                                                                          )) * 10000"/>
                                                    <xsl:choose>
                                                        <xsl:when test="$Result = 1000000">
                                                            <xsl:value-of select="'INFINITY'"/>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <xsl:value-of select="$Result"/>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </xsl:when>
                                                <xsl:when test="$FailoverDomain/meta_attributes/nvpair[
                                                                    @name = 'ordered'
                                                                ]/@value = 1">
                                                    <xsl:value-of select="500000"/>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:value-of select="'INFINITY'"/>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </xsl:attribute>
                                        <expression id="CONSTRAINT-LOCATION-{$Resource/@id}-{@value}-expr"
                                                    attribute="#uname"
                                                    operation="eq"
                                                    value="{@value}"/>
                                    </rule>
                                </xsl:for-each>
                                <xsl:if test="$FailoverDomain/meta_attributes/nvpair[
                                                  @name = 'restricted'
                                              ]/@value = 1">
                                    <xsl:comment
                                    ><xsl:value-of select="concat(' mimic RESTRICTED failoverdomain (',
                                                                  substring-after($FailoverDomain/@id, 'FAILOVERDOMAIN-'),
                                                                  ') for ', $Service/@id, ' ')"
                                    /></xsl:comment>
                                    <rule id="CONSTRAINT-LOCATION-{$Resource/@id}-RESTRICTED"
                                          boolean-op="and"
                                          score="-INFINITY">
                                        <xsl:choose>
                                            <xsl:when test="$FailoverDomain/meta_attributes/nvpair[
                                                                starts-with(@name, 'failoverdomainnode-')
                                                            ]">
                                                <xsl:for-each select="$FailoverDomain/meta_attributes/nvpair[
                                                                          starts-with(@name, 'failoverdomainnode-')
                                                                      ]">
                                                    <expression id="CONSTRAINT-LOCATION-{$Resource/@id}-RESTRICTED-{@value}-expr"
                                                                attribute="#uname"
                                                                operation="ne"
                                                                value="{@value}"/>
                                                </xsl:for-each>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <!-- see filters/ccs-revitalize[failoverdomains]:
                                                     warn on empty restricted failoverdomains -->
                                                <expression id="CONSTRAINT-LOCATION-{$Resource/@id}-RESTRICTED-all-expr"
                                                            attribute="#uname"
                                                            operation="defined"/>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </rule>
                                </xsl:if>
                            </rsc_location>
                        </xsl:if>
                    </xsl:for-each>
                    <xsl:if test="count($Resources) &gt; 1">
                        <rsc_order id="CONSTRAINT-ORDER-{$Service/@id}"
                                score="INFINITY">
                            <resource_set id="CONSTRAINT-ORDER-{$Service/@id}-RESOURCES">
                                <xsl:for-each select="$Resources">
                                    <resource_ref id="{@id}"/>
                                </xsl:for-each>
                            </resource_set>
                        </rsc_order>
                    </xsl:if>
                </xsl:for-each>
            </xsl:for-each>
        </xsl:copy>
    </xsl:template>
''') % dict(
    note_stonith="NOTE: no fencing is configured hence stonith is disabled;"
                 " please note, however, that this is suboptimal, especially"
                 " in shared storage scenarios",
    package_name=package_name()
)

###

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....utils_xslt import NL

cib2pcscmd = ('''\
    <xsl:if test="not($pcscmd_dryrun) and $pcscmd_tmpcib">
''' + (
        verbose_inform('"get initial/working CIB: ", $pcscmd_tmpcib')
) + '''
        <xsl:value-of select="concat('pcs cluster cib ',
                                     $pcscmd_tmpcib)"/>
        <xsl:value-of select="'%(NL)s'"/>
''' + (
        verbose_ec_test
) + '''
    </xsl:if>
    <clufter:descent-mix at="crm_config"/>
    <clufter:descent-mix at="rsc_defaults"/>
    <clufter:descent-mix at="op_defaults"/>
    <clufter:descent-mix at="nodes"/>
    <clufter:descent-mix at="resources"/>
    <!-- constraints may refer to resource IDs from above -->
    <clufter:descent-mix at="constraints"/>
    <!-- fencing-level may refer to resource IDs from above,
         not enforced by schemas per se, but pcs mandates
         the referential integrity here, anyway
         (https://bugzilla.redhat.com/1441332#c7) -->
    <clufter:descent-mix at="fencing-topology"/>
    <clufter:descent-mix at="alerts"/>
    <!-- acls may refer to particular IDs (any) from above -->
    <clufter:descent-mix at="acls"/>

    <!-- enabling ACLs is sensible only at the very end of processing
         (was explicitly skipped while descenting into crm_config)
         XXX: should be more smoothly solved by using different modes
              with xsl:apply-templates, but that'd be quite an effort -->
    <xsl:variable name="CibAclEnable"
                  select="crm_config/cluster_property_set/nvpair[@name='enable-acl']"/>
    <xsl:if test="$CibAclEnable">


        <!-- "pcs acl" only supported with certain newer versions of
             pcs/pacemaker (https://bugzilla.redhat.com/1111369) -->
        <xsl:choose>
            <xsl:when test="$pcscmd_extra_acls">
''' + (
                verbose_inform('"set singleton cluster property: ", $CibAclEnable/@name')
) + '''
                <xsl:value-of select='concat($pcscmd_pcs, "property set")'/>
                <xsl:if test="$pcscmd_force">
                    <xsl:value-of select="' --force'"/>
                </xsl:if>
                <xsl:value-of select='concat(" &apos;", $CibAclEnable/@name,
                                             "=", $CibAclEnable/@value, "&apos;")'/>
                <xsl:value-of select="'%(NL)s'"/>
''' + (
                verbose_ec_test
) + '''
            </xsl:when>
            <xsl:otherwise>
                <xsl:message>%(acls_msg)s</xsl:message>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:if>

    <xsl:if test="not($pcscmd_dryrun) and $pcscmd_tmpcib">
''' + (
        verbose_inform('"push CIB: ", $pcscmd_tmpcib')
) + '''
        <xsl:value-of select="concat('pcs cluster cib-push ',
                                     $pcscmd_tmpcib, ' --config')"/>
        <xsl:value-of select="'%(NL)s'"/>
''' + (
        verbose_ec_test
) + '''
    </xsl:if>
''') % dict(
    NL=NL,
    acls_msg="WARNING: target pcs/pacemaker version does not support"
             " (new) ACLs, hence &apos;enable-acl&apos; property omitted",
)

###

from ....utils_xslt import xslt_is_member, xslt_string_mapping

from itertools import chain

cib_revitalize_deprecated_props_cluster_rsc = {
    'default-resource-stickiness': 'resource-stickiness',
    'is-managed-default':          'is-managed',
}

cib_revitalize_deprecated_props_cluster_op = {
    'default-action-timeout': 'timeout',
}

cib_revitalize_deprecated_props_cluster = \
    chain(cib_revitalize_deprecated_props_cluster_rsc,
          cib_revitalize_deprecated_props_cluster_op)

cib_revitalize = ('''\
    <xsl:copy>

    <!-- nested handling of crm_config: drop the innovated nvpairs -->
    <clufter:descent-mix at="crm_config"/>

    <!-- move deprecated crm_config properties to rsc_defaults -->
    <xsl:choose>
        <xsl:when test="crm_config/cluster_property_set/nvpair[
''' + (
                             xslt_is_member('@name',
                                            cib_revitalize_deprecated_props_cluster_rsc)
) + ''']">
            <rsc_defaults>
                <xsl:apply-templates select="rsc_defaults/nvpair"/>
                <xsl:for-each select="crm_config/cluster_property_set[nvpair[
''' + (
                             xslt_is_member('@name',
                                            cib_revitalize_deprecated_props_cluster_rsc)
) + ''']]">
                    <meta_attributes id="{concat(@id, '-', generate-id(.))}">
                    <!-- XXX make rewrite-id a generalized helper -->
                    <!-- xsl:if test="rule">
                        <xsl:call-template name="rewrite-id">
                            <xsl:with-param name="Elem" select="rule"/>
                            <xsl:with-param name="InstanceId" select="generate-id(rule)"/>
                        </xsl:call-template>
                    </xsl:if -->
                    <xsl:for-each select="nvpair[
''' + (
                             xslt_is_member('@name',
                                            cib_revitalize_deprecated_props_cluster_rsc)
) + ''']">
                        <nvpair id="{concat(@id, '-', generate-id(.))}">
                            <xsl:attribute name="name">
                                <xsl:choose>
''' + (
                                xslt_string_mapping(cib_revitalize_deprecated_props_cluster_rsc, '@name')
) + '''
                                </xsl:choose>
                            </xsl:attribute>
                            <xsl:attribute name="value">
                                <xsl:value-of select="@value"/>
                            </xsl:attribute>
                        </nvpair>
                    </xsl:for-each>
                    </meta_attributes>
                    <xsl:apply-templates select="rsc_defaults/score"/>
                </xsl:for-each>
            </rsc_defaults>
        </xsl:when>
        <xsl:otherwise>
            <xsl:apply-templates select="rsc_defaults"/>
        </xsl:otherwise>
    </xsl:choose>

    <!-- move deprecated crm_config properties to op_defaults -->
    <xsl:choose>
        <xsl:when test="crm_config/cluster_property_set/nvpair[
''' + (
                             xslt_is_member('@name',
                                            cib_revitalize_deprecated_props_cluster_op)
) + ''']">
            <op_defaults>
                <xsl:apply-templates select="op_defaults/nvpair"/>
                <xsl:for-each select="crm_config/cluster_property_set[nvpair[
''' + (
                             xslt_is_member('@name',
                                            cib_revitalize_deprecated_props_cluster_op)
) + ''']]">
                    <meta_attributes id="{concat(@id, '-', generate-id(.))}">
                    <!-- XXX make rewrite-id a generalized helper -->
                    <!-- xsl:if test="rule">
                        <xsl:call-template name="rewrite-id">
                            <xsl:with-param name="Elem" select="rule"/>
                            <xsl:with-param name="InstanceId" select="generate-id(rule)"/>
                        </xsl:call-template>
                    </xsl:if -->
                    <xsl:for-each select="nvpair[
''' + (
                             xslt_is_member('@name',
                                            cib_revitalize_deprecated_props_cluster_op)
) + ''']">
                        <nvpair id="{concat(@id, generate-id(.))}">
                            <xsl:attribute name="name">
                                <xsl:choose>
''' + (
                                xslt_string_mapping(cib_revitalize_deprecated_props_cluster_op)
) + '''
                                </xsl:choose>
                            </xsl:attribute>
                            <xsl:attribute name="value">
                                <xsl:value-of select="."/>
                            </xsl:attribute>
                        </nvpair>
                    </xsl:for-each>
                    </meta_attributes>
                    <xsl:apply-templates select="op_defaults/score"/>
                </xsl:for-each>
            </op_defaults>
        </xsl:when>
        <xsl:otherwise>
            <xsl:apply-templates select="op_defaults"/>
        </xsl:otherwise>
    </xsl:choose>

    <xsl:apply-templates select="*[not(
''' + (
        xslt_is_member('name()',
                       ('crm_config', 'rsc_defaults', 'op_defaults'))
) + ''')]"/>

    </xsl:copy>
''')
