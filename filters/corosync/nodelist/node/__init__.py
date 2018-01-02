# -*- coding: UTF-8 -*-
# Copyright 2018 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

needlexml2pcscmd = '''\
    <xsl:value-of select="concat(' ', @ring0_addr)"/>
    <xsl:if test="@ring1_addr">
        <xsl:value-of select="concat(',', @ring1_addr)"/>
    </xsl:if>
    <xsl:if test="@name">
        <!-- https://bugzilla.redhat.com/1183103 -->
        <xsl:message>
            <xsl:value-of select="concat('WARNING: `nodelist.node.name`',
                                         ' value `', ., '` specified,',
                                         ' but current pcs not capable',
                                         ' to set it')"/>
        </xsl:message>
    </xsl:if>
'''
