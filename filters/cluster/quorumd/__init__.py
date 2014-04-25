# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

ccs_obfuscate_identifiers = '''\
    <xsl:copy>
        <!-- awkward way to keep both relative attribute ordering
             and ordering QUORUMD-LABEL-{1, 2}; not scaling well -->
        <xsl:variable name="QuorumdLabel"
                      select="@*[
                          contains(concat(
                              '|cman_label',
                              '|label',
                              '|'), concat('|', name(), '|')
                          )
                      ]"/>
        <xsl:for-each select="@*">
            <xsl:variable name="QuorumdLabelMatch"
                          select="$QuorumdLabel[
                                      name()
                                      =
                                      name(current())
                                  ][1]"/>
            <xsl:choose>
                <xsl:when test="$QuorumdLabelMatch">
                    <xsl:variable name="QuorumdLabelsCurrent"
                                  select="name()"/>
                    <xsl:attribute name="{name()}">
                        <xsl:value-of select="concat(
                            'QUORUMD-LABEL-',
                             count($QuorumdLabelMatch/preceding-sibling::*) + 1
                        )"/>
                    </xsl:attribute>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:copy/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:for-each>
        <xsl:apply-templates/>
    </xsl:copy>
'''
