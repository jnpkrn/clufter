# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ...utils_cib import ResourceSpec


ccsflat2pcs = '''\
    <!--
        VirtualDomain ~ vm
     -->
    <xsl:when test="name() = 'vm'">
''' + \
        ResourceSpec('ocf:heartbeat:VirtualDomain').xsl_attrs \
+ '''
        <!-- SHOW-STOPPERS -->
        <xsl:if test="@use_virsh = '0'">
            <xsl:message terminate="true"
            >Cannot reliably convert non-virsh configuration</xsl:message>
        </xsl:if>

        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
            <!-- config ~ xmlfile -->
            <xsl:if test="@xmlfile or @path">
            <nvpair id="{concat($Prefix, '-ATTRS-config')}"
                    name="config"
                    value="{@xmlfile}">
                <xsl:if test="not(@xmlfile)">
                    <xsl:attribute name="value">
                        <!-- XXX simply assume the extension -->
                        <xsl:value-of select="concat(@path, '/', @name, '.xml')"/>
                    </xsl:attribute>
                </xsl:if>
            </nvpair>
            </xsl:if>
            <!-- hypervisor ~ hypervisor_uri -->
            <xsl:if test="@hypervisor_uri">
            <nvpair id="{concat($Prefix, '-ATTRS-hypervisor')}"
                    name="hypervisor"
                    value="{@hypervisor_uri}"/>
            </xsl:if>
            <!-- snapshot ~ snapshot -->
            <xsl:if test="@snapshot">
            <nvpair id="{concat($Prefix, '-ATTRS-snapshot')}"
                    name="snapshot"
                    value="{@snapshot}"/>
            </xsl:if>
        </instance_attributes>
    </xsl:when>
'''
