# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

###

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....utils_xslt import NL, xslt_is_member

needlexml2pcscmd_attrs = (
    # model has a special role here
    'sync_timeout',
    'timeout',
    'votes',
)
needleqdevicexml2pcscmd = ('''\
    <!-- "pcs quorum device add" only supported with certain newer
         versions of pcs, support for qdevice itself in corosync
         ditto -->
    <xsl:choose>
        <xsl:when test="$pcscmd_extra_qdevice">
            <xsl:variable name="ModelOpts">
                <xsl:choose>

                    <!-- make sure there is at least a single "when" -->
                    <xsl:when test="false()"/>

                    <!-- the nested snippets should be guarded with
                         xsl:when test="@model = 'foo'" -->
                    <clufter:descent-mix at="*"/>

                    <xsl:otherwise>
                        <xsl:value-of select="'clufter:UNKNOWN'"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:variable>
            <xsl:choose>
                <xsl:when test="not(starts-with($ModelOpts, 'clufter:'))">
''' + (
                    verbose_inform('"add quorum device: ", @model, " model"')
) + '''
                    <xsl:value-of select="'pcs quorum device add'"/>

                    <xsl:for-each select="@*[
''' + (
                        xslt_is_member('name()', needlexml2pcscmd_attrs)
) + ''']">
                        <xsl:value-of select="concat(' ', name(), '=', .)"/>
                    </xsl:for-each>

                    <xsl:value-of select="concat(' model ', @model, $ModelOpts)"/>

                    <xsl:value-of select="'%(NL)s'"/>
''' + (
                    verbose_ec_test
) + '''
                </xsl:when>
                <xsl:when test="$ModelOpts = 'clufter:UNKNOWN'">
                    <xsl:message>%(note_unhandled)s</xsl:message>
                </xsl:when>
                <xsl:when test="$ModelOpts = 'clufter:UNSUPPORTED'">
                    <xsl:message>%(qmodel_msg)s</xsl:message>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:message>WARNING: internal error</xsl:message>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:when>
        <xsl:otherwise>
            <xsl:message>%(qdevice_msg)s</xsl:message>
        </xsl:otherwise>
    </xsl:choose>
''') % dict(
    NL=NL,
    note_unhandled='''<xsl:value-of select="concat('WARNING: quorum device model `',
                                                   @model,
                                                   '` is currently unhandled',
                                                   ' in the conversion')"/>''',
    qdevice_msg="WARNING: target corosync+pcs versions do not support qdevice,"
                " hence omitted",
    qmodel_msg='''<xsl:value-of select="concat('WARNING: target corosync+pcs',
                                               ' versions do not support quorum',
                                               ' device model `',
                                               @model,
                                               '`, hence omitted')"/>''',
)
