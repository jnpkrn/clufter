# -*- coding: UTF-8 -*-
# Copyright 2018 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

###

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....utils_xslt import NL, xslt_is_member

needleqdevicexml2pcscmd_attrs = (
    # model has a special role here
    'sync_timeout',
    'timeout',
    'votes',  # extra handling (e.g. set to 1 for ffsplit algorithm to work)
)
needleqdevicexml2pcscmd_heuristics_attrs = (
    # exec_NAME needs to be handled separately
    'interval',
    'mode',
    'sync_timeout',
    'timeout',
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
                        xslt_is_member('name()', needleqdevicexml2pcscmd_attrs)
) + ''']">
                        <xsl:choose>
                            <xsl:when test="name() = 'votes'">
                                <xsl:message>
                                    <xsl:value-of select="concat('NOTE: `quorum.device.votes`',
                                                                 ' value `', ., '` specified,',
                                                                 ' but current pcs manages it',
                                                                 ' solely on its own')"/>
                                </xsl:message>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="concat(' ', name(), '=', .)"/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:for-each>

                    <xsl:value-of select="concat(' model ', @model, $ModelOpts)"/>

                    <xsl:choose>
                        <xsl:when test="$pcscmd_extra_qdevice_heuristics
                                        and
                                        heuristics/@*">
                            <xsl:value-of select="' heuristics'"/>
                            <xsl:for-each select="heuristics/@*[
''' + (
                                xslt_is_member('name()', needleqdevicexml2pcscmd_heuristics_attrs)
) + ''']">
                                <xsl:value-of select="concat(' ', name(), '=', .)"/>
                            </xsl:for-each>
                            <xsl:if test="not(heuristics/@*[
                                              starts-with(name(), 'exec_')
                                          ])">
                                <xsl:message>%(qheuristics_disabled_msg)s</xsl:message>
                            </xsl:if>
                            <xsl:for-each select="heuristics/@*[
                                                      starts-with(name(), 'exec_')
                                                  ]">
                                <xsl:value-of select='concat(" &apos;", name(), "=", .,
                                                             "&apos;")'/>
                            </xsl:for-each>
                        </xsl:when>
                        <xsl:when test="$pcscmd_extra_qdevice_heuristics">
                            <!-- no parameters, nothing to do -->
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:message>%(qheuristics_msg)s</xsl:message>
                        </xsl:otherwise>
                    </xsl:choose>

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
    qdevice_msg="WARNING: target corosync/pcs versions do not support qdevice,"
                " hence omitted",
    qheuristics_msg="WARNING: target corosync/pcs versions do not support"
                    " heuristics, hence omitted",
    qheuristics_disabled_msg="WARNING: no heuristic commands specified,"
                             " heuristics will not be enabled by corosync",
    qmodel_msg='''<xsl:value-of select="concat('WARNING: target corosync/pcs',
                                               ' versions do not support quorum',
                                               ' device model `',
                                               @model,
                                               '`, hence omitted')"/>''',
)
