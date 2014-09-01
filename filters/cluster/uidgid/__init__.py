# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

ccs2needlexml = '''\
    <xsl:copy>
        <xsl:copy-of select="@*[
            contains(concat(
                '|gid',
                '|uid',
                '|'), concat('|', name(), '|'))]"/>
    </xsl:copy>
'''
