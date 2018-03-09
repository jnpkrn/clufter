# -*- coding: UTF-8 -*-
# Copyright 2018 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

###

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....utils_xslt import NL, xslt_is_member


needlexml2pcscmd_attrs = (
    'algorithm',  # required
    'connect_timeout',
    'force_ip_version',
    'host',  # required
    'port',
    'tie_breaker',
    'tls',  # see https://bugzilla.redhat.com/1476862
)

needleqdevicexml2pcscmd = '''\
    <xsl:when test="@model = 'net' and $pcscmd_extra_qnet">
        <xsl:for-each select="net/@*[
''' + (
            xslt_is_member('name()', needlexml2pcscmd_attrs)
) + ''']">
            <xsl:choose>
                <xsl:when test="name() = 'tls'
                                and
                                . = 'on'">
                </xsl:when>
                <xsl:when test="name() = 'tls'">
                    <xsl:message>
                        <xsl:value-of select="concat('WARNING: non-default',
                                                     ' `quorum.device.net.tls`',
                                                     ' value `', ., '` specified,',
                                                     ' but current pcs not capable',
                                                     ' to set it')"/>
                    </xsl:message>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="concat(' ', name(), '=', .)"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:for-each>
    </xsl:when>
    <xsl:when test="@model = 'net'">
        <xsl:value-of select="'clufter:UNSUPPORTED'"/>
    </xsl:when>
'''
