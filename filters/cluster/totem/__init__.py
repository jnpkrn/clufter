# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from ....utils_xslt import xslt_is_member

###

from hashlib import sha256
from os import getpid
from time import time

ccs2needlexml_attrs = (
    'consensus',
    'fail_recv_const',
    'join',
    'keyfile',
    'max_messages',
    'miss_count_const',
    'netmtu',
    'rrp_mode',
    'rrp_problem_count_threshold',
    'secauth',
    'seqno_unchanged_const',
    'token',
    'token_retransmits_before_loss_const',
    'window_size',
)

ccs2needlexml = ('''\
    <xsl:copy-of select="@*[
''' + (
        xslt_is_member('name()', ccs2needlexml_attrs)
) + ''']"/>
    <!-- see bz1165821 (pcs currently doesn't handle corosync's keyfile) -->
    <xsl:if test="(not(@secauth) or @secauth != 'off') and not(@keyfile)">
        <xsl:message>%(key_message)s</xsl:message>
        <xsl:attribute name="key">
            <xsl:value-of select="%(key)s"/>
        </xsl:attribute>
    </xsl:if>
    <!-- XXX bz1078343 -->
    <!-- xsl:if test="not(@token)">
        <xsl:attribute name="token">10000</xsl:attribute>
    </xsl:if -->
    <clufter:descent at="interface"/>
''') % dict(key='_NOT_SECRET_' + sha256(
                    str(getpid()) + '_REALLY_' + str(int(time()))
                ).hexdigest(),
            key_message='secret key used by corosync for encryption/integrity'
                        ' checking is, as a measure to prevent from dropping'
                        ' these security features entirely, stored directly'
                        ' in the main configuration file, possibly readable'
                        ' by arbitrary system-local user',
       )

###

from ....filters.ccs_artefacts import artefact_cond

ccs_artefacts = artefact_cond('@keyfile', kind='F', desc='totem keyfile')
