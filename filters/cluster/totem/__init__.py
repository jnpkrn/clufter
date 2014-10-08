# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from ....utils_xslt import xslt_is_member


ccs2needlexml_attrs = (
    'consensus',
    'fail_recv_const',
    'join',
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
''' + ( \
        xslt_is_member('name()', ccs2needlexml_attrs)
) + ''']"/>
    <!-- XXX bz1078343 -->
    <!-- xsl:if test="not(@token)">
        <xsl:attribute name="token">10000</xsl:attribute>
    </xsl:if -->
    <clufter:descent at="interface"/>
'''
