# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from ....utils_xslt import xslt_is_member

###

ccs2needlexml_attrs = (
    'consensus',
    'fail_recv_const',
    'join',
    'keyfile',
    'max_messages',
    'miss_count_const',
    'netmtu',
    'rrp_mode',
    'rrp_problem_count_threshold',
    'secauth',
    'seqno_unchanged_const',
    'token',
    'token_retransmits_before_loss_const',
    'window_size',
)

ccs2needlexml = '''\
    <xsl:copy-of select="@*[
''' + (
        xslt_is_member('name()', ccs2needlexml_attrs)
) + ''']"/>
    <clufter:descent at="interface"/>
'''

###

from ....filters.ccs_artefacts import artefact_cond

ccs_artefacts = artefact_cond('@keyfile', kind='F', desc='totem keyfile')

###

# 1:1 mapping of supported params to pcs arguments (not: rrpmode)
ccspcmk2pcscmd_supported = (
    'consensus',
    'join',
    'token',
    'fail_recv_const',
    'miss_count_const',
)

ccspcmk2pcscmd = '''\
    <xsl:for-each select="@*[
''' + (
        xslt_is_member('name()', ccspcmk2pcscmd_supported)
) + ''']">
        <xsl:if test=".">
            <xsl:value-of select="concat(' --', name(), ' ', .)"/>
        </xsl:if>
    </xsl:for-each>
    <xsl:if test="@rrp_mode">
        <xsl:value-of select="concat(' --rrpmode ', @rrp_mode)"/>
    </xsl:if>

    <clufter:descent-mix at="interface"/>

    <!-- corosync encryption _disabling_ (not possible) -->
    <xsl:if test="@secauth = 'off'">
        <xsl:message>
            <xsl:value-of select="concat('WARNING: no encryption requested,',
                                         ' but current pcs not capable to',
                                         ' disable it for CMAN')"/>
        </xsl:message>
    </xsl:if>
'''
