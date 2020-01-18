# -*- coding: UTF-8 -*-
# Copyright 2020 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

# following 2nd chance import is to allow direct usage context (testing, etc.)
try:
    from ....utils_xslt import xslt_is_member
except (ImportError, ValueError):
    from ...utils_xslt import xslt_is_member

###

# XXX: normally, there would be fs.py containing this common implementation
#      and {cluster,net}.py referring to it, but due to the way it is used
#      in the parent, current approach seems better

try:
    from ....utils_cib import ResourceSpec
except (ImportError, ValueError):
    from ...utils_cib import ResourceSpec

ccsflat2cibprelude = ('''
    <!--
        Filesystem ~ {,cluster,net}fs
     -->
    <xsl:when test="name() = '%(target)s'">
        <xsl:variable name="FsKind" select="name()"/>
''' + (
        ResourceSpec('ocf:heartbeat:Filesystem').xsl_attrs
) + '''
        <!-- INSTANCE_ATTRIBUTES -->
        <instance_attributes id="{concat($Prefix, '-ATTRS')}">
            <!-- device ~ device -->
            <nvpair id="{concat($Prefix, '-ATTRS-device')}"
                    name="device">
                <xsl:attribute name="value">
                    <xsl:choose>
                        <!-- LABEL or UUID specification -->
                        <xsl:when test="starts-with(@device, 'LABEL=')">
                            <xsl:value-of select="concat(
                                                      '-L',
                                                      substring-after(@device, 'LABEL=')
                                                  )"/>
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
                                        (
                                            not(@fstype)
                                            or
                                            starts-with(@fstype, 'nfs')
                                        )">
                            <xsl:value-of select="concat(
                                                      @host,
                                                      ':',
                                                      @export)"/>
                        </xsl:when>
                        <xsl:when test="$FsKind = 'netfs'
                                        and
                                        starts-with(@fstype, 'cifs')">
                            <xsl:value-of select="concat(
                                                      '//',
                                                      @host,
                                                      '/',
                                                      @export)"/>
                        </xsl:when>
                        <xsl:when test="$FsKind = 'bind-mount'">
                            <xsl:value-of select="@source"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="@device"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:attribute>
            </nvpair>
            <!-- directory ~ mountpoint -->
            <nvpair id="{concat($Prefix, '-ATTRS-directory')}"
                    name="directory"
                    value="{@mountpoint}"/>
            <!-- fstype ~ fstype -->
            <xsl:if test="@fstype or $FsKind = 'bind-mount'">
            <nvpair id="{concat($Prefix, '-ATTRS-fstype')}"
                    name="fstype">
                <xsl:attribute name="value">
                    <xsl:choose>
                        <xsl:when test="$FsKind = 'bind-mount'">
                            <xsl:value-of select="'none'"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="@fstype"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:attribute>
            </nvpair>
            </xsl:if>
            <!-- options ~ options -->
            <xsl:if test="@options
                          or
''' + (
                          xslt_is_member('$FsKind', ('netfs', 'bind-mount'))
) + '''">
            <nvpair id="{concat($Prefix, '-ATTRS-options')}"
                    name="options">
                <xsl:attribute name="value">
                    <xsl:choose>
                        <xsl:when test="$FsKind = 'bind-mount'">
                            <xsl:value-of select="'bind'"/>
                        </xsl:when>
                        <xsl:when test="@options">
                            <xsl:value-of select="@options"/>
                        </xsl:when>
                        <xsl:when test="$FsKind = 'netfs'
                                        and
                                        (
                                            not(@fstype)
                                            or
                                            starts-with(@fstype, 'nfs')
                                        )">
                            <xsl:value-of select="'sync,soft,noac'"/>
                        </xsl:when>
                        <xsl:when test="$FsKind = 'netfs'
                                        and
                                        starts-with(@fstype, 'cifs')">
                            <xsl:value-of select="'guest'"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:message terminate="yes"
                            >Unexpected *fs RA params combination witnessed.</xsl:message>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:attribute>
            </nvpair>
            </xsl:if>
            <!-- run_fsck ~ force_fsck -->
            <xsl:if test="$FsKind != 'bind-mount'
                          and
''' + (
                xslt_is_member('@force_fsck', ('1', 'yes'))
) + '''">
            <nvpair id="{concat($Prefix, '-ATTRS-run_fsck')}"
                    name="run_fsck"
                    value="force"/>
            </xsl:if>
            <!-- force_unmount (true|safe|false) ~ force_unmount (true...|false...)
                 - this depends on
                   https://github.com/ClusterLabs/resource-agents/pull/423
                 - alternatively the commented out part below might be used
                   to achieve similar behavior (no signal ever sent) -->
            <nvpair id="{concat($Prefix, '-ATTRS-force_unmount')}"
                    name="force_unmount"
                    value="false">
                <xsl:if test="not(
''' + (
                    xslt_is_member('@force_unmount', ('1', 'yes', 'on', 'true'))
) + ''')">
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
                interval="0"
                timeout="1"/>
        </operations>
        </xsl:if -->
    </xsl:when>
''') % dict(target=__name__.rsplit('.', 1)[-1].split('_', 1)[-1])
