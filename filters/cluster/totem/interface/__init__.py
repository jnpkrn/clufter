# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from ....utils_xslt import xslt_is_member

###

ccs2needlexml_attrs = (
    'ringnumber',
    'bindnetaddr',
    'broadcast',
    'mcastaddr',
    'mcastport',
    'ttl',
)

ccs2needlexml = '''\
    <xsl:copy>
        <xsl:copy-of select="@*[
''' + (
            xslt_is_member('name()', ccs2needlexml_attrs)
) + ''']" />
    </xsl:copy>
'''

###

ccspcmk2pcscmd = '''\
    <xsl:variable name="RingNumber">
        <xsl:choose>
            <xsl:when test="@ringnumber = 0
                            or
                            (
                              not(@ringnumber)
                              and
                              count(preceding-sibling::interface) = 0
                            )">
                <xsl:value-of select="'0'"/>
            </xsl:when>
            <xsl:when test="@ringnumber = 1
                            or
                            (
                              not(@ringnumber)
                              and
                              count(preceding-sibling::interface) = 1
                            )">
                <xsl:value-of select="'1'"/>
            </xsl:when>
        </xsl:choose>
    </xsl:variable>
    <xsl:if test="$RingNumber">
        <xsl:if test="@bindnetaddr">
            <xsl:value-of select="concat(' --addr', $RingNumber,' ', @bindnetaddr)"/>
        </xsl:if>
        <xsl:if test="@mcastaddr">
            <xsl:value-of select="concat(' --mcast', $RingNumber,' ', @mcastaddr)"/>
        </xsl:if>
        <xsl:if test="@mcastport">
            <xsl:value-of select="concat(' --mcastport', $RingNumber,' ', @mcastport)"/>
        </xsl:if>
        <xsl:if test="@broadcast">
            <xsl:value-of select="concat(' --broadcast', $RingNumber)"/>
        </xsl:if>
    </xsl:if>
'''
