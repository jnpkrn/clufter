# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

ccs2coroxml = '''\
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
            '|'), concat('|', name(), '|'))]" />
    <clufter:descent at="interface"/>
'''
