# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from ....utils_xslt import xslt_is_member

###

ccs2needlexml_attrs = (
    'expected_votes',
    'two_node',
)

ccs2needlexml = '''\
    <xsl:copy-of select="@*[
''' + (
        xslt_is_member('name()', ccs2needlexml_attrs)
) + ''']"/>
'''

###

from ....filters.ccs_artefacts import artefact_cond

ccs_artefacts = artefact_cond('@keyfile', kind='F', desc='CMAN keyfile')
