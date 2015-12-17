# -*- coding: UTF-8 -*-
# Copyright 2015 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

from ....filters._2pcscmd import verbose_ec_test, verbose_inform
from ....filters.cib2pcscmd import attrset_xsl
from ....utils_xslt import NL

cib2pcscmd = ('''\
    <xsl:if test="instance_attributes/nvpair">
''' + (
        verbose_inform('"set properties for ", @uname, " node"')
) + '''
        <xsl:value-of select='concat($pcscmd_pcs, "property set")'/>
        <xsl:value-of select="concat(' --node ', @uname)"/>
''' + (
        attrset_xsl("instance_attributes")
) + '''
        <xsl:value-of select="'%(NL)s'"/>
''' + (
        verbose_ec_test
) + '''
    </xsl:if>

    <!-- XXX "pcs resource utilization" not supported with majority
             of pcs versions -->
    <xsl:if test="utilization/nvpair">
''' + (
        verbose_inform('"set utilization for resource: ", @uname, " node"')
) + '''
        <xsl:value-of select="concat($pcscmd_pcs, 'node utilization -h',
                                     ' &gt;/dev/null',
                                     ' &amp;&amp; ',
                                     $pcscmd_pcs, 'node utilization',
                                     ' ', @uname)"/>
''' + (
            attrset_xsl("utilization")
) + '''
        <xsl:value-of select="'%(NL)s'"/>
''' + (
        verbose_ec_test
) + '''
    </xsl:if>
''') % dict(
    NL=NL,
)
