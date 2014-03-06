# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

ccs2flatironxml = ccs2needlexml = ccs2coroxml = '''\
    <quorum provider="corosync_votequorum">
        <xsl:copy-of select="@*[
            contains(concat(
                '|expected_votes',
                '|two_node',
                '|'), concat('|', name(), '|'))]" />
    </quorum>
'''
