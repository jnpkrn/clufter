# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"


ccs_revitalize = '''\
    <!-- omit failoverdomains with repeated name
         rgmanager/src/daemons/fo_domain.c:fod_get_domain:error #31
     -->
    <xsl:template match="failoverdomain[
                             preceding-sibling::failoverdomain[
                                 @name = current()/@name
                             ]
                         ]">
        <xsl:message>
            <xsl:value-of select="concat('WARNING: omitting failoverdomain',
                                         ' with repeated name (', @name, ')')"/>
        </xsl:message>
    </xsl:template>
    <!-- warn on empty restricted failoverdomains
         rgmanager/src/daemons/groups.c:consider_start:instead of start req.
         http://oss.clusterlabs.org/pipermail/users/2016-January/002176.html
     -->
    <xsl:template match="failoverdomain[
                             @restricted != ''
                             and
                             contains('123456789',
                                       substring(@restricted, 1, 1))
                             and
                             not(failoverdomainnode)
                         ]">
        <xsl:message>
            <xsl:value-of select="concat('WARNING: empty restricted failoverdomain',
                                         ' means associated resource groups',
                                         ' will not start (', @name, ')')"/>
        </xsl:message>
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
'''
