# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

ccsflat2pcs = '''\
    <template id="{concat('FENCEDEV-', @name)}"
              class="stonith"
              type="{@agent}">
        <xsl:variable name='FenceDevName' select="@name"/>
        <instance_attributes id="{concat('FENCEDEV-', @name, '-ATTRS')}">
        <xsl:for-each select="@*[name() != 'agent' and name() != 'name']">
            <nvpair id="{concat('FENCEDEV-', $FenceDevName, '-ATTRS-', name())}"
                    name="{name()}"
                    value="{.}"/>
        </xsl:for-each>
        </instance_attributes>
    </template>
'''

ccs_obfuscate_credentials = '''\
    <xsl:copy>
        <xsl:apply-templates select="@*"/>
        <xsl:for-each select="@*[contains(concat(
                '|passwd',
                '|snmp_priv_passwd',
                '|'), concat('|', name(), '|'))]">
                <xsl:attribute name="{name()}">SECRET-PASSWORD</xsl:attribute>
        </xsl:for-each>
        <xsl:for-each select="@*[contains(concat(
                '|login',
                '|'), concat('|', name(), '|'))]">
                <xsl:attribute name="{name()}">SECRET-LOGIN</xsl:attribute>
        </xsl:for-each>
        <xsl:apply-templates/>
    </xsl:copy>
'''

ccs_revitalize = '''\
    <!-- xvm: domain -> port -->
    <xsl:template match="fencedevice[@agent = 'xvm']">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:for-each select="@domain">
                <xsl:attribute name="port">
                    <xsl:value-of select="."/>
                </xsl:attribute>
            </xsl:for-each>
            <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>
'''
