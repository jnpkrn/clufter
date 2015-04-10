# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)


###

# NOTE copy of filters/cluster/cman/multicast/__init__.py + s/0/1/

ccspcmk2pcscmd = '''\
    <xsl:if test="@addr">
        <xsl:value-of select="concat(' --mcast1 ', @addr)"/>
    </xsl:if>
    <xsl:if test="@port">
        <xsl:value-of select="concat(' --mcastport1 ', @port)"/>
    </xsl:if>
    <xsl:if test="@ttl">
        <xsl:value-of select="concat(' --ttl1 ', @ttl)"/>
    </xsl:if>
'''
