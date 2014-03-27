# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

ccs2flatironxml = ccs2needlexml = '''\
    <xsl:copy-of select="@*[
        contains(concat(
            '|consensus',
            '|fail_recv_const',
            '|join',
            '|max_messages',
            '|miss_count_const',
            '|netmtu',
            '|rrp_mode',
            '|rrp_problem_count_threshold',
            '|secauth',
            '|seqno_unchanged_const',
            '|token',
            '|token_retransmits_before_loss_const',
            '|window_size',
            '|'), concat('|', name(), '|'))]"/>
    <!-- XXX bz1078343 -->
    <!-- xsl:if test="not(@token)">
        <xsl:attribute name="token">10000</xsl:attribute>
    </xsl:if -->
    <clufter:descent at="interface"/>
'''
