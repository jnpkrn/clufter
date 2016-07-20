# -*- coding: UTF-8 -*-
# Copyright 2016 Red Hat, Inc.
# Part of clufter project
# Licensed under GPLv2+ (a copy included | http://gnu.org/licenses/gpl-2.0.txt)
__author__ = "Jan Pokorný <jpokorny @at@ Red Hat .dot. com>"

###

from ....filters.cib2pcscmd import attrset_xsl

cib2pcscmd = ((
    attrset_xsl("instance_attributes",
                cmd='$pcscmd_pcs, "property set"',
                inform='"set properties for ", @uname, " node"')

) + '''
    <!-- "pcs node utilization" only supported with certain newer
         versions of pcs -->
    <xsl:choose>
        <xsl:when test="$pcscmd_extra_utilization">
''' + (
        attrset_xsl("utilization",
                    cmd='$pcscmd_pcs, "node utilization ", @uname',
                    inform='"set utilization for node: ", @uname')
) + '''
        </xsl:when>
        <xsl:when test="utilization/nvpair">
            <xsl:message>%(utilization_msg)s</xsl:message>
        </xsl:when>
    </xsl:choose>
''') % dict(
    utilization_msg="WARNING: target pcs version does not support utilization"
                    " attributes, hence omitted",
)
