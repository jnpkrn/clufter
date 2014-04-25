# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

ccs2needlexml = '''\
    <xsl:if test="@name='corosync' and @subsys">
        <logger_subsys>
            <xsl:copy-of select="@*[
                contains(concat(
                    '|debug',
                    '|logfile',
                    '|logfile_priority',
                    '|subsys',
                    '|syslog_facility',
                    '|syslog_priority',
                    '|to_logfile',
                    '|to_syslog',
                    '|'), concat('|', name(), '|')
                )
            ]"/>
        </logger_subsys>
    </xsl:if>
'''
