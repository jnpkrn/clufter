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

from .... import package_name

ccsflat2pcs_elems = (
    'service',
    'vm',
)

ccsflat2pcs = ('''\
    <xsl:for-each select="*[
''' + ( \
    xslt_is_member('name()', ccsflat2pcs_elems)
) + ''']/*">
        <xsl:variable name="Prefix"
                      select="concat('RESOURCE-', name(), '-',
                                     @name,
                                     translate(@address, '/', '_')
                              )"/>
        <primitive id="{$Prefix}">
            <xsl:choose>

                <!-- the nested snippets should be guarded with
                     xsl:when name="foo" -->
                <clufter:descent-mix at="*"/>

                <xsl:otherwise>
                    <xsl:message terminate="no">
                        <value-of select="concat('unhandled resource: ', name())"/>
                    </xsl:message>
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
''' + ( \
    xslt_is_member('name()', ccsflat2pcs_elems)
) + ''']">
        <xsl:variable name="Container"
                      select="concat(
                                  translate(
                                      name(),
                                      'abcdefghijklmnopqrstuvwxyz',
                                      'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                  ),
                                  '-',
                                  @name
                              )"/>
        <template id="{$Container}"
                class="ocf"
                provider="%(package_name)s"
                type="temporary-service">
            <meta_attributes id="{$Container}-META">
                <nvpair id="{$Container}-META-domain"
                        name="domain"
                        value="FAILOVERDOMAIN-{@domain}"/>
                <nvpair id="{$Container}-META-autostart"
                        name="autostart"
                        value="{@autostart}"/>
                <nvpair id="{$Container}-META-exclusive"
                        name="exclusive"
                        value="{@exclusive}"/>
                <nvpair id="{$Container}-META-recovery"
                        name="recovery"
                        value="{@recovery}"/>
                <nvpair id="{$Container}-META-depend"
                        name="depend"
                        value="{@depend}"/>
                <nvpair id="{$Container}-META-depend_mode"
                        name="depend_mode"
                        value="{@depend_mode}"/>
                <nvpair id="{$Container}-META-max_restarts"
                        name="max_restarts"
                        value="{@max_restarts}"/>
                <nvpair id="{$Container}-META-restart_expire_time"
                        name="restart_expire_time"
                        value="{@restart_expire_time}"/>
                <nvpair id="{$Container}-META-priority"
                        name="priority"
                        value="{@priority}"/>
            </meta_attributes>
        </template>
    </xsl:for-each>

    <clufter:descent at="failoverdomain"/>
''') % dict(package_name=package_name())
