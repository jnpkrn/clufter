# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....utils_xslt import NL, xslt_is_member


cib2pcscmd_options = (
    'loss-policy',
)

cib2pcscmd = ('''\
    <xsl:choose>
        <!-- plain rsc -->
        <xsl:when test="@rsc">
''' + (
            verbose_inform('"new ticket constraint: ", @id')
) + '''
            <xsl:value-of select="concat($pcscmd_pcs, 'constraint ticket add')"/>
            <xsl:value-of select="concat(' ', @ticket)"/>
            <xsl:if test="@rsc-role">
                <xsl:value-of select="concat(' ', @rsc-role)"/>
            </xsl:if>
            <xsl:value-of select="concat(' ', @rsc)"/>
            <xsl:for-each select="@*[
''' + (
                xslt_is_member('name()', cib2pcscmd_options)
) + ''']">
                <xsl:value-of select="concat(' ', name(), '=', .)"/>
            </xsl:for-each>
            <xsl:value-of select="concat(' ', 'id=', @id)"/>
            <xsl:value-of select="'%(NL)s'"/>
''' + (
            verbose_ec_test
) + '''
        </xsl:when>

        <!-- resource sets -->
        <xsl:when test="resource_set">
            <xsl:message
            >WARNING: ticket constraint with resource sets not supported (yet)</xsl:message>
        </xsl:when>
    </xsl:choose>

''') % dict(
    NL=NL,
)
