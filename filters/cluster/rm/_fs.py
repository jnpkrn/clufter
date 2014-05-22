# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

# XXX: normally, there would be fs.py containing this common implementation
#      and {cluster,net}.py referring to it, but due to the way it is used
#      in the parent, current approach seems better

from clufter.utils_cib import ResourceSpec


ccsflat2pcs = '''\
    <!--
        Filesystem ~ {,cluster,net}fs
     -->
    <xsl:when test="contains(concat(
                        '|fs',
                        '|netfs',
                        '|clusterfs'
                        '|'), concat('|', name(), '|'))">
        <xsl:variable name="FsKind">
            <xsl:choose>
                <!-- XXX could be as per meta-rgmanager-... -->
                <xsl:when test="not(@device)
                                and
                                @host
                                and
                                @export">
                    <xsl:value-of select="'netfs'"/>
                </xsl:when>
                <xsl:when test="contains(concat(
                                    '|gfs',
                                    '|gfs2',
                                    '|'), concat('|', @fstype, '|'))">
                    <xsl:value-of select="'clusterfs'"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="'fs'"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
''' + \
        ResourceSpec('ocf:heartbeat:Filesystem').xsl_attrs \
+ '''
        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
            <!-- device ~ device -->
            <nvpair id="{concat($Prefix, '-ATTRS-device')}"
                    name="device"/>
                <xsl:attribute name="value">
                    <xsl:choose>
                        <!-- LABEL or UUID specification -->
                        <xsl:when test="starts-with(@device, 'LABEL=')">
                            <xsl:value-of select="concat(
                                                      '-L',
                                                      substring-after(@device, 'LABEL=')
                                                  )"/>
                            </xsl:attribute>
                        </xsl:when>
                        <xsl:when test="starts-with(@device, 'UUID=')">
                            <xsl:value-of select="concat(
                                                      '-U',
                                                      substring-after(@device, 'UUID=')
                                                  )"/>
                        </xsl:when>
                        <!-- specification a la netfs-->
                        <xsl:when test="$FsKind = 'netfs'
                                        and
                                        starts-with(@fstype, 'nfs')">
                            <xsl:value-of select="concat(
                                                      @host,
                                                      ':',
                                                      @export)"/>
                        </xsl:when>
                        <xsl:when test="$FsKind = 'netfs'
                                        and
                                        starts-with(@fstype, 'cifs')">
                            <xsl:value-of select="concat(
                                                      '//'
                                                      @host,
                                                      '/',
                                                      @export)"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="@device">
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:attribute>
            <!-- directory ~ mountpoint -->
            <nvpair id="{concat($Prefix, '-ATTRS-directory')}"
                    name="directory"
                    value="{@mountpoint}"/>
            <!-- options ~ options -->
            <xsl:if test="@options or $FsKind = 'netfs'">
            <nvpair id="{concat($Prefix, '-ATTRS-options')}"
                    name="options"/>
                <xsl:attribute name="value">
                    <xsl:choose>
                        <xsl:when test="$FsKind = 'netfs'
                                        and
                                        starts-with(@fstype, 'nfs')">
                            <xsl:value-of select="'sync,soft,noac'"/>
                        </xsl:when>
                        <xsl:when test="$FsKind = 'netfs'
                                        and
                                        starts-with(@fstype, 'cifs')">
                            <xsl:value-of select="'guest'"/>
                        </xsl:when>
                        <xsl:when test="$FsKind != 'netfs'">
                            <xsl:value-of select="@options"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:message terminate="true"
                            >Unexpected *fs RA params combination witnessed.</xsl:message>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:attribute>
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
