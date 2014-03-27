# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

ccs_obfuscate_identifiers = '''\

    <!-- REL-FENCE-METHOD -->

    <xsl:copy>
        <xsl:apply-templates select="@*"/>
        <xsl:for-each select="node()">
            <xsl:choose>
                <xsl:when test="name() = 'method'">
                    <xsl:variable name="MethodPos"
                                  select="count(preceding-sibling::method) + 1"/>
                    <xsl:copy>
                        <xsl:copy-of select="@*"/>
                        <xsl:for-each select="@name">
                            <xsl:attribute name="{name()}">
                                <xsl:value-of select="concat(
                                    'REL-FENCE-METHOD-', $MethodPos
                                )"/>
                            </xsl:attribute>
                        </xsl:for-each>
                        <xsl:apply-templates/>
                    </xsl:copy>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:copy>
                        <xsl:apply-templates/>
                    </xsl:copy>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:for-each>
    </xsl:copy>
'''
