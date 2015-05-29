# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....utils_xslt import NL, xslt_is_member

cib2pcscmd = ('''\
    <xsl:choose>
        <!-- plain "with" -->
        <xsl:when test="@rsc and @with-rsc">
''' + (
            verbose_inform('"new colocation constraint: ", @id')
) + '''
            <xsl:value-of select="'pcs constraint colocation add'"/>
            <xsl:if test="
''' + (
            xslt_is_member('@rsc-role', ('master', 'slave'))
) + '''">
                <xsl:value-of select="concat(' ', @rsc-role)"/>
            </xsl:if>
            <xsl:value-of select="concat(' ', @rsc, ' with')"/>
            <xsl:if test="
''' + (
            xslt_is_member('@with-rsc-role', ('master', 'slave'))
) + '''">
                <xsl:value-of select="concat(' ', @with-rsc-role)"/>
            </xsl:if>
            <xsl:value-of select="concat(' ', @with-rsc)"/>
            <xsl:if test="@score and not(
''' + (
            xslt_is_member('@score', ('INFINITY', '+INFINITY'))
) + ''')">
                <xsl:value-of select="concat(' ', @score)"/>
            </xsl:if>
            <xsl:value-of select="concat(' ', 'id=', @id)"/>
            <xsl:choose>
                <xsl:when test="@score"/>
                <xsl:when test="@score-attribute">
                    <xsl:value-of select="concat(' ', 'score-attribute=',
                                                 @score-attribute)"/>
                </xsl:when>
                <xsl:when test="@score-attribute-mangle">
                    <xsl:value-of select="concat(' ', 'score-attribute-mangle=',
                                                 @score-attribute-mangle)"/>
                </xsl:when>
            </xsl:choose>
            <xsl:value-of select="'%(NL)s'"/>
''' + (
            verbose_ec_test
) + '''
        </xsl:when>

        <!-- resource sets -->
        <xsl:when test="rsc_colocation[resource_set]">
            <xsl:message
            >WARNING: colocation constraint with resource sets not supported (yet)</xsl:message>
        </xsl:when>
    </xsl:choose>

''') % dict(
    NL=NL,
)
