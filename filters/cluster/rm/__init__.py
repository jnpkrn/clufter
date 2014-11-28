# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_xslt import xslt_is_member

###

# avoid accidental start of rgmanager, see bz#723925;
# only rm tag already present as only then there is a chance
# of having RGManager + service set to start on boot
ccs2ccs_pcmk = '''\
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
from .... import package_name

ccsflat2pcsprelude_elems = (
    'service',
    'vm',
)

ccsflat2pcsprelude = ('''\
    <xsl:for-each select="*[
''' + (
    xslt_is_member('name()', ccsflat2pcsprelude_elems)
) + ''']/*">
        <xsl:variable name="Prefix"
                      select="concat('RESOURCE-', name(), '-',
                                     @name,
                                     translate(@address, '/', '_')
                              )"/>
        <primitive id="{$Prefix}">

            <xsl:attribute name="description"
            ><xsl:value-of select="concat('natively converted from ', name(),
                                          ' RA')"
            /></xsl:attribute>

            <xsl:choose>

                <!-- the nested snippets should be guarded with
                     xsl:when name="foo" -->
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

            <!-- store service reference for later use -->

            <meta_attributes id="{$Prefix}-META">
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
                <!--nvpair id="{$Prefix}-META-domain"
                        name="rgmanager-domain"
                        value="{../@domain}"/-->
            </meta_attributes>
        </primitive>
    </xsl:for-each>

    <xsl:for-each select="*[
''' + (
    xslt_is_member('name()', ccsflat2pcsprelude_elems)
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
    note_unhandled='''<xsl:value-of select="concat('WARNING: resource ', name(),
                                                   ' is currently unhandled by',
                                                   ' the conversion, you are',
                                                   ' advised to copy ',
                                                   substring-before(
                                                       @rgmanager-meta-agent,
                                                       '.metadata'
                                                   ),
                                                   ' RGManager agent (incl.',
                                                   ' dependencies if any)',
                                                   ' to /usr/lib/ocf/resource.d',
                                                   '/rgmanager directory')"/>'''
)
