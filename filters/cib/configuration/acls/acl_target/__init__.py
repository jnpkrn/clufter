# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....utils_xslt import NL

cib2pcscmd = ('''\
    <!-- "pcs acl" only supported with certain newer versions of
         pcs/pacemaker (https://bugzilla.redhat.com/1111369) -->
    <xsl:choose>
        <xsl:when test="$pcscmd_extra_acls">
''' + (
    verbose_inform('"new ACL user: ", @id')
) + '''
    <xsl:value-of select="concat($pcscmd_pcs, 'acl user create', ' ', @id)"/>
    <xsl:for-each select="role">
        <xsl:value-of select="concat(' ', @id)"/>
    </xsl:for-each>
    <xsl:value-of select="'%(NL)s'"/>
''' + (
    verbose_ec_test
) + '''
        </xsl:when>
        <xsl:when test="not(preceding-sibling::acl_group)">
            <xsl:message>%(acls_msg)s</xsl:message>
        </xsl:when>
    </xsl:choose>
''') % dict(
    NL=NL,
    acls_msg="WARNING: target pcs/pacemaker version does not support"
             " (new) ACLs, hence &apos;acl_group&apos; element(s) omitted",
)
