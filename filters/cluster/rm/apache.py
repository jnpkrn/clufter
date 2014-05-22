# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from clufter.utils_cib import ResourceSpec


flatccs2pcs = '''\
    <!--
        apache ~ apache
     -->
    <xsl:when test="name() = 'apache'">
''' + \
        ResourceSpec('ocf:heartbeat:apache').xsl_attrs \
+ '''
        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
            <!-- configfile ~ config_file (if present) -->
            <xsl:if test="@config_file">
                <nvpair id="{concat($Prefix, '-ATTRS-configfile')}"
                        name="configfile"
                        value="{@config_file}"/>
            </xsl:if>
            <!-- options ~ httpd_options (if present; + name, server_root) -->
            <nvpair id="{concat($Prefix, '-ATTRS-options')}"
                    name="options"/>
                <xsl:attribute name="value">
                    <xsl:value-of select="concat(
                        ' -D\&quot;', @name, '\&quot;'
                    )"/>
                    <xsl:if test="@server_root">
                        <xsl:value-of select="concat(
                            ' -d \&quot;', @server_root, '\&quot;'
                        )"/>
                    </xsl:if>
                    <xsl:if test="@httpd_options">
                        <xsl:value-of select="concat(
                            ' ', @httpd_options
                        )"/>
                    </xsl:if>
                </xsl:attribute>
        </instance_attributes>

        <!-- OPERATIONS -->
        <operations>
            <xsl:if test="@shutdown_wait">
            <op id="{concat($Prefix, '-OPS-shutdown')}"
                name="stop"
                timeout="{concat(@shutdown_wait, 's')}"/>
            </xsl:if>
        </operations>
    </xsl:when>
'''
