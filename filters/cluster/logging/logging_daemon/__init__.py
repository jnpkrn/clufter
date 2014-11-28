# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from ....utils_xslt import xslt_is_member

###

# XXX: logging/__init__.py: ccs2needlexml_attrs + ('subsys', )
ccs2needlexml_attrs = (
    'debug',
    'logfile',
    'logfile_priority',
    'subsys',
    'syslog_facility',
    'syslog_priority',
    'to_logfile',
    'to_syslog',
)

ccs2needlexml = '''\
    <xsl:if test="@name='corosync' and @subsys">
        <logger_subsys>
            <xsl:copy-of select="@*[
''' + (
                xslt_is_member('name()', ccs2needlexml_attrs)
) + ''']"/>
        </logger_subsys>
    </xsl:if>
'''

###

from ....filters.ccs_artefacts import artefact_cond

ccs_artefacts = artefact_cond('@logfile', kind='F',
                              desc="log file for ', normalize-space(@name), '")
