# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from ....utils_xslt import xslt_is_member

###

ccs2needlexml_attrs = (
    'ringnumber',
    'bindnetaddr',
    'broadcast',
    'mcastaddr',
    'mcastport',
    'ttl',
)

ccs2needlexml = '''\
    <xsl:copy>
        <xsl:copy-of select="@*[
''' + (
            xslt_is_member('name()', ccs2needlexml_attrs)
) + ''']" />
    </xsl:copy>
'''
