# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

###

# NOTE pcs doesn't support udpb directly via --transport (unless forced),
#      one has to specify --broadcast0 parameter instead and transport
#      will get silently switched to udpb

from ....utils_xslt import xslt_is_member

needlexml2pcscmd_transports = ('udp', 'udpu')
needlexml2pcscmd_rrp_mode = ('active', 'passive')
# 1:1 mapping of supported params to pcs arguments (not: rrpmode)
needlexml2pcscmd_supported = (
    'consensus',
    'join',
    'token',
    'token_coefficients',
    'fail_recv_const',
    'miss_count_const',
    'token_coefficient',
)

needlexml2pcscmd = '''\
    <!-- transport -->
    <xsl:if test="
''' + (
    xslt_is_member('@transport', needlexml2pcscmd_transports)
) + '''">
        <xsl:value-of select="concat(' --transport ', @transport)"/>
    </xsl:if>

    <!-- rrpmode -->
    <xsl:if test="
''' + (
    xslt_is_member('@rrp_mode', needlexml2pcscmd_rrp_mode)
) + '''">
        <xsl:value-of select="concat(' --rrpmode ', @rrp_mode)"/>
    </xsl:if>

    <clufter:descent-mix at="interface"/>

    <!-- ipv6? -->
    <xsl:if test="@ip_version = 'ipv6'">
        <xsl:value-of select="' --ipv6'"/>
    </xsl:if>

    <xsl:for-each select="@*[
''' + (
        xslt_is_member('name()', needlexml2pcscmd_supported)
) + ''']">
        <xsl:if test=".">
            <xsl:value-of select="concat(' --', name(), ' ', .)"/>
        </xsl:if>
    </xsl:for-each>
'''
