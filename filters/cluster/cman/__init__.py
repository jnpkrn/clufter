# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from ....utils_xslt import xslt_is_member

###

ccs2needlexml_attrs = (
    # 'expected_votes',  # see below
    'two_node',
)

ccs2needlexml = '''\
    <xsl:copy-of select="@*[
''' + (
        xslt_is_member('name()', ccs2needlexml_attrs)
) + ''']"/>
    <xsl:if test="@expected_votes">
        <xsl:message>
            <xsl:value-of select="concat('WARNING: intentionally omitting',
                                         ' expected_votes parameter as it',
                                         ' may be based on assumptions',
                                         ' no longer true in post-conversion',
                                         ' environment')"/>
        </xsl:message>
    </xsl:if>
'''

###

from ....filters.ccs_artefacts import artefact_cond

ccs_artefacts = artefact_cond('@keyfile', kind='F', desc='CMAN keyfile')

###

# NOTE pcs doesn't support udpb directly via --transport (unless forced),
#      one has to specify --broadcast0 parameter instead and transport
#      will get silently switched to udpb

ccspcmk2pcscmd_transports = ('udp', 'udpu')

ccspcmk2pcscmd = '''\
    <xsl:if test="
''' + (
    xslt_is_member('@transport', ccspcmk2pcscmd_transports)
) + '''">
        <xsl:value-of select="concat(' --transport ', @transport)"/>
    </xsl:if>

    <clufter:descent-mix at="multicast"/>
    <clufter:descent-mix at="altmulticast"/>
'''
