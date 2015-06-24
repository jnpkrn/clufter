# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

###

needlexml2pcscmd = '''\
    <xsl:variable name="RingNumber">
        <xsl:choose>
            <xsl:when test="@ringnumber">
                <xsl:value-of select="@ringnumber"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="count(
                    preceding-sibling::interface[not(@ringnumber)]
                )"/>
            </xsl:otherwise>
        <xsl:choose>
    </xsl:variable>
    <xsl:if test="$RingNumber &gt;= 0 or $RingNumber &lt;= 1">
        <xsl:if test="@bindnetaddr">
            <xsl:value-of select="concat(' --addr', $RingNumber, ' ', @bindnetaddr)"/>
        </xsl:if>
        <xsl:choose>
            <xsl:when test="@broadcast = 'yes'">
                <xsl:value-of select="concat(' --broadcast', $RingNumber)"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:if test="@mcastaddr">
                    <xsl:value-of select="concat(' --mcast', $RingNumber, ' ', @mcastaddr)"/>
                </xsl:if>
                <xsl:if test="@mcastport">
                    <xsl:value-of select="concat(' --mcastport', $RingNumber, ' ', @mcastport)"/>
                </xsl:if>
                <xsl:if test="@ttl">
                    <xsl:value-of select="concat(' --ttl', $RingNumber, ' ', @ttl)"/>
                </xsl:if>
            <xsl:otherwise>
        </xsl:choose>
    </xsl:if>
'''
