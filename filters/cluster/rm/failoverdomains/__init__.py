# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
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
'''
