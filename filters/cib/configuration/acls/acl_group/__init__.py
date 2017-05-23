# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....utils_xslt import NL

cib2pcscmd = ((
    verbose_inform('"new ACL group: ", @id')
) + '''
    <xsl:value-of select="concat($pcscmd_pcs, 'acl group create', ' ', @id)"/>
    <xsl:for-each select="role">
        <xsl:value-of select="concat(' ', @id)"/>
    </xsl:for-each>
    <xsl:value-of select="'%(NL)s'"/>
''' + (
    verbose_ec_test
)) % dict(
    NL=NL,
)
