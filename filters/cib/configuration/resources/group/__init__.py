# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....filters.cib2pcscmd import attrset_xsl
from ....utils_xslt import NL

cib2pcscmd = ('''\
''' + (
    verbose_inform('"new group: ", @id')
) + '''
    <xsl:value-of select="concat($pcscmd_pcs, 'resource group add ', @id)"/>
    <xsl:for-each select="primitive">
        <xsl:value-of select="concat(' ', @id)"/>
    </xsl:for-each>
    <xsl:value-of select="'%(NL)s'"/>
''' + (
    verbose_ec_test
) + '''

    <!-- meta attrs -->
    <xsl:if test="meta_attributes/nvpair">
''' + (
        verbose_inform('"meta attributes for group: ", @id')
) + '''
        <xsl:value-of select="concat($pcscmd_pcs, 'resource meta ', @id)"/>
''' + (
            attrset_xsl("meta_attributes")
) + '''
        <xsl:value-of select="'%(NL)s'"/>
''' + (
        verbose_ec_test
) + '''
    </xsl:if>
''') % dict(
    NL=NL,
)
