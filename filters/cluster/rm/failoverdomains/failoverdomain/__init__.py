# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

from .... import package_name

ccsflat2cibprelude = ('''\
    <template id="FAILOVERDOMAIN-{@name}"
              class="ocf"
              provider="%(package_name)s"
              type="temporary-failoverdomain">
        <meta_attributes id="FAILOVERDOMAIN-{@name}-META">
            <nvpair id="FAILOVERDOMAIN-{@name}-META-ordered"
                    name="ordered"
                    value="0">
                <xsl:if test="@ordered != ''
                              and
                              contains('123456789',
                                        substring(@ordered, 1, 1))">
                    <xsl:attribute name="value">
                        <xsl:value-of select="'1'"/>
                    </xsl:attribute>
                </xsl:if>
            </nvpair>
            <nvpair id="FAILOVERDOMAIN-{@name}-META-restricted"
                    name="restricted"
                    value="0">
                <xsl:if test="@restricted != ''
                              and
                              contains('123456789',
                                        substring(@restricted, 1, 1))">
                    <xsl:attribute name="value">
                        <xsl:value-of select="'1'"/>
                    </xsl:attribute>
                </xsl:if>
            </nvpair>
            <nvpair id="FAILOVERDOMAIN-{@name}-META-nofailback"
                    name="nofailback"
                    value="0">
                <xsl:if test="@nofailback != ''
                              and contains('123456789',
                                           substring(@nofailback, 1, 1))">
                    <xsl:attribute name="value">
                        <xsl:value-of select="'1'"/>
                    </xsl:attribute>
                </xsl:if>
            </nvpair>
            <xsl:for-each select="failoverdomainnode">
                <nvpair id="FAILOVERDOMAIN-{../@name}-META-failoverdomainnode-{@name}"
                        name="failoverdomainnode-{@priority}"
                        value="{@name}"/>
            </xsl:for-each>
        </meta_attributes>
    </template>
''') % dict(package_name=package_name())

###

ccs_revitalize = '''\
    <!-- omit failoverdomainnodes with repeated name
         rgmanager/src/daemons/fo_domain.c:fod_get_node:error #30
     -->
    <xsl:template match="failoverdomainnode[
                             preceding-sibling::failoverdomainnode[
                                 @name = current()/@name
                             ]
                         ]">
        <xsl:message>
            <xsl:value-of select="concat('WARNING: omitting failoverdomainnode',
                                         ' with repeated name (', @name, ')')"/>
        </xsl:message>
    </xsl:template>
'''
