# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from ....utils_xslt import xslt_is_member

###

ccs2needlexml_attrs = (
    'debug',
    'logfile',
    'logfile_priority',
    'syslog_facility',
    'syslog_priority',
    'to_logfile',
    'to_syslog',
)

ccs2needlexml = '''\
    <logging>
        <xsl:copy-of select="@*[
''' + (
            xslt_is_member('name()', ccs2needlexml_attrs)
) + ''']"/>
        <!-- XXX: the latter match (if any) should overwrite the former -->
        <clufter:descent at="logging_daemon"/>
    </logging>
'''

###

from ....filters.ccs_artefacts import artefact_cond

ccs_artefacts = artefact_cond('@logfile', kind='F', desc='base logfile')
