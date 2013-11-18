# -*- coding: UTF-8 -*-
# Copyright 2013 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2 (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

ccs2coroxml = '''\
    <xsl:for-each select="self::node()[@name='corosync' and @subsys]">
        <logger_subsys>
            <xsl:copy-of select="@*[
                contains(concat(
                    '|debug',
                    '|logfile',
                    '|subsys',
                    '|to_logfile',
                    '|to_syslog',
                    '|'), concat('|', name(), '|'))]" />
        </logger_subsys>
    </xsl:for-each>
'''
