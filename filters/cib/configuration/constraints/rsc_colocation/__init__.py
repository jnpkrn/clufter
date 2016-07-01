# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....utils_xslt import NL, translate_lower, xslt_is_member


cib2pcscmd_options = (
    'score',
    # following are highly questionable:
    # https://github.com/ClusterLabs/pacemaker/pull/1091
    #'score-attribute',
    #'score-attribute-mangle',
)

cib2pcscmd_set_options = (
    'role',
    'sequential',
    'score',
    'ordering',  # since constraints-2.1.rng
)

cib2pcscmd = ('''\
    <xsl:choose>
        <!-- plain "A with B" -->
        <xsl:when test="@rsc and @with-rsc">
''' + (
            verbose_inform('"new colocation constraint (resource pair): ", @id')
) + '''
            <xsl:value-of select="concat($pcscmd_pcs, 'constraint colocation add')"/>
            <xsl:if test="
''' + (
            xslt_is_member(translate_lower('@rsc-role'),
                           ('master', 'slave'))
) + '''">
                <xsl:value-of select="concat(' ',
''' + (
                    translate_lower('@rsc-role')
) + ''')"/>
            </xsl:if>
            <xsl:value-of select="concat(' ', @rsc, ' with')"/>
            <xsl:if test="
''' + (
            xslt_is_member(translate_lower('@with-rsc-role'),
                           ('master', 'slave'))
) + '''">
                <xsl:value-of select="concat(' ',
''' + (
                    translate_lower('@with-rsc-role')
) + ''')"/>
            </xsl:if>
            <xsl:value-of select="concat(' ', @with-rsc)"/>
            <xsl:choose>
                <!-- missing score is considered INFINITY by pcs anyway -->
                <xsl:when test="@score and not(
''' + (
                    xslt_is_member('@score', ('INFINITY', '+INFINITY'))
) + ''')">
                    <xsl:value-of select="concat(' ', @score)"/>
                </xsl:when>
                <xsl:when test="@score"/>
                <xsl:otherwise>
                    <!-- missing score would be considered INFINITY by pcs -->
                    <xsl:value-of select="' 0'"/>
                </xsl:otherwise>
            </xsl:choose>
            <xsl:value-of select="concat(' ', 'id=', @id)"/>
            <xsl:value-of select="'%(NL)s'"/>
''' + (
            verbose_ec_test
) + '''
        </xsl:when>

        <!-- resource sets -->
        <xsl:when test="resource_set">
''' + (
            verbose_inform('"new colocation constraint (resource set): ", @id')
) + '''
            <xsl:value-of select="concat($pcscmd_pcs, 'constraint colocation')"/>

            <xsl:for-each select="resource_set">
                <xsl:value-of select="' set'"/>
                <xsl:for-each select="resource_ref">
                    <xsl:value-of select="concat(' ', @id)"/>
                </xsl:for-each>

                <xsl:for-each select="@*[
''' + (
                    xslt_is_member('name()', cib2pcscmd_set_options)
) + ''']">
                    <xsl:value-of select="concat(' ', name(), '=', .)"/>
                </xsl:for-each>

            </xsl:for-each>

            <xsl:value-of select="' setoptions'"/>
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
    </xsl:choose>

''') % dict(
    NL=NL,
)
