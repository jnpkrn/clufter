# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_xslt import NL

cib2pcscmd = ('''\
    <xsl:value-of select="concat('pcs group add ', @id)"/>
    <xsl:for-each select="primitive">
        <xsl:value-of select="concat(' ', @id)"/>
    </xsl:for-each>
    <xsl:value-of select="'%(NL)s'"/>
''') % dict(
    NL=NL
)
