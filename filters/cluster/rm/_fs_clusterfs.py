# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"


ccsflat2pcs = '''\
    <!--
        Filesystem ~ (fs|clusterfs)
     -->
    <xsl:when test="name() = 'fs'
                    or
                    name() = 'clusterfs'">
        <xsl:attribute name='type'>Filesystem</xsl:attribute>

        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
            <!-- device ~ device -->
            <nvpair id="{concat($Prefix, '-ATTRS-device')}"
                    name="device"
                    value="{@device}"/>
                <xsl:if test="starts-with(@device, 'LABEL=')">
                    <xsl:attribute name="value">
                        <xsl:value-of select="concat(
                                                  '-L',
                                                  substring-after(@device, 'LABEL=')
                                              )"/>
                    </xsl:attribute>
                </xsl:if>
                <xsl:if test="starts-with(@device, 'UUID=')">
                    <xsl:attribute name="value">
                        <xsl:value-of select="concat(
                                                  '-U',
                                                  substring-after(@device, 'UUID=')
                                              )"/>
                    </xsl:attribute>
            <!-- directory ~ mountpoint -->
            <nvpair id="{concat($Prefix, '-ATTRS-directory')}"
                    name="directory"
                    value="{@mountpoint}"/>
            <!-- options ~ options -->
            <xsl:if test="@options and @options != ''">
            <nvpair id="{concat($Prefix, '-ATTRS-options')}"
                    name="options"
                    value="{@options}"/>
            </xsl:if>
            <!-- run_fsck ~ force_fsck -->
            <xsl:if test="@force_fsck = '1' or @force_fsck = 'yes'">
            <nvpair id="{concat($Prefix, '-ATTRS-run_fsck')}"
                    name="run_fsck"
                    value="force"/>
            </xsl:if>
            <!-- force_unmount (true|safe|false) ~ force_unmount (true...|false...)
                 - this depends on
                   https://github.com/ClusterLabs/resource-agents/pull/423
                 - alternatively the comment out part below might be used
                   to achieve similar behavior (no signal ever sent) -->
            <nvpair id="{concat($Prefix, '-ATTRS-force_unmount')}"
                    name="force_unmount"
                    value="false">
                <xsl:if test="not(contains(concat(
                                  '|yes',
                                  '|on',
                                  '|true',
                                  '|1',
                                  '|'), concat('|', @force_unmount, '|')))">
                    <xsl:attribute name="value">
                        <xsl:value-of select="'safe'"/>
                    </xsl:attribute>
                </xsl:if>
            </nvpair>
            </instance_attributes>
        <!-- xsl:if test="not(contains(concat(
                          '|yes',
                          '|on',
                          '|true',
                          '|1',
                          '|'), concat('|', @force_unmount, '|')))">
        < operations>
            - this should cause no signal is ever sent to FS users -
            <op id="{concat($Prefix, '-OPS-shutdown')}"
                name="stop"
                timeout="1"/>
        </operations>
        </xsl:if -->
    </xsl:when>
'''
