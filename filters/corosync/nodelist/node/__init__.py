# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)


###

needlexml2pcscmd = '''\
    <xsl:value-of select="concat(' ', @ring0_addr)"/>
    <xsl:if test="@ring1_addr">
        <xsl:value-of select="concat(',', @ring1_addr)"/>
    </xsl:if>
'''
