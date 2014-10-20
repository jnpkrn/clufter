# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"


pcsprelude2pcscompact = '''\
    <clufter:descent-mix preserve-rest="true"/>
    <!-- strip empty optional elements -->
    <xsl:template match="fencing-topology[count(*) = 0]"/>
'''

###

from .... import package_name

pcscompact2pcs = ('''\
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
                                        <xsl:for-each select="$FailoverDomain/meta_attributes/nvpair[
                                                                  starts-with(@name, 'failoverdomainnode-')
                                                              ]">
                                            <expression id="CONSTRAINT-LOCATION-{$Resource/@id}-RESTRICTED-{@value}-expr"
                                                        attribute="#uname"
                                                        operation="ne"
                                                        value="{@value}"/>
                                        </xsl:for-each>
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
