# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....filters.cib2pcscmd import attrset_xsl
from ....utils_xslt import NL, xslt_is_member

cib2pcscmd = ('''\
    <xsl:for-each select="*[
''' + (
                          xslt_is_member('name()', ('primitive', 'group'))
) + ''']">
''' + (
        verbose_inform('"make ", name(), " a clone: ", @id')
) + '''
        <xsl:value-of select="concat($pcscmd_pcs, 'resource ', name(..))"/>
        <!-- pcs only allows to identify master, not a clone -->
        <xsl:if test="name(..) = 'master'">
            <xsl:value-of select="concat(' ', ../@id)"/>
        </xsl:if>
        <xsl:value-of select="concat(' ', @id)"/>
''' + (
            attrset_xsl("../meta_attributes")
) + '''
        <xsl:value-of select="'%(NL)s'"/>
''' + (
        verbose_ec_test
) + '''
    </xsl:for-each>
''') % dict(
    NL=NL,
)
