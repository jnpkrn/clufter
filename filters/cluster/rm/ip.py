# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ..utils_cib import ResourceSpec


ccsflat2pcs = '''\
    <!--
        IPAddr2 ~ ip
     -->
    <xsl:when test="name() = 'ip'">
        <xsl:variable name="IpAddress"
                      select="substring-before(@address, '/')"/>
''' + \
        ResourceSpec('ocf:heartbeat:IPaddr2').xsl_attrs \
+ '''
        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
            <!-- ip (+ cidr_netmask) ~ address -->
            <nvpair id="{concat($Prefix, '-ATTRS-ip')}"
                    name="ip"
                    value="{@address}">
                <xsl:if test="$IpAddress">
                <xsl:attribute name="value">
                    <xsl:value-of select="$IpAddress"/>
                </xsl:attribute>
                </xsl:if>
            </nvpair>
            <xsl:if test="$IpAddress">
            <nvpair id="{concat($Prefix, '-ATTRS-cidr_netmask')}"
                    name="cidr_netmask"
                    value="{substring-after(@address, '/')}"/>
            </xsl:if>
        </instance_attributes>
    </xsl:when>
'''
