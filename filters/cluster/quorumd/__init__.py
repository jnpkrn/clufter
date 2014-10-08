# -*- coding: UTF-8 -*-
# Copyright 2014 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)

from ....utils_xslt import xslt_is_member

###

ccs_obfuscate_identifiers = '''\
    <xsl:copy>
        <!-- awkward way to keep both relative attribute ordering
             and ordering QUORUMD-LABEL-{1, 2}; not scaling well -->
        <xsl:variable name="QuorumdLabel"
                      select="@*[
''' + ( \
            xslt_is_member('name()', ('cman_label',
                                      'label'))
) + ''']"/>
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

###

from ....filters.ccs_artefacts import artefact_cond

ccs_artefacts = artefact_cond('@statusfile', kind='F',
                              desc='quorumd status file')
