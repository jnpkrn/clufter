# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

###

from ....utils_xslt import xslt_is_member

# 1:1 mapping of supported params to pcs arguments
needlexml2pcscmd_supported = (
    # binary 0|1 values
    'auto_tie_breaker',
    'last_man_standing',
    'wait_for_all',
    # standard values
    'last_man_standing_window',
)

needlexml2pcscmd = '''\
    <xsl:for-each select="@*[
''' + (
        xslt_is_member('name()', needlexml2pcscmd_supported)
) + ''']">
        <xsl:if test=".">
            <!-- but see https://bugzilla.redhat.com/1235452 -->
            <xsl:value-of select="concat(' --', name(), '=', .)"/>
        </xsl:if>
    </xsl:for-each>
'''
