# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)


###

ccspcmk2pcscmd = '''\
    <xsl:if test="@addr">
        <xsl:value-of select="concat(' --mcast0 ', @addr)"/>
    </xsl:if>
    <xsl:if test="@port">
        <xsl:value-of select="concat(' --mcastport0 ', @port)"/>
    </xsl:if>
    <xsl:if test="@ttl">
        <xsl:value-of select="concat(' --ttl0 ', @ttl)"/>
    </xsl:if>
'''
