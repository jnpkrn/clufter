# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

###

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....utils_xslt import NL, xslt_is_member, xslt_string_mapping


needlexml2pcscmd_attrs = (
    'algorithm',
    'connect_timeout',
    'force_ip_version',
    'host',
    'port',
    'tie_breaker',
    'tls',
)

needleqdevicexml2pcscmd = '''\
    <xsl:when test="@model = 'net' and $pcscmd_extra_qnet">
        <xsl:for-each select="net/@*[
''' + (
            xslt_is_member('name()', needlexml2pcscmd_attrs)
) + ''']">
            <xsl:value-of select="concat(' ', name(), '=', .)"/>
        </xsl:for-each>
    </xsl:when>
    <xsl:when test="@model = 'net'">
        <xsl:value-of select="'clufter:UNSUPPORTED'"/>
    </xsl:when>
'''
