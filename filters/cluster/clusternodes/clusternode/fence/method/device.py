# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

ccs_obfuscate_credentials = '''\
    <xsl:copy>
        <xsl:copy-of select="@*"/>
        <xsl:for-each select="@*">
            <xsl:if test="contains(concat(
                '|login',
                '|'), concat('|', name(), '|'))">
                <xsl:attribute name="{name()}">SECRET-LOGIN</xsl:attribute>
            </xsl:if>
            <xsl:if test="contains(concat(
                '|community',
                '|passwd',
                '|snmp_priv_passwd',
                '|'), concat('|', name(), '|'))">
                <xsl:attribute name="{name()}">SECRET-PASSWORD</xsl:attribute>
            </xsl:if>
        </xsl:for-each>
    </xsl:copy>
'''
