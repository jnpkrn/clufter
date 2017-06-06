# -*- coding: UTF-8 -*-
# Copyright 2017 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

from ....utils_xslt import xslt_is_member

cib2pcscmd_contopts_whitelist = (
    'image',
    'replicas',
    'replicas_per_host',
    'masters',
    'run-command',
    'network',
    'options',
)

cib2pcscmd = ('''\
    <xsl:when test="name() = 'docker'">
        <xsl:value-of select="name()"/>

        <xsl:for-each select="@*">
            <xsl:choose>
                <xsl:when test="
''' + (
                xslt_is_member('name()', cib2pcscmd_contopts_whitelist)
) + '''">
                    <xsl:value-of select='concat(" &apos;", name(), "=", ., "&apos;")'/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:message>
                        <xsl:value-of select="concat('WARNING: dropping non-whitelisted',
                                                     ' bundle/docker property: `',
                                                     name(), '`')"/>
                    </xsl:message>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:for-each>
    </xsl:when>
''')
