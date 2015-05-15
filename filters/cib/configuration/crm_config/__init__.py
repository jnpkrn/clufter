# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

from ....utils_xslt import NL

cib2pcscmd = ('''\
    <xsl:for-each select="cluster_property_set">
        <xsl:for-each select="nvpair">
            <!-- unfortunately pcs will throw away the rest of name-value
                 pairs when first unknown observed; alternatively a single
                 command with "force" -->
            <xsl:value-of select="'pcs property set'"/>
            <xsl:value-of select='" &apos;"'/>
            <xsl:value-of select="concat(@name, '=', @value)"/>
            <xsl:value-of select='"&apos;"'/>
            <xsl:value-of select="'%(NL)s'"/>
        </xsl:for-each>
    </xsl:for-each>
''') % dict(
    NL=NL
)
