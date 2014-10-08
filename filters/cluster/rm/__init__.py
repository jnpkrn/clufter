# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_xslt import xslt_is_member


# avoid accidental start of rgmanager, see bz#723925;
# only rm tag already present as only then there is a chance
# of having RGManager + service set to start on boot
ccs2ccs_pcmk = '''\
    <xsl:copy>
        <xsl:attribute name="disabled">1</xsl:attribute>
    </xsl:copy>
'''


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


ccsflat2pcs_elems = (
    'service',
    'vm',
)

ccsflat2pcs = '''\
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
        </primitive>
    </xsl:for-each>
'''
