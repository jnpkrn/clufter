# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

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
'''
