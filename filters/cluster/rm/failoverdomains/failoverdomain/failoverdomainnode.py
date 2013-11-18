# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

obfuscate_identifiers = '''\
    <xsl:copy>
        <xsl:copy-of select="@*"/>
        <xsl:if test="@name">
            <xsl:attribute name="name">
                <xsl:for-each select="(key('clusternode_key', @name) | .)[0]">
                    <xsl:choose>
                        <xsl:when test="generate-id() = generate-id(current())">
                            <xsl:value-of select="'UNTRACKED-NODE'"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="concat('NODE-', position())"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:for-each>
            </xsl:attribute>
        </xsl:if>
    </xsl:copy>
'''
