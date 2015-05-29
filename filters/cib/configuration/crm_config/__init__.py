# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....utils_xslt import NL

cib2pcscmd = ('''\
    <xsl:for-each select="cluster_property_set">
        <xsl:for-each select="nvpair">
            <!-- unfortunately pcs will throw away the rest of name-value
                 pairs when first unknown observed; alternatively a single
                 command with "force" -->
''' + (
            verbose_inform('"new singleton property set: ", @name')
) + '''
            <xsl:value-of select='concat($pcscmd_pcs, "property set")'/>
            <xsl:if test="$pcscmd_force">
                <xsl:value-of select="' --force'"/>
            </xsl:if>
            <xsl:value-of select='concat(" &apos;", @name, "=", @value, "&apos;")'/>
            <xsl:value-of select="'%(NL)s'"/>
''' + (
            verbose_ec_test
) + '''
        </xsl:for-each>
    </xsl:for-each>
''') % dict(
    NL=NL,
)
