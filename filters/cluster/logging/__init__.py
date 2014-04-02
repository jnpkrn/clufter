# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

ccs2needlexml = '''\
    <logging>
        <xsl:copy-of select="@*[
            contains(concat(
                '|debug',
                '|logfile',
                '|logfile_priority',
                '|syslog_facility',
                '|syslog_priority',
                '|to_logfile',
                '|to_syslog',
                '|'), concat('|', name(), '|')
            )
        ]"/>
        <!-- XXX: the latter match (if any) should overwrite the former -->
        <clufter:descent at="logging_daemon"/>
    </logging>
'''
