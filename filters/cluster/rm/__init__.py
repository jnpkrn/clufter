# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_xslt import xslt_is_member

###

ccs_disable_rg = '''\
    <xsl:copy>
        <xsl:attribute name="disabled">1</xsl:attribute>
    </xsl:copy>
'''

###

ccs_obfuscate_identifiers = '''\

    <!-- FAILOVER-DOMAIN -->

    <xsl:variable name="FailoverDomain"
                  select="//rm/failoverdomains/failoverdomain[@name]"/>
    <xsl:template match="
        //rm/failoverdomains/failoverdomain/@name
        |//rm/service/@domain
        |//rm/vm/@domain">
        <xsl:variable name="FailoverDomainMatch"
                      select="$FailoverDomain[
                                  @name
                                  =
                                  current()
                              ][1]"/>
        <xsl:attribute name="{name()}">
            <xsl:choose>
                <xsl:when test="$FailoverDomainMatch">
                    <!-- 1+ match(es) found -->
                    <xsl:value-of select="concat(
                        'FAILOVER-DOMAIN-',
                        count($FailoverDomainMatch/preceding-sibling::failoverdomain) + 1
                    )"/>
                </xsl:when>
                <xsl:otherwise>
                    <!-- probably refential integrity error -->
                    <xsl:value-of select="concat(
                        'FAILOVER-DOMAIN-UNDEF-',
                        generate-id()
                    )"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:attribute>
    </xsl:template>

    <!-- SERVICE -->

    <xsl:variable name="Service"
                  select="//rm/service[@name or @ref]"/>
    <xsl:template match="
        //rm/service/@name
        |//rm/service/@ref
        |//rm/resource/@name">
        <xsl:variable name="ServiceMatch"
                      select="$Service[
                                  @name and @name = current()
                                  or
                                  @ref and @ref = current()
                              ][1]"/>
        <xsl:attribute name="{name()}">
            <xsl:choose>
                <xsl:when test="$ServiceMatch">
                    <!-- 1+ match(es) found -->
                    <xsl:value-of select="concat(
                        'SERVICE-',
                        count($ServiceMatch/preceding-sibling::service) + 1
                    )"/>
                </xsl:when>
                <xsl:otherwise>
                    <!-- unused service or refential integrity error -->
                    <xsl:value-of select="concat(
                        'SERVICE-UNUSED-',
                        generate-id()
                    )"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:attribute>
    </xsl:template>
'''

###

from ....utils_cib import ResourceSpec
from ....utils_xslt import xslt_id_friendly
from .... import package_name

ccsflat2cibprelude_elems_res_hybrid = (
    'vm',
)

ccsflat2cibprelude_elems_res_toplevel = ccsflat2cibprelude_elems_res_hybrid + (
    'service',
)

ccsflat2cibprelude = ('''\
    <xsl:for-each select="*[
''' + (
        xslt_is_member('name()', ccsflat2cibprelude_elems_res_hybrid)
) + ''']
    |
    *[
''' + (
        xslt_is_member('name()', ccsflat2cibprelude_elems_res_toplevel)
) + ''']/*[name() != 'action']">
        <!-- meta-primary can be, e.g., @address in case of ip,
             and that can contain '/' which is not NCNameChar -->
        <xsl:variable name="Spec"
                      select="
''' + (
                              xslt_id_friendly(
                                  '(@*[name() = current()/@rgmanager-meta-primary]'
                                  '|@name'
                                  '|@address'
                                  '|@SID'
                                  '|@InstanceName'
                                  ')[1]'
                              )
) + '''"/>
        <xsl:variable name="Prefix"
                      select="concat('RESOURCE-', name(), '-', $Spec)"/>
        <primitive id="{$Prefix}">

            <xsl:attribute name="description"
            ><xsl:value-of select="concat('natively converted from ', name(),
                                          ' RA')"
            /></xsl:attribute>

            <xsl:choose>

                <!-- make sure there is at least a single "when" -->
                <xsl:when test="false()"/>

                <!-- the nested snippets should be guarded with
                     xsl:when test="name() = 'foo'" -->
                <clufter:descent-mix at="*"/>

                <xsl:otherwise>

                    <xsl:attribute name="description"
                    ><xsl:value-of select="concat('could not natively convert',
                                                  ' from ', name(), ' RA')"
                    /></xsl:attribute>
''' + (
                    ResourceSpec('ocf:rgmanager:PLACEHOLDER').xsl_attrs
) + '''
                    <xsl:attribute name="type"
                    ><xsl:value-of select="substring-before(
                                               @rgmanager-meta-agent,
                                               '.metadata'
                                           )"
                    /></xsl:attribute>
                    <instance_attributes id="{$Prefix}-ATTRS">
                        <xsl:for-each select="@*[
                                                  name() != 'rgmanager-meta-agent'
                                              ]">
                            <nvpair id="{$Prefix}-ATTRS-{name()}"
                                    name="{name()}"
                                    value="{.}"/>
                        </xsl:for-each>
                    </instance_attributes>
                    <xsl:comment> %(note_unhandled)s </xsl:comment>
                    <xsl:message>%(note_unhandled)s</xsl:message>
                </xsl:otherwise>
            </xsl:choose>

            <xsl:if test="number(@__max_failures) &gt; 0
                          and
                          number(@__failure_expire_time) &gt; 0">
                <xsl:message>
                    <xsl:value-of select="concat('WARNING: failures in status',
                                                 ' checks (akin to __max_failures',
                                                 ' and __failure_expire_time) are',
                                                 ' always directly propagated',
                                                 ' in Pacemaker without any',
                                                 ' thresholding (', $Spec, ')')"/>
                </xsl:message>
            </xsl:if>

            <!-- store service reference for later use -->

            <meta_attributes id="{$Prefix}-META">
                <xsl:if test="
''' + (
                    xslt_is_member('name(..)',
                                   ccsflat2cibprelude_elems_res_toplevel)
) + '''">
                    <nvpair id="{$Prefix}-META-service"
                            name="rgmanager-service"
                            value="{concat(
                                    translate(
                                        name(..),
                                        'abcdefghijklmnopqrstuvwxyz',
                                        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                    ),
                                    '-',
                                    ../@name
                                )}"/>
                </xsl:if>
                <xsl:variable name="IntervalFound"
                              select="action[
                                  (
                                      @name = 'monitor'
                                      or
                                      @name = 'status'
                                  )
                                  and
                                  not(preceding-sibling::action[
                                      (
                                          @name = 'monitor'
                                          or
                                          @name = 'status'
                                      )
                                      and
                                      @depth &lt; current()/@depth
                                  ])
                                  and
                                  not(following-sibling::action[
                                      (
                                          @name = 'monitor'
                                          or
                                          @name = 'status'
                                      )
                                      and
                                      @depth &lt; current()/@depth
                                  ])
                              ]/@interval"/>
                <xsl:variable name="Interval">
                    <xsl:value-of select="$IntervalFound"/>
                    <xsl:if test="not($IntervalFound)">
                        <xsl:value-of select="'60'"/>
                    </xsl:if>
                </xsl:variable>
                <nvpair id="{$Prefix}-META-monitor"
                        name="rgmanager-monitor"
                        value="{concat($Interval, 's')}"/>
                <!--nvpair id="{$Prefix}-META-domain"
                        name="rgmanager-domain"
                        value="{../@domain}"/-->
            </meta_attributes>
        </primitive>
    </xsl:for-each>

    <xsl:for-each select="*[
''' + (
    xslt_is_member('name()', ccsflat2cibprelude_elems_res_toplevel)
) + ''']">
        <xsl:variable name="ResourceGroup"
                      select="concat(
                                  translate(
                                      name(),
                                      'abcdefghijklmnopqrstuvwxyz',
                                      'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                  ),
                                  '-',
                                  @name
                              )"/>
        <template id="{$ResourceGroup}"
                class="ocf"
                provider="%(package_name)s"
                type="temporary-service">
            <meta_attributes id="{$ResourceGroup}-META">
                <xsl:if test="@domain">
                    <nvpair id="{$ResourceGroup}-META-domain"
                            name="domain"
                            value="FAILOVERDOMAIN-{@domain}"/>
                </xsl:if>
                <nvpair id="{$ResourceGroup}-META-autostart"
                        name="autostart"
                        value="{@autostart}">
                    <xsl:if test="not(@autostart)">
                        <xsl:attribute name="value">1</xsl:attribute>
                    </xsl:if>
                </nvpair>
                <nvpair id="{$ResourceGroup}-META-exclusive"
                        name="exclusive"
                        value="{@exclusive}">
                    <xsl:if test="not(@exclusive)">
                        <xsl:attribute name="value">0</xsl:attribute>
                    </xsl:if>
                </nvpair>
                <nvpair id="{$ResourceGroup}-META-recovery"
                        name="recovery"
                        value="{@recovery}"/>
                <nvpair id="{$ResourceGroup}-META-depend"
                        name="depend"
                        value="{@depend}"/>
                <nvpair id="{$ResourceGroup}-META-depend_mode"
                        name="depend_mode"
                        value="{@depend_mode}"/>
                <nvpair id="{$ResourceGroup}-META-max_restarts"
                        name="max_restarts"
                        value="{@max_restarts}"/>
                <nvpair id="{$ResourceGroup}-META-restart_expire_time"
                        name="restart_expire_time"
                        value="{@restart_expire_time}"/>
                <nvpair id="{$ResourceGroup}-META-priority"
                        name="priority"
                        value="{@priority}"/>
            </meta_attributes>
        </template>
    </xsl:for-each>

    <clufter:descent at="failoverdomain"/>
''') % dict(
    package_name=package_name(),
    note_unhandled='''<xsl:value-of select="concat('WARNING: resource `',
                                                   name(),
                                                   '` is currently unhandled',
                                                   ' in the conversion, you',
                                                   ' are advised to copy ',
                                                   substring-before(
                                                       @rgmanager-meta-agent,
                                                       '.metadata'
                                                   ),
                                                   ' RGManager agent (incl.',
                                                   ' dependencies if any)',
                                                   ' to /usr/lib/ocf/resource.d',
                                                   '/rgmanager directory')"/>'''
)

###

ccs_revitalize = '''\
    <xsl:template match="service
                          |service//*[name() != 'action']
                          |vm
                          |vm//*[name() != 'action']
                          |resources/*">
        <xsl:choose>
            <!-- omit resources with repeated primary attribute
                 rgmanager/src/daemons/reslist.c:store_resource:attribute collision
                 (simplified a bit - limited just to sibling scope)
                 XXX: this will only work for config preprocessed with
                      ccs_flatten
             -->
            <xsl:when test="preceding-sibling::*[
                                name() = name(current())
                                and
                                current()/@rgmanager-meta-primary
                                and
                                @*[
                                    name() = current()/@rgmanager-meta-primary
                                ] = current()/@*[
                                    name() = current()/@rgmanager-meta-primary
                                ]
                             ]">
                <xsl:message>
                    <xsl:value-of select="concat('WARNING: omitting resource',
                                                ' with repeated primary',
                                                ' attribute (', name(), '/@',
                                                @rgmanager-meta-primary, '=',
                                                @*[
                                                    name()
                                                    =
                                                    current()/@rgmanager-meta-primary
                                                ], ')'
                                          )"/>
                </xsl:message>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy>
                    <xsl:choose>
                        <!-- omit __max_failures + __failure_expire_time when
                             used without any real effect -->
                        <xsl:when test="not(@__max_failures)
                                        !=
                                        not(@__failure_expire_time)
                                        or
                                        number(@__max_failures) &lt;= 0
                                        or
                                        number(@__failure_expire_time) &lt; 0">
                            <xsl:message>
                                <xsl:value-of select="concat('WARNING: __max_failures',
                                                             ' and __failure_expire_time',
                                                             ' must be specified in pair',
                                                             ' and both of them has to be',
                                                             ' positive numbers; not',
                                                             ' satisfied, hence dropped',
                                                             '(', name(),')')"/>
                            </xsl:message>
                            <xsl:apply-templates select="@*[
                                                             not(
''' + (
                                xslt_is_member('name()',
                                               ('__max_failures',
                                                '__failure_expire_time'))
) + ''')]"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:apply-templates select="@*"/>
                        </xsl:otherwise>
                    </xsl:choose>
                    <xsl:apply-templates select="@*|node()"/>
                </xsl:copy>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
'''
